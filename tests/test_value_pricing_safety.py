import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import requests

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "value-pricing" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from common import eval_expr  # noqa: E402
from crawl_site import Fetcher  # noqa: E402


class SafeExpressionTests(unittest.TestCase):
    def test_template_numpy_and_rng_expression(self):
        n = 64
        rng = np.random.default_rng(1)
        values = eval_expr(
            "np.clip(rng.lognormal(np.log(0.12), 0.5, n), 0.02, 0.4)",
            {"np": np, "rng": rng, "n": n},
        )
        self.assertEqual(values.shape, (n,))
        self.assertTrue(np.all((values >= 0.02) & (values <= 0.4)))

    def test_arbitrary_python_is_rejected(self):
        with self.assertRaises((ValueError, SyntaxError)):
            eval_expr("__import__('os').system('echo unsafe')", {})

    def test_expression_cannot_mutate_inputs_with_numpy_out(self):
        source = np.array([1.0, 2.0])
        with self.assertRaises(ValueError):
            eval_expr("np.clip(x, 0, 1, out=x)", {"x": source})
        np.testing.assert_array_equal(source, [1.0, 2.0])


class SelfTestDestinationTests(unittest.TestCase):
    def test_existing_directory_is_refused_without_modification(self):
        script = SCRIPTS / "selftest.py"
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "existing"
            destination.mkdir()
            sentinel = destination / "sentinel.txt"
            sentinel.write_text("keep")
            result = subprocess.run(
                [sys.executable, str(script), "--dir", str(destination), "--no-hb"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("already exists", result.stderr)
            self.assertEqual(sentinel.read_text(), "keep")


class CrawlerBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.fetcher = Fetcher(delay=0, browser=False, contact="test@example.com")
        self.fetcher.origin = ("https", "example.com", 443)

    def tearDown(self):
        self.fetcher.close()

    @patch("crawl_site.socket.getaddrinfo")
    def test_private_dns_destination_is_blocked(self, getaddrinfo):
        getaddrinfo.return_value = [(None, None, None, None, ("127.0.0.1", 0))]
        self.assertFalse(self.fetcher.safe_url("https://example.com/private"))

    @patch("crawl_site.socket.getaddrinfo")
    def test_cross_origin_redirect_is_not_followed(self, getaddrinfo):
        getaddrinfo.return_value = [(None, None, None, None, ("93.184.216.34", 0))]
        response = requests.Response()
        response.status_code = 302
        response.headers["Location"] = "http://127.0.0.1/admin"
        with patch.object(self.fetcher.s, "get", return_value=response) as get:
            code, message = self.fetcher.get("https://example.com/start")
        self.assertEqual(code, 0)
        self.assertIn("blocked", message)
        get.assert_called_once()

    @patch("crawl_site.socket.getaddrinfo")
    def test_nonstandard_port_is_blocked(self, getaddrinfo):
        self.assertFalse(self.fetcher.safe_url("https://example.com:8443/"))
        getaddrinfo.assert_not_called()


if __name__ == "__main__":
    unittest.main()

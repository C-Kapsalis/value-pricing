#!/usr/bin/env python3
"""Polite crawler: a product's own site (phase 1) or competitors' pricing pages (phase 2) → markdown.

Conduct: robots.txt honoured, an identifying user agent with a contact, >= --delay seconds between
requests to a host, retry with backoff on 429/5xx, resumable (a state file records every URL tried and
the links it found, so a rerun continues where the last stopped). Pages are saved as
<out>/<host>/<slug>.md with front matter (url, title, status, fetched). Keep the output out of git.

  crawl_site.py --study S --url https://example.com [--max-pages 150] [--browser] --contact you@company.com
  crawl_site.py --study S --vendors market/data/vendors.csv --pricing-only

--browser renders with Playwright (pip install playwright && playwright install chromium) for sites
that build their content in JavaScript; otherwise plain HTTP.
"""
from __future__ import annotations

import csv
import json
import re
import time
import urllib.robotparser as robotparser
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from common import Study, study_arg

UA = "value-pricing-research/0.1 (pricing study; contact: {contact})"
PRIORITY = re.compile(r"pric|plan|feature|product|integrat|connector|solution|use-case|customer|case-stud|compare|vs-|alternative|docs|changelog|about|security|enterprise", re.I)
PRICING = re.compile(r"pric|plans?\b|billing|subscribe|buy", re.I)
SKIP = re.compile(r"\.(png|jpe?g|gif|svg|webp|ico|pdf|zip|mp4|mov|css|js|xml|json|woff2?)(\?|$)|/(login|signin|signup|register|cart|checkout|account|wp-admin)\b|mailto:|tel:", re.I)


class Fetcher:
    def __init__(self, delay: float, browser: bool, contact: str):
        self.delay, self.last, self.robots = delay, {}, {}
        self.s = requests.Session()
        self.s.headers["User-Agent"] = UA.format(contact=contact)
        self.browser = None
        if browser:
            from playwright.sync_api import sync_playwright
            self._pw = sync_playwright().start()
            self.browser = self._pw.chromium.launch()

    def allowed(self, url: str) -> bool:
        p = urlparse(url)
        host = f"{p.scheme}://{p.netloc}"
        if host not in self.robots:
            rp = robotparser.RobotFileParser()
            try:
                r = self.s.get(host + "/robots.txt", timeout=15)
                rp.parse(r.text.splitlines() if r.status_code == 200 else [])
            except Exception:
                rp.parse([])
            self.robots[host] = rp
        return self.robots[host].can_fetch(self.s.headers["User-Agent"], url)

    def get(self, url: str) -> tuple[int, str]:
        host = urlparse(url).netloc
        code, html = 0, ""
        for attempt in range(4):
            wait = self.delay - (time.time() - self.last.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            self.last[host] = time.time()
            try:
                if self.browser:
                    pg = self.browser.new_page(user_agent=self.s.headers["User-Agent"])
                    resp = pg.goto(url, wait_until="networkidle", timeout=45000)
                    html, code = pg.content(), (resp.status if resp else 0)
                    pg.close()
                else:
                    r = self.s.get(url, timeout=30)
                    html, code = r.text, r.status_code
                if code in (429, 500, 502, 503, 504):
                    time.sleep(self.delay * 2 ** (attempt + 1))
                    continue
                return code, html
            except Exception as e:
                code, html = 0, str(e)
                time.sleep(self.delay * 2 ** (attempt + 1))
        return code, html

    def close(self):
        if self.browser:
            self.browser.close()
            self._pw.stop()


def to_markdown(html: str, url: str) -> tuple[str, str, list[str]]:
    soup = BeautifulSoup(html, "lxml")
    links = [urldefrag(urljoin(url, a["href"]))[0] for a in soup.find_all("a", href=True)]
    for t in soup(["script", "style", "noscript", "svg", "iframe", "form"]):
        t.decompose()
    title = (soup.title.get_text(strip=True) if soup.title else "") or url
    body = soup.find("main") or soup.body or soup
    lines, seen = [], set()
    for el in body.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th", "span", "div"]):
        if el.name in ("span", "div") and el.find(["p", "li", "h1", "h2", "h3", "h4", "div", "td"]):
            continue
        txt = " ".join(el.get_text(" ", strip=True).split())
        if len(txt) < 2:
            continue
        line = ("\n" + "#" * int(el.name[1]) + " " + txt) if el.name in ("h1", "h2", "h3", "h4") else ("- " + txt if el.name == "li" else txt)
        if line not in seen:
            seen.add(line)
            lines.append(line)
    return title, "\n".join(lines), links


def slug(url: str) -> str:
    p = urlparse(url)
    s = re.sub(r"[^a-z0-9]+", "-", (p.path + ("-" + p.query if p.query else "")).lower()).strip("-")
    return s[:120] or "index"


def save(out: Path, url: str, code: int, title: str, md: str):
    d = out / urlparse(url).netloc
    d.mkdir(parents=True, exist_ok=True)
    fm = {"url": url, "title": title, "status": code, "fetched": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (d / f"{slug(url)}.md").write_text("---\n" + "\n".join(f"{k}: {json.dumps(v)}" for k, v in fm.items()) + "\n---\n\n" + md)


def crawl(f: Fetcher, start: str, out: Path, max_pages: int, state: Path, pricing_only: bool) -> int:
    done = {}
    if state.exists():
        for l in state.read_text().splitlines():
            r = json.loads(l)
            done[r["url"]] = r.get("links")
    host = urlparse(start).netloc
    q, seen, n = deque([start]), {start}, 0
    if pricing_only:
        for guess in ("/pricing", "/plans"):
            u = urljoin(start, guess)
            if u not in seen:
                q.append(u)
                seen.add(u)

    def enqueue(links):
        for l in links:
            if l not in seen:
                seen.add(l)
                (q.appendleft if PRIORITY.search(urlparse(l).path) else q.append)(l)

    while q and n < max_pages:
        url = q.popleft()
        if url in done:                     # resumed: re-queue what this page linked to, skip the fetch
            if done[url] is not None:
                n += 1
                enqueue(done[url])
            continue
        rec = {"url": url}
        if not f.allowed(url):
            rec["status"] = "robots_disallowed"
        else:
            code, html = f.get(url)
            rec["status"] = code
            if code == 200 and "<" in html:
                title, md, links = to_markdown(html, url)
                save(out, url, code, title, md)
                n += 1
                nxt = [l for l in links if urlparse(l).netloc == host and not SKIP.search(l)]
                if pricing_only:
                    nxt = [l for l in nxt if PRICING.search(urlparse(l).path)]
                nxt = sorted(set(nxt), key=lambda l: (not PRIORITY.search(urlparse(l).path), len(l)))
                rec["links"] = nxt
                enqueue(nxt)
        with state.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
    return n


def main():
    ap = study_arg(__doc__.splitlines()[0])
    ap.add_argument("--url")
    ap.add_argument("--vendors", help="CSV with vendor,url columns (phase 2)")
    ap.add_argument("--pricing-only", action="store_true")
    ap.add_argument("--max-pages", type=int, default=150)
    ap.add_argument("--delay", type=float, default=1.2)
    ap.add_argument("--browser", action="store_true")
    ap.add_argument("--contact", default="unset; pass --contact")
    ap.add_argument("--out")
    a = ap.parse_args()
    st = Study(a.study)
    f = Fetcher(a.delay, a.browser, a.contact)
    try:
        if a.url:
            out = Path(a.out) if a.out else st.root / "corpus" / "site"
            n = crawl(f, a.url, out, a.max_pages, st.path("corpus", "site_state.jsonl"), a.pricing_only)
            print(f"{n} pages → {out}")
        if a.vendors:
            out = Path(a.out) if a.out else st.root / "corpus" / "vendors"
            vp = Path(a.vendors) if Path(a.vendors).is_absolute() else st.root / a.vendors
            rows = [r for r in csv.DictReader(open(vp)) if r.get("vendor") != "__ours__"]
            for i, r in enumerate(rows, 1):
                url = r.get("url") or f"https://{r['vendor']}"
                n = crawl(f, url, out, 6 if a.pricing_only else a.max_pages, st.path("corpus", "vendors_state.jsonl"), a.pricing_only)
                print(f"[{i}/{len(rows)}] {r.get('vendor', url)}: {n} pages", flush=True)
    finally:
        f.close()


if __name__ == "__main__":
    main()

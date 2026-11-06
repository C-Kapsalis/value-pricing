# ClawHub findings and regression review

Verified against the revised 0.1.3 skill. This is a code and behavior review, not a fresh SkillSpecter verdict. The screenshot category labels alone do not establish an exploit, particularly where no source excerpt was supplied.

| Screenshot(s) / finding | Resolution and evidence |
| --- | --- |
| 1–2: capabilities / missing permissions | SKILL.md declares Python and optional credentials using ClawHub runtime metadata and describes local inputs, explicit source/output paths, Git provenance, crawler requests, and both model runners. These declarations describe behavior; they do not provide an OS sandbox. Metadata regression test passes. No MCP server or tool is shipped. |
| 1: external transmission, environment access, enumeration | Crawling and model-assisted research remain intentional capabilities. Model batches require explicit transfer confirmation, validated IDs and confined input/output paths. CLI environment forwarding uses a fixed allowlist; unrelated secrets are excluded. Corpus ingestion reads explicit paths and skips symlinked files. Local path and mocked CLI/API tests pass. |
| 1: tool poisoning / hidden instructions | Research prompts treat source material as untrusted. API calls expose no tools; CLI invocation disables tools, MCP, settings and session persistence. No specific poisoned MCP description was supplied in the screenshots. Prompt guards cannot guarantee that a model will never follow injected instructions. |
| 3: missing competitor evidence becomes absence | Explicit absence is zero; unclear and missing responses remain blank, with separate flags. Agreement uses known pairs only, including historical zero-plus-unclear outputs. Hedonic fitting refuses unresolved evidence after applying requested scope. Collection and agreement integration tests pass. |
| 4: missing population weights | Configured strata require finite nonnegative shares with positive totals. No implicit equal-share substitution remains. Explicit weights normalize as before. An unstratified value model remains supported when no archetypes are configured. Tests cover both supported and rejected inputs. |
| 5: Git subprocess | Git provenance is read from HEAD, loose refs or packed refs, including worktree metadata, without spawning Git. Detached and packed-ref tests pass. |
| 2, 6, 8, 9: Unicode warnings | The screenshot excerpts show ASCII shebangs, which do not demonstrate Unicode deception. Shipped text contains no Unicode format controls, and Python identifiers are ASCII. Scientific symbols remain in explanatory text. The automated payload inspection passes. |
| 7: browser robots and delay bypass | Every routed HTTP browser request checks the selected origin and robots rules and waits for the host delay. POST requests are blocked. Service workers are disabled; WebSockets are intercepted without connecting upstream. HTTP redirect destinations are checked as well. Real Chromium against a local fixture verifies allowed requests, minimum spacing, and that blocked paths, POST, workers and sockets never reach the server. |
| 8: PDF subprocess | PDF extraction uses pypdf. Local PDF and plain-text ingestion tests pass, including plain text when the optional PDF import is unavailable. The tested pypdf release is pinned. |
| 9: model CLI subprocess | Restored the supported CLI runner that the previous fix incorrectly removed. It uses an argument list without a shell, restricted environment and timeout; failure exit codes are rejected. Both CLI and API runners remain selectable and require transfer confirmation. Mocked transport tests pass; no paid/live model calls were made. A generic subprocess warning can legitimately remain. |
| 10: self-test subprocess | The development runner lives under tests/, outside the skill payload. Its subprocesses execute known repository scripts. Existing-directory protection passes. Its new fixture is explicitly fictional and independent of the blank public templates. |
| 11: dynamic expression attribute access | RNG access is explicit; expression calls are restricted to named operations and allowed argument counts. Arbitrary Python, namespace callables and positional/keyword output mutation are rejected. The previous helper name remains compatible. Expression tests pass. Parsing an arithmetic AST is still intentional; Python eval/exec are not used. |
| 12: conjoint dynamic attributes | Design records use dictionary keys, retaining custom attribute names that namedtuple conversion can rename. The custom-column regression test and both full conjoint estimators pass. |

## Validation

- 36 regression tests pass, including real Chromium (Playwright 1.64.1), local PDF ingestion, mocked model transports and payload inspection.
- 18 full synthetic workflow assertions pass: value attribution, market premium recovery, market meter elasticity, Bayesian transaction elasticity and convergence, posterior predictive checks, fallback and Bayesian conjoint recovery, synthesis and proposal scoring.
- All 17 shipped executable script entry points accept `--help`.
- Python 3.12.13, all declared analysis dependencies, and optional Playwright/Anthropic dependencies installed successfully in an isolated environment.
- The recovery expectation is derived from the fictional fixture's actual segment shares and randomized anchors. The original 25% tolerance is unchanged.
- The four distribution archives are rebuilt and checked for corruption, correct SKILL.md placement and exclusion of development tests.

Run regression checks:

```sh
RUN_PRICING_BROWSER_TESTS=1 python -m unittest discover -s tests -v
python tests/selftest_value_pricing.py
sh scripts/package.sh
```

The browser check requires Playwright and Chromium. Real provider authentication, paid model outputs, arbitrary production studies, and the hosted ClawHub scanner are outside this local verification. Source instruction guards are defense in depth, not proof against all prompt injection. Re-upload the revised skill for a fresh hosted scan; do not claim a clean scan based on this report.

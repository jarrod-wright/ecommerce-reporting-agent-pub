# E-commerce Performance Reporting Agent

**A provider-agnostic, security-hardened AI agent that turns Shopify and Google Analytics 4 data into automated e-commerce performance reports — with a reproducible request-integrity proof you can run in one command.**

[![CI](https://github.com/jarrod-wright/ecommerce-reporting-agent-pub/actions/workflows/ci.yml/badge.svg)](https://github.com/jarrod-wright/ecommerce-reporting-agent-pub/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

Built on [LangGraph](https://langchain-ai.github.io/langgraph/), the agent runs a
`fetch → process → insights → report` pipeline behind a hardened FastAPI service
and a Streamlit front end. The interesting part isn't that it writes reports — it's
*how* it's engineered: the LLM provider is a config value, request integrity is
cryptographically enforced and provable, and the agent's analytical output is
checked against generated ground truth rather than asserted correct.

## Highlights

- **Provider-agnostic by construction.** A graph node asks for a *role*
  (`primary`, `challenger`); the concrete `(provider, model)` pair is resolved in a
  factory (`src/agent/clients/factory.py`). Swapping between Google Gemini and
  Anthropic Claude is a config change, not a code change.
- **Cryptographic request integrity — and you can prove it.** `make demo` runs a
  real HMAC-SHA256 signature check end-to-end: a valid signature passes, a
  tampered body is rejected, a missing signature is rejected. No mocks, no staging.
- **Validated against ground truth, not vibes.** A dynamic validation framework
  (`src/validation/`) checks the agent's business-logic outputs against generated
  ground-truth datasets, with evidence captured in `results/validation_results.json`
  — so "it works" is a measured claim, not an assertion.
- **Security-first, documented as-built.** A full [STRIDE threat
  model](docs/05_security/THREAT_MODEL_V1.md), OWASP-LLM mapping, fail-closed
  configuration, rate limiting, JWT auth, security headers, and `bleach` output
  sanitization — with an honest ledger of what's wired and what isn't.
- **TDD + honeypot discipline.** Security-critical behaviour is proven by tests
  that demonstrate the *rejected* state (HMAC tamper → 403; fail-closed config
  raising on placeholder secrets), not just the happy path.
- **191 passing tests, CI on every push, one-command containerised run.**

## See it work in 30 seconds

```bash
poetry install
make demo          # HMAC request-integrity proof: valid -> 200, tampered -> 403, missing -> 403
```

`make demo` prints a real `hmac.new(WEBHOOK_SECRET_KEY, body, sha256).hexdigest()`
and drives it against the live guarded route — the signature guard is demonstrated,
not described.

## Architecture

```
src/
  main.py                       FastAPI service (validation, JWT auth, HMAC middleware)
  agent/
    graph/                      LangGraph nodes: fetch -> process -> insights -> report
    clients/                    provider-agnostic LLM + data clients (factory pattern)
    api/middleware/             HMAC request-signing middleware
    config.py                   fail-closed settings
    utils/pii_scrubber.py       presidio PII scrubbing helper
  streamlit_app/                Streamlit UI
  validation/                   dynamic business-logic validation framework
```

The design goal throughout is **substitutability**: the LLM provider, the data
source clients, and the validation datasets are all seams, so the system can be
re-pointed without rewrites. `src/agent/clients/factory.py` is the clearest
example — role-to-model resolution keeps the graph logic provider-independent.

## Quickstart

Requires Python ≥ 3.11 and [Poetry](https://python-poetry.org/).

```bash
poetry install
cp .env.example .env          # then fill in the values (see Configuration)
poetry run pytest             # 191 passed, 13 skipped
make demo                     # the HMAC request-integrity proof
```

One-command containerised run:

```bash
docker compose up --build     # serves the API on :8080; reads secrets from .env
```

### Configuration

Copy `.env.example` to `.env` and set the values. Config is **fail-closed**: the
service refuses to start if `WEBHOOK_SECRET_KEY` or `JWT_SECRET_KEY` is unset,
empty, or a placeholder (see `src/agent/config.py`) — misconfiguration fails loudly
at boot rather than silently at runtime.

LLM defaults run on Google Gemini's free tier for a **zero-cost demo**:

- **`gemini-3.1-flash-lite`** is the default (free-tier, cost-efficient).
- `gemini-3.5-flash` is available as a higher-quality option but requires a
  **billed** API key — set `PRIMARY_LLM_MODEL=gemini-3.5-flash` to use it.

## Security

Controls are documented as-built in the [STRIDE threat
model](docs/05_security/THREAT_MODEL_V1.md) (status: *as-built v1*).

**Implemented:** HMAC request signing, rate limiting, global exception handling,
strict Pydantic input validation, security headers, and `bleach` HTML output
sanitization.

### HMAC request-integrity demo

`make demo` proves the HMAC-SHA256 request-signature guard end-to-end against the
guarded `/demo/verify` route:

- a body signed with the key → **200**
- the same signature over a **tampered** body → **403**
- a missing signature → **403**

**Enforcement scope, stated plainly:** the HMAC guard applies to routes *not* in
the middleware's `skip_paths`. `/generate-report` and `/test-exception` **are** in
`skip_paths` and are therefore not signature-gated — `/generate-report` is
protected by JWT bearer auth instead. The demo targets the dedicated HMAC-guarded
`/demo/verify` route specifically so the proof is real rather than staged. Knowing
exactly which routes a control does and doesn't cover is the point.

## Project scope & status

This is an **engineering portfolio / case-study project**, built and dynamically
validated as an exercise in doing agentic backend engineering *properly* —
provider abstraction, cryptographic request integrity, ground-truth validation, and
a documented threat model. It has not been operated as a commercial service; the
value on offer here is the engineering and the way it's evidenced, and every claim
above is backed by code and a runnable test suite rather than by assertion.

That same discipline extends to what *isn't* finished: where a control is designed
but not yet wired end-to-end, this README and the threat model say so directly.

## Known limitations

Tracked, not hidden:

- **PII scrubbing layer is not yet wired.** The `presidio`-based scrubber
  (`src/agent/utils/pii_scrubber.py`) is implemented and unit-tested but is **not
  yet invoked** in the request/agent flow, so OWASP LLM01/LLM06 remain partial
  residuals (see the threat model). Output HTML *is* sanitized via `bleach`.
- **Legacy lint debt.** `ruff check .` is clean, but a set of pre-existing legacy
  modules carry scoped, documented `per-file-ignores` in `pyproject.toml` (mostly
  long lines). New code passes under the full ruleset; the legacy debt is tracked
  for incremental cleanup rather than mass-rewritten.

## Testing

```bash
poetry run pytest        # 191 passed, 13 skipped
poetry run ruff check .  # clean
```

The suite provisions demo security keys via `tests/conftest.py`, so it runs without
any real secrets.

## License

[MIT](LICENSE).

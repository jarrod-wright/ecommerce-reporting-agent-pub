# E-commerce Performance Reporting Agent

An AI agent that turns Shopify and Google Analytics 4 data into automated
e-commerce performance reports. Built on [LangGraph](https://langchain-ai.github.io/langgraph/)
with a provider-agnostic LLM layer, a hardened FastAPI service, and a Streamlit
front end.

## Status & honesty

This project was **built and dynamically validated as an engineering portfolio
piece**. It has **never been operated commercially** and is not a product. Running
it end-to-end against live data and paid LLM inference is **uneconomic to operate
solo** — the value here is the engineering, not a service.

What that means for you as a reader:

- The security, testing, and architecture claims below are backed by code and by a
  runnable suite (`poetry run pytest` → 191 passed, 13 skipped), not by assertion.
- Where a control is designed but not yet wired end-to-end, this README and the
  [threat model](docs/05_security/THREAT_MODEL_V1.md) say so plainly (see
  [Known limitations](#known-limitations)).

## Quickstart

Requires Python ≥ 3.11 and [Poetry](https://python-poetry.org/).

```bash
poetry install
cp .env.example .env          # then fill in the values (see below)
poetry run pytest             # run the test suite
make demo                     # run the HMAC request-integrity proof
```

One-command containerised run:

```bash
docker compose up --build     # serves the API on :8080; reads secrets from .env
```

### Configuration

Copy `.env.example` to `.env` and set the values. Config is **fail-closed**: the
service refuses to start if `WEBHOOK_SECRET_KEY` or `JWT_SECRET_KEY` is unset,
empty, or a placeholder value (see `src/agent/config.py`).

LLM defaults run on Google Gemini's free tier for a **zero-cost demo**:

- **`gemini-3.1-flash-lite`** is the default (free-tier, cost-efficient).
- `gemini-3.5-flash` is available as a higher-quality option but requires a
  **billed** API key — set `PRIMARY_LLM_MODEL=gemini-3.5-flash` to use it.

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

A graph node asks for a *role* (`primary`, `challenger`) and the concrete
`(provider, model)` pair is resolved in `src/agent/clients/factory.py`, so the
agent is genuinely provider-agnostic (Google Gemini and Anthropic Claude).

## Security

Security controls are documented as-built in the
[STRIDE threat model](docs/05_security/THREAT_MODEL_V1.md) (status: *as-built v1*).

**Implemented:** HMAC request signing, rate limiting, global exception handling,
strict Pydantic input validation, security headers, and `bleach` HTML output
sanitization.

### HMAC request-integrity demo

`make demo` proves the HMAC-SHA256 request-signature guard end-to-end:

- a body signed with the key on the guarded `/demo/verify` route -> **200**
- the same signature over a **tampered** body -> **403**
- a missing signature -> **403**

and prints the real `hmac.new(WEBHOOK_SECRET_KEY, body, sha256).hexdigest()`.

**Enforcement scope (stated honestly):** the HMAC guard applies to routes that are
**not** in the middleware's `skip_paths`. The `/generate-report` and
`/test-exception` routes **are** in `skip_paths` and are therefore **not**
signature-gated — `/generate-report` is protected by JWT bearer authentication
instead. The demo targets the dedicated, HMAC-guarded `/demo/verify` route so the
proof is real rather than staged.

## Crown jewels

- **Provider-agnostic LLM factory** (`src/agent/clients/factory.py`) — role -> model
  resolution, so swapping providers is a config change, not a code change.
- **Dynamic validation framework** (`src/validation/`, evidence in
  `results/validation_results.json`) — the agent's business-logic outputs are
  checked against generated ground truth rather than asserted correct.
- **TDD + honeypot discipline** — security-critical behaviour is proven by tests
  that demonstrate the *rejected* state (e.g. the HMAC tamper -> 403 case, and the
  fail-closed config raising on placeholder secrets).

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

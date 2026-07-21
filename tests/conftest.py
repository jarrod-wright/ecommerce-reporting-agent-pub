"""Shared pytest fixtures / test-environment provisioning (T08b).

The security config is fail-closed (see ``src/agent/config.py``): the module-level
``settings = Settings()`` singleton raises at import unless ``WEBHOOK_SECRET_KEY``
and ``JWT_SECRET_KEY`` are set to secure, non-placeholder values. Because many
modules import that singleton, the whole suite (and CI) would fail to collect
without those keys.

We inject **demo** keys into the process environment here, before any test module
is imported, so the suite loads cleanly. These are demo-only values — never real
secrets — and are deliberately free of the insecure markers the validator rejects.
Using ``setdefault`` means a real/CI-provided value in the environment always wins.
"""

import os

# Demo-only security keys — not real secrets, and not placeholder-marked.
_DEMO_ENV = {
    "WEBHOOK_SECRET_KEY": "demo-webhook-secret-not-a-real-key-0123456789",
    "JWT_SECRET_KEY": "demo-jwt-secret-not-a-real-key-0123456789",
}

# Set at import time (conftest is imported before test collection) so the
# fail-closed ``Settings()`` singleton can load when test modules import it.
for _key, _value in _DEMO_ENV.items():
    os.environ.setdefault(_key, _value)

"""Fail-closed configuration tests (T07 RED / T08 GREEN).

The security secrets ``WEBHOOK_SECRET_KEY`` and ``JWT_SECRET_KEY`` must never
fall back to an insecure value. Unset, empty, and known-placeholder values must
all be rejected at load time (fail-closed); only an explicitly-provided secure
value is allowed to load. Correctness is proven by demonstrating the *rejected*
state (a raised ``ValidationError``), i.e. the guard blocks the insecure config.
"""

import pytest
from pydantic import ValidationError

from agent.config import Settings

# An explicitly non-empty, non-placeholder value (demo only — never a real secret).
SECURE = "demo-only-not-a-real-secret-0123456789abcdef"

# Known-insecure values that fail-closed config must reject: empty + the two
# legacy placeholders that used to be the defaults in ``config.py``.
INSECURE_VALUES = [
    "",
    "default-secret-key-change-in-production",
    "test-secret-key",
]


def _load(monkeypatch, **overrides):
    """Instantiate ``Settings`` hermetically: ignore any ``.env`` and any ambient
    secret env, using only the explicitly-provided overrides."""
    monkeypatch.delenv("WEBHOOK_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    return Settings(_env_file=None, **overrides)


@pytest.mark.parametrize("bad", INSECURE_VALUES)
def test_webhook_secret_key_rejects_insecure(monkeypatch, bad):
    """WEBHOOK_SECRET_KEY = empty/placeholder must raise (guard blocks it)."""
    with pytest.raises(ValidationError):
        _load(monkeypatch, WEBHOOK_SECRET_KEY=bad, JWT_SECRET_KEY=SECURE)


@pytest.mark.parametrize("bad", INSECURE_VALUES)
def test_jwt_secret_key_rejects_insecure(monkeypatch, bad):
    """JWT_SECRET_KEY = empty/placeholder must raise (guard blocks it)."""
    with pytest.raises(ValidationError):
        _load(monkeypatch, WEBHOOK_SECRET_KEY=SECURE, JWT_SECRET_KEY=bad)


def test_unset_security_keys_raise(monkeypatch):
    """Neither key provided, no ``.env``, no ambient env -> required -> must raise."""
    with pytest.raises(ValidationError):
        _load(monkeypatch)


def test_valid_security_keys_load_clean(monkeypatch):
    """An explicit secure value for both keys loads without error."""
    s = _load(monkeypatch, WEBHOOK_SECRET_KEY=SECURE, JWT_SECRET_KEY=SECURE)
    assert s.WEBHOOK_SECRET_KEY == SECURE
    assert s.JWT_SECRET_KEY == SECURE

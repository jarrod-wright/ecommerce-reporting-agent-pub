"""HMAC request-integrity demo test (T11 RED / T12 GREEN).

Proves the HMAC-SHA256 request-signature guard on a route the middleware
*actually* guards. The contract was confirmed by reading
``src/agent/api/middleware/request_signing.py`` (INV-19):

* header:  ``x-request-signature``
* digest:  ``hmac.new(WEBHOOK_SECRET_KEY, raw_body, sha256).hexdigest()``
* guarded: any path NOT in ``skip_paths``; a valid signature passes, a missing
           or invalid signature is rejected with HTTP 403.

``/generate-report`` is deliberately in ``skip_paths`` (NOT signature-gated), so
the demo targets a dedicated ``/demo/verify`` route wired through the middleware.
Correctness is proven by demonstrated rejection: the tampered-body case returns 403.
"""

import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from agent.config import settings
from main import app

DEMO_ROUTE = "/demo/verify"


def _sign(body: bytes, key: str) -> str:
    """Real HMAC-SHA256 hex digest of the raw body — the exact contract the
    middleware computes."""
    return hmac.new(key.encode(), body, hashlib.sha256).hexdigest()


def test_valid_signature_returns_200():
    """A body signed with the demo key on the guarded route is accepted."""
    client = TestClient(app)
    body = json.dumps({"message": "integrity-demo"}).encode()
    signature = _sign(body, settings.WEBHOOK_SECRET_KEY)
    response = client.post(
        DEMO_ROUTE,
        content=body,
        headers={"x-request-signature": signature, "content-type": "application/json"},
    )
    assert response.status_code == 200


def test_tampered_body_returns_403():
    """Honeypot: the original signature over a *tampered* body is rejected (403).

    Correctness by demonstrated refusal — this is the load-bearing assertion.
    """
    client = TestClient(app)
    body = json.dumps({"message": "integrity-demo"}).encode()
    # signature computed over the ORIGINAL body
    signature = _sign(body, settings.WEBHOOK_SECRET_KEY)
    tampered = json.dumps({"message": "tampered-in-flight"}).encode()
    response = client.post(
        DEMO_ROUTE,
        content=tampered,
        headers={"x-request-signature": signature, "content-type": "application/json"},
    )
    assert response.status_code == 403


def test_digest_is_a_real_sha256_and_server_agrees():
    """The digest is a real 64-hex-char HMAC-SHA256, and the server accepts
    exactly that digest for exactly that body (digest-equality)."""
    body = b'{"message": "integrity-demo"}'
    expected = hmac.new(
        settings.WEBHOOK_SECRET_KEY.encode(), body, hashlib.sha256
    ).hexdigest()
    assert len(expected) == 64
    assert all(c in "0123456789abcdef" for c in expected)

    client = TestClient(app)
    response = client.post(
        DEMO_ROUTE,
        content=body,
        headers={"x-request-signature": expected, "content-type": "application/json"},
    )
    assert response.status_code == 200

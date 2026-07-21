"""Runnable HMAC request-integrity demo (T12).

Proves the HMAC-SHA256 request-signature guard end-to-end against the app's
guarded ``/demo/verify`` route:

* a body signed with the demo key            -> 200
* the *same* signature over a TAMPERED body  -> 403  (integrity violation caught)
* a missing signature                        -> 403

The digest printed is a real ``hmac.new(WEBHOOK_SECRET_KEY, body, sha256).hexdigest()``.

Run with ``make demo`` (or ``python demo/hmac_integrity_demo.py``). The signing key
is read from the environment (``WEBHOOK_SECRET_KEY``); a clearly-labelled demo value
is used only as a fallback so the fail-closed config loads — never a real secret.
``/generate-report`` is deliberately NOT signature-gated (it is in ``skip_paths``).
"""

import hashlib
import hmac
import json
import os

ROUTE = "/demo/verify"

# Demo-only fallbacks so the fail-closed config loads when run standalone; a real
# environment value always wins. These are NOT real secrets.
_DEMO_KEYS = {
    "WEBHOOK_SECRET_KEY": "demo-webhook-secret-not-a-real-key-0123456789",
    "JWT_SECRET_KEY": "demo-jwt-secret-not-a-real-key-0123456789",
}


def _sign(body: bytes, key: str) -> str:
    """Real HMAC-SHA256 hex digest of the raw body — the middleware's contract."""
    return hmac.new(key.encode(), body, hashlib.sha256).hexdigest()


def main() -> int:
    for name, demo_value in _DEMO_KEYS.items():
        os.environ.setdefault(name, demo_value)

    # Imported after env provisioning so the fail-closed Settings singleton loads.
    from fastapi.testclient import TestClient

    from agent.config import settings
    from main import app

    client = TestClient(app)
    body = json.dumps({"message": "integrity-demo"}).encode()
    signature = _sign(body, settings.WEBHOOK_SECRET_KEY)

    print("HMAC request-integrity demo")
    print("=" * 48)
    print(f"route            : {ROUTE} (guarded — not in skip_paths)")
    key_len = len(settings.WEBHOOK_SECRET_KEY)
    print(f"key              : WEBHOOK_SECRET_KEY (len={key_len}, demo, from env)")
    print(f"body             : {body.decode()}")
    print(f"HMAC-SHA256 sig  : {signature}")
    print("-" * 48)

    valid = client.post(ROUTE, content=body, headers={"x-request-signature": signature})
    print(f"valid signature      -> {valid.status_code}  (expect 200)")

    tampered_body = json.dumps({"message": "tampered-in-flight"}).encode()
    tampered = client.post(
        ROUTE, content=tampered_body, headers={"x-request-signature": signature}
    )
    print(f"tampered body        -> {tampered.status_code}  (expect 403)")

    missing = client.post(ROUTE, content=body)
    print(f"missing signature    -> {missing.status_code}  (expect 403)")

    ok = (
        valid.status_code == 200
        and tampered.status_code == 403
        and missing.status_code == 403
    )
    print("=" * 48)
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

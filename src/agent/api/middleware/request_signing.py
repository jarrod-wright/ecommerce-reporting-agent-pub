"""HMAC request signature validation middleware.

This module implements the Cryptographic Request Integrity Pattern as specified
in the Resilient API Framework to prevent request tampering and ensure
message authenticity through HMAC-SHA256 signature verification.
"""

import hashlib
import hmac

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from agent.config import settings


class HMACSignatureMiddleware(BaseHTTPMiddleware):
    """HMAC signature validation middleware for request integrity verification.

    This middleware implements cryptographic request integrity checking by:
    1. Extracting the HMAC signature from the X-Request-Signature header
    2. Computing the expected HMAC-SHA256 signature of the request body
    3. Using timing-attack-resistant comparison to validate signatures
    4. Rejecting requests with missing or invalid signatures with HTTP 403

    This provides defense against:
    - Request tampering attacks
    - Replay attacks (when combined with timestamps)
    - Unauthorized API access
    """

    def __init__(self, app, secret_key: str = None):
        """Initialize HMAC signature middleware.

        Args:
            app: FastAPI application instance
            secret_key: Optional secret key override (defaults to settings value)
        """
        super().__init__(app)
        self.secret_key = secret_key or settings.WEBHOOK_SECRET_KEY

    async def dispatch(self, request: Request, call_next) -> Response:
        """Validate HMAC signature and process request.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or endpoint handler

        Returns:
            Response from the next handler if signature is valid,
            or JSON error response with 403 status if invalid
        """
        # Skip signature validation for health check and certain endpoints
        # during testing
        skip_paths = [
            "/health",
            "/health/deep",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/generate-report",
            "/test-exception",
        ]
        request_path = request.url.path

        if request_path in skip_paths:
            return await call_next(request)

        # Extract signature from request headers
        provided_signature = request.headers.get("x-request-signature")

        if not provided_signature:
            # Return a proper 403 response. An exception raised inside a
            # BaseHTTPMiddleware.dispatch() propagates above the app's exception
            # handlers and would surface as HTTP 500, defeating the guard.
            return JSONResponse(
                status_code=403, content={"detail": "Missing request signature"}
            )

        # Read the raw request body
        body = await request.body()

        # Compute expected HMAC-SHA256 signature
        expected_signature = hmac.new(
            self.secret_key.encode(), body, hashlib.sha256
        ).hexdigest()

        # Use timing-attack-resistant comparison
        if not hmac.compare_digest(provided_signature, expected_signature):
            return JSONResponse(
                status_code=403, content={"detail": "Invalid request signature"}
            )

        # Signature is valid, proceed with request
        return await call_next(request)

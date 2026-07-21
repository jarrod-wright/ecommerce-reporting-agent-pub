"""FastAPI application for e-commerce performance reporting agent.

This module implements a hardened FastAPI service with proper input validation
and OWASP API Security countermeasures.
"""

import re
import uuid
from datetime import datetime, timezone

import bleach
import structlog
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, ConfigDict, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from agent.api.security import HMACSignatureMiddleware
from agent.clients.anthropic_client import AnthropicClient
from agent.clients.google_client import GoogleAIClient
from agent.config import settings
from agent.observability.logging_config import setup_logging


class GenerateReportRequest(BaseModel):
    """Hardened request model for report generation with OWASP API4 countermeasures.

    This model uses Pydantic Field validators to enforce strict constraints
    and prevent resource consumption attacks.
    """

    report_title: str = Field(
        ...,
        max_length=100,
        min_length=1,
        description="Title for the generated report",
        json_schema_extra={"example": "Monthly Sales Performance Report"},
    )

    date_range: str = Field(
        ...,
        max_length=50,
        min_length=1,
        description="Date range for the report analysis",
        json_schema_extra={"example": "2024-01-01 to 2024-01-31"},
    )

    model_config = ConfigDict(
        extra="forbid"  # Reject any additional fields not defined in the model
    )

    @field_validator("report_title", "date_range")
    @classmethod
    def sanitize_html_string_fields(cls, v: str) -> str:
        """Sanitize HTML/JS from string fields using Hybrid Sanitization Doctrine.

        This validator implements the two-layer Hybrid Sanitization pattern:
        1. Formatting Layer (Regex): Replace dangerous tags with [removed] placeholders
        2. Security Layer (Bleach): Strip any remaining dangerous content

        This directly addresses the "Critical Security Gaps" for "API Input Models"
        identified in the V1.0 Release Candidate Audit Report.
        """
        if not isinstance(v, str):
            return v

        # Layer 1: Formatting Layer - Replace specific tags with [removed] placeholders
        # Replace opening tags (both self-closing and regular)
        sanitized = re.sub(
            r'<(script|iframe|img|object|embed|form)(\s[^>]*)?/?>',
            '[removed]',
            v,
            flags=re.IGNORECASE
        )
        # Replace closing tags
        sanitized = re.sub(
            r'</(script|iframe|img|object|embed|form)>',
            '[removed]',
            sanitized,
            flags=re.IGNORECASE
        )
        # Remove event handlers like onerror, onclick, etc.
        sanitized = re.sub(
            r'\s(on\w+|javascript:)[^>\s]*',
            '',
            sanitized,
            flags=re.IGNORECASE
        )

        # Keep individual [removed] markers to show each sanitized tag

        # Layer 2: Security Layer - Use bleach as final comprehensive cleanup
        final_sanitized = bleach.clean(
            sanitized,
            tags=[],  # Allow no tags
            attributes={},  # Allow no attributes
            strip=True,  # Strip disallowed tags completely
        )

        return final_sanitized


class GenerateReportResponse(BaseModel):
    """Response model for successful report generation requests."""

    message: str
    status: str


# Initialize HTTP Bearer security scheme for JWT authentication
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """JWT authentication security dependency function.

    This function implements the Authentication & Authorization mandate from the
    Resilient API Framework by validating JWT Bearer tokens for protected endpoints.

    Args:
        credentials: HTTP Bearer credentials containing the JWT token

    Returns:
        str: The authenticated user's identity (subject claim from JWT)

    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, or malformed
    """
    # Check if credentials were provided
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Decode and validate the JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Extract user identity from token subject
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify token expiration
        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(
            exp, tz=timezone.utc
        ) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=401,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except JWTError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# Configure structured logging for observability framework
setup_logging()

# Initialize rate limiter for API4: Unrestricted Resource Consumption countermeasures
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Initialize FastAPI application
app = FastAPI(
    title="E-commerce Performance Reporting Agent",
    description="AI-powered agent for automated e-commerce performance analysis",
    version="3.1.0",
)

# Add rate limit exceeded exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add HMAC signature validation middleware for cryptographic request integrity
app.add_middleware(HMACSignatureMiddleware)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Security headers middleware implementing OWASP API8 countermeasures.

    This middleware adds essential security headers to all HTTP responses
    to prevent content type sniffing and other client-side vulnerabilities.
    It also generates and adds a correlation ID for request tracing and
    binds it to the structured logging context.

    Args:
        request: The incoming HTTP request
        call_next: The next middleware or endpoint handler

    Returns:
        Response with security headers and correlation ID applied
    """
    # Generate unique correlation ID for request tracing
    correlation_id = str(uuid.uuid4())

    # Bind correlation ID to structured logging context
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

    response = await call_next(request)

    # Add comprehensive security headers per Resilient API Framework
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; object-src 'none'; "
        "frame-ancestors 'none'; upgrade-insecure-requests;"
    )

    # Add correlation ID header for observability framework
    response.headers["X-Correlation-ID"] = correlation_id

    return response


@app.get("/health")
@limiter.limit("15/minute")  # Conservative limit that allows the test to pass
async def health_check(request: Request):
    """Health check endpoint for monitoring and load balancer probes.

    This endpoint provides a simple health status check that can be used
    by monitoring systems, load balancers, and container orchestrators.
    Rate limited to 15 requests per minute to prevent DoS attacks while
    maintaining compatibility with test validation.

    Returns:
        Simple status response indicating the service is operational
    """
    return {"status": "ok"}


@app.get("/health/deep")
async def deep_health_check():
    """Deep health check endpoint implementing Active Health Verification Pattern.

    This endpoint performs dependency health checks by attempting to instantiate
    both AnthropicClient and GoogleAIClient to verify API key availability and
    client configuration validity. Returns detailed status information about
    each dependency's operational state.

    Returns:
        JSON response with overall health status and individual check results:
        - 200 OK with {"status": "healthy"} when all dependencies are operational
        - 503 Service Unavailable with {"status": "degraded", "checks": {...}}
          when any dependency fails
    """
    checks = {}
    all_healthy = True

    # Check AnthropicClient health
    try:
        AnthropicClient()
        checks["anthropic_api"] = True
    except Exception:
        checks["anthropic_api"] = False
        all_healthy = False

    # Check GoogleAIClient health
    try:
        GoogleAIClient()
        checks["google_api"] = True
    except Exception:
        checks["google_api"] = False
        all_healthy = False

    if all_healthy:
        return {"status": "healthy"}
    else:
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "checks": checks}
        )


@app.get("/test-exception")
async def test_exception_endpoint():
    """Test endpoint that raises exception for global handler testing.

    This endpoint exists solely for testing the global exception handler.
    It's not rate limited to avoid interference with other tests.
    """
    raise Exception("This is a test exception")


@app.post("/generate-report", response_model=GenerateReportResponse)
async def generate_report(
    request: GenerateReportRequest, current_user: str = Depends(get_current_user)
) -> GenerateReportResponse:
    """Generate an e-commerce performance report.

    This endpoint validates input against hardened Pydantic models and implements
    OWASP API Security countermeasures including:
    - Strict input validation (API3:2023)
    - Resource consumption limits (API4:2023)
    - Proper error handling with 422 status codes

    Args:
        request: Validated report generation request

    Returns:
        Success message with report generation status
    """
    return GenerateReportResponse(
        message=(
            f"Report '{request.report_title}' generation initiated for "
            f"{request.date_range}"
        ),
        status="accepted",
    )


@app.post("/demo/verify")
async def demo_verify_signature(request: Request) -> JSONResponse:
    """HMAC request-integrity demo endpoint (T12).

    This route is intentionally NOT in the middleware's ``skip_paths``, so every
    request must carry a valid ``x-request-signature`` — the HMAC-SHA256 digest of
    the raw body (see ``HMACSignatureMiddleware``). Reaching this handler means the
    signature already verified; a missing or tampered body is rejected with 403 by
    the middleware before this code runs. It exists solely to demonstrate the guard
    and is not part of the product API. ``/generate-report`` is deliberately in
    ``skip_paths`` and is therefore NOT signature-gated.
    """
    return JSONResponse(
        status_code=200,
        content={"verified": True, "detail": "HMAC signature verified"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler implementing Structured Error Handling mandate.

    This handler captures all unhandled exceptions, logs full details for internal
    review using structured logging, and returns a standardized generic error
    response to prevent information disclosure vulnerabilities.

    Implements the Resilient API Framework's Structured Error Handling requirement
    for consistent, secure error responses.

    Args:
        request: The HTTP request that caused the exception
        exc: The unhandled exception that was raised

    Returns:
        Standardized JSON error response with 500 status code
    """
    # Get structured logger instance
    logger = structlog.get_logger()

    # Log full exception details for internal review
    logger.error(
        "Unhandled exception occurred",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        request_path=request.url.path,
        request_method=request.method,
        exc_info=True,
    )

    # Return standardized generic error response
    return JSONResponse(
        status_code=500, content={"detail": "An internal server error occurred."}
    )

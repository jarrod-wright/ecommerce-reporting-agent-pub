"""Security tests for API input validation and OWASP compliance."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from agent.config import settings
from main import GenerateReportRequest, app


def test_generate_report_endpoint_rejects_invalid_payload(jwt_tokens):
    """Test that the /generate-report endpoint rejects malformed JSON with 422 status.

    This test implements OWASP API Security countermeasures for injection attacks
    and improper data handling by verifying that the API properly validates input
    and rejects malformed payloads with appropriate HTTP error codes.
    """
    client = TestClient(app)

    # Include valid JWT token for authentication
    headers = {"Authorization": f"Bearer {jwt_tokens['valid_token']}"}

    # Test case 1: report_title should be string, not integer
    malformed_payload_1 = {
        "report_title": 12345,  # Invalid: should be string
        "date_range": "2024-01-01 to 2024-01-31",
    }

    response = client.post("/generate-report", json=malformed_payload_1, headers=headers)
    assert response.status_code == 422  # Unprocessable Entity

    # Test case 2: Extra unexpected field should be rejected
    malformed_payload_2 = {
        "report_title": "Valid Report Title",
        "date_range": "2024-01-01 to 2024-01-31",
        "malicious_field": "should_not_be_allowed",  # Extra field
    }

    response = client.post("/generate-report", json=malformed_payload_2, headers=headers)
    assert response.status_code == 422  # Unprocessable Entity


def test_api_includes_security_headers():
    """Test that the API includes required security headers in responses.

    This test implements OWASP API8: Security Misconfiguration countermeasures
    by verifying that all API responses include essential security headers
    to prevent content type sniffing and other client-side vulnerabilities.
    """
    client = TestClient(app)

    # Make a simple GET request to the health endpoint
    response = client.get("/health")

    # Verify the response includes the X-Content-Type-Options security header
    assert response.headers.get("x-content-type-options") == "nosniff"


def test_api_responses_contain_correlation_id():
    """Test that all API responses contain X-Correlation-ID header.

    This test ensures that the correlation ID middleware is properly
    configured to add a correlation ID header to all API responses,
    supporting the observability framework's tracing capabilities.
    """
    client = TestClient(app)

    # Make a simple GET request to the health endpoint
    response = client.get("/health")

    # Assert that the response headers contain the correlation ID
    assert "x-correlation-id" in response.headers

    # Assert that the correlation ID value is a non-empty string
    correlation_id = response.headers.get("x-correlation-id")
    assert correlation_id is not None
    assert isinstance(correlation_id, str)
    assert len(correlation_id) > 0


def test_api_responses_contain_comprehensive_security_headers():
    """Test that all API responses contain comprehensive security headers.

    This test ensures that the API includes all required security headers
    as mandated by the Resilient API Framework for defense against
    common web vulnerabilities including clickjacking, MITM attacks,
    and content injection.
    """
    client = TestClient(app)

    # Make a simple GET request to the health endpoint
    response = client.get("/health")

    # Assert that the response headers contain the comprehensive security headers
    assert response.headers.get("strict-transport-security") == (
        "max-age=31536000; includeSubDomains"
    )
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("content-security-policy") == (
        "default-src 'self'; object-src 'none'; "
        "frame-ancestors 'none'; upgrade-insecure-requests;"
    )


def test_rate_limiter_blocks_excessive_requests():
    """Test that the rate limiter blocks excessive requests with HTTP 429.

    This test implements OWASP API4: Unrestricted Resource Consumption
    countermeasures and mitigates LLM04: Model Denial of Service threats
    by verifying that the API properly enforces rate limits and returns
    HTTP 429 status codes when request limits are exceeded.
    """
    client = TestClient(app)

    # Make multiple requests to the health endpoint to exceed rate limit
    responses = []
    for _ in range(20):  # Attempt 20 requests rapidly
        response = client.get("/health")
        responses.append(response)

        # Stop early if we get rate limited
        if response.status_code == 429:
            break

    # Assert that at least one request was rate limited with 429 status
    rate_limited_responses = [r for r in responses if r.status_code == 429]
    assert len(rate_limited_responses) > 0, (
        "Expected at least one 429 response from rate limiter"
    )


def test_global_exception_handler_returns_500():
    """Test that the global exception handler returns standardized 500 error response.

    This test implements the Structured Error Handling mandate from the Resilient API
    Framework by verifying that unhandled exceptions are caught by the global handler
    and return a consistent, secure error response without exposing internal details.
    """
    # Use a separate TestClient instance to avoid rate limiting conflicts with other tests
    client = TestClient(app, raise_server_exceptions=False)

    # Make request to test-exception endpoint that always raises an exception
    response = client.get("/test-exception")

    # Assert the HTTP status code is exactly 500
    assert response.status_code == 500

    # Assert the JSON response body matches the expected standardized format
    assert response.json() == {"detail": "An internal server error occurred."}


@patch("main.AnthropicClient")
@patch("main.GoogleAIClient")
def test_deep_health_check_success_when_dependencies_are_healthy(
    mock_google_client, mock_anthropic_client
):
    """Test that /health/deep returns 200 OK when all dependencies are healthy.

    This test implements the Active Health Verification Pattern by verifying
    that the deep health check endpoint properly validates external dependencies
    and returns a healthy status when all services are operational.
    """
    client = TestClient(app)

    # Mock both clients to behave normally (no exceptions raised)
    mock_anthropic_client.return_value
    mock_google_client.return_value

    # Make request to /health/deep endpoint
    response = client.get("/health/deep")

    # Assert that the response status code is 200 OK
    assert response.status_code == 200

    # Assert that the JSON response body contains healthy status
    assert response.json() == {"status": "healthy"}


@patch("main.AnthropicClient")
@patch("main.GoogleAIClient")
def test_deep_health_check_degraded_when_dependency_fails(
    mock_google_client, mock_anthropic_client
):
    """Test that /health/deep returns 503 Service Unavailable when a dependency fails.

    This test implements the Active Health Verification Pattern by verifying
    that the deep health check endpoint properly detects failing dependencies
    and returns a degraded status with specific failure information.
    """
    client = TestClient(app)

    # Mock AnthropicClient to raise an exception
    mock_anthropic_client.side_effect = Exception("API is down")

    # Mock GoogleAIClient to behave normally
    mock_google_client.return_value

    # Make request to /health/deep endpoint
    response = client.get("/health/deep")

    # Assert that the response status code is 503 Service Unavailable
    assert response.status_code == 503

    # Assert that the JSON response body contains degraded status with specific check results
    assert response.json() == {
        "status": "degraded",
        "checks": {"anthropic_api": False, "google_api": True},
    }


def test_generate_report_request_sanitizes_inputs():
    """Test that GenerateReportRequest sanitizes malicious HTML inputs using Hybrid Sanitization.

    This test implements the hybrid sanitization approach by verifying that
    the GenerateReportRequest Pydantic model automatically sanitizes HTML/JavaScript
    payloads in input fields using the two-layer approach:
    1. Formatting Layer (Regex): Replace specific tags with [removed] placeholders
    2. Security Layer (Bleach): Strip any remaining dangerous content

    This test directly addresses the "Critical Security Gaps" for "API Input Models"
    identified in the V1.0 Release Candidate Audit Report.
    """
    # Test report_title field with malicious script injection
    malicious_request = GenerateReportRequest(
        report_title="<script>alert(1)</script>Quarterly Report",
        date_range="2024-01-01 to 2024-03-31",
    )

    # Assert that the script tags were replaced with [removed] placeholders
    assert (
        malicious_request.report_title == "[removed]alert(1)[removed]Quarterly Report"
    )

    # Test date_range field with malicious iframe injection (shorter payload)
    malicious_request_2 = GenerateReportRequest(
        report_title="Valid Report Title",
        date_range="<iframe></iframe>2024-01-01 to 2024-03-31",
    )

    # Assert that the iframe tags were replaced with [removed] placeholders (open + close)
    assert malicious_request_2.date_range == "[removed][removed]2024-01-01 to 2024-03-31"

    # Test multiple dangerous tags in a single field (shorter payload)
    malicious_request_3 = GenerateReportRequest(
        report_title="<img><object>Report",
        date_range="2024-01-01 to 2024-03-31",
    )

    # Assert that both tags were sanitized according to the Hybrid Sanitization pattern
    assert malicious_request_3.report_title == "[removed][removed]Report"


@pytest.fixture
def jwt_tokens():
    """Fixture to generate valid and invalid JWT tokens for testing authentication.
    
    Returns a dictionary containing:
    - valid_token: A properly signed JWT token that should pass authentication
    - invalid_token: A JWT token with incorrect signature that should fail authentication
    - expired_token: A JWT token that has expired and should fail authentication
    """
    # Secret key for JWT encoding/decoding — must match application config
    # (fail-closed config no longer ships a hardcoded default key).
    secret_key = settings.JWT_SECRET_KEY
    algorithm = "HS256"

    # Valid token with future expiration
    valid_payload = {
        "sub": "test-user",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    valid_token = jwt.encode(valid_payload, secret_key, algorithm=algorithm)

    # Invalid token with wrong secret key
    invalid_token = jwt.encode(valid_payload, "wrong-secret-key", algorithm=algorithm)

    # Expired token
    expired_payload = {
        "sub": "test-user",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
    }
    expired_token = jwt.encode(expired_payload, secret_key, algorithm=algorithm)

    return {
        "valid_token": valid_token,
        "invalid_token": invalid_token,
        "expired_token": expired_token,
    }


def test_protected_endpoint_success_with_valid_token(jwt_tokens):
    """Test that protected endpoint returns 200 OK with valid JWT token.
    
    This test implements JWT authentication requirements from the Authentication & Authorization
    mandate by verifying that protected endpoints accept requests with valid Bearer tokens
    and return successful responses.
    
    Expected to FAIL until JWT authentication is implemented on the /generate-report endpoint.
    """
    client = TestClient(app)

    # Prepare valid request payload
    payload = {
        "report_title": "Test Report",
        "date_range": "2024-01-01 to 2024-01-31",
    }

    # Include valid JWT token in Authorization header
    headers = {"Authorization": f"Bearer {jwt_tokens['valid_token']}"}

    # Make request to protected endpoint
    response = client.post("/generate-report", json=payload, headers=headers)

    # Assert successful response (will fail until endpoint is protected)
    assert response.status_code == 200


def test_protected_endpoint_fails_with_invalid_token(jwt_tokens):
    """Test that protected endpoint returns 401 Unauthorized with invalid JWT token.
    
    This test implements JWT authentication requirements from the Authentication & Authorization
    mandate by verifying that protected endpoints reject requests with invalid Bearer tokens
    and return 401 Unauthorized responses.
    
    Expected to FAIL until JWT authentication is implemented on the /generate-report endpoint.
    """
    client = TestClient(app)

    # Prepare valid request payload
    payload = {
        "report_title": "Test Report",
        "date_range": "2024-01-01 to 2024-01-31",
    }

    # Include invalid JWT token in Authorization header
    headers = {"Authorization": f"Bearer {jwt_tokens['invalid_token']}"}

    # Make request to protected endpoint
    response = client.post("/generate-report", json=payload, headers=headers)

    # Assert 401 Unauthorized response (will fail until endpoint is protected)
    assert response.status_code == 401


def test_protected_endpoint_fails_with_no_token():
    """Test that protected endpoint returns 401 Unauthorized with no Authorization header.
    
    This test implements JWT authentication requirements from the Authentication & Authorization
    mandate by verifying that protected endpoints reject requests without Bearer tokens
    and return 401 Unauthorized responses.
    
    Expected to FAIL until JWT authentication is implemented on the /generate-report endpoint.
    """
    client = TestClient(app)

    # Prepare valid request payload
    payload = {
        "report_title": "Test Report",
        "date_range": "2024-01-01 to 2024-01-31",
    }

    # Make request to protected endpoint without Authorization header
    response = client.post("/generate-report", json=payload)

    # Assert 401 Unauthorized response (will fail until endpoint is protected)
    assert response.status_code == 401

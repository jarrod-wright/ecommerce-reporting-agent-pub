"""Security middleware components for the API layer.

This module exports security-related middleware components for use
throughout the application, implementing the Resilient API Framework.
"""

from agent.api.middleware.request_signing import HMACSignatureMiddleware

__all__ = ["HMACSignatureMiddleware"]

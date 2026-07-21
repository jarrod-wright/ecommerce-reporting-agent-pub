"""
ERA Schema Mapper - TDG Configuration Engineering

Maps ERA requirements to TDG configuration schemas for different business types.
Generates high-fidelity eCommerce test datasets compatible with ERA's data processing pipeline.
"""

from typing import Any, Dict


class ERASchemaMapper:
    """Maps ERA requirements to TDG configuration schemas."""

    VALID_BUSINESS_TYPES = [
        "high_growth_startup",
        "stable_enterprise",
        "seasonal_business",
        "data_with_pii",
        "edge_case_scenarios"
    ]

    def __init__(self):
        """Initialize the ERA Schema Mapper."""
        pass

    def generate_shopify_profile(self, business_type: str) -> Dict[str, Any]:
        """Generate Shopify-compatible TDG configuration for specified business type.
        
        Args:
            business_type: Type of business profile to generate
            
        Returns:
            Dictionary containing Shopify profile configuration
            
        Raises:
            ValueError: If business_type is not supported
        """
        if business_type not in self.VALID_BUSINESS_TYPES:
            raise ValueError(
                f"Invalid business type: {business_type}. "
                f"Valid business types are: {', '.join(self.VALID_BUSINESS_TYPES)}"
            )

        if business_type == "high_growth_startup":
            return {
                "customers": 5000,
                "orders_per_customer": {
                    "mean": 15,
                    "std_dev": 10,
                    "min": 1,
                    "max": 100
                },
                "revenue_distribution": {
                    "type": "lognormal",
                    "mean": 200,
                    "std": 150
                },
                "growth_pattern": "exponential",
                "seasonality": "minimal"
            }

        elif business_type == "stable_enterprise":
            return {
                "customers": 50000,
                "orders_per_customer": {
                    "mean": 8,
                    "std_dev": 5,
                    "min": 1,
                    "max": 25
                },
                "revenue_distribution": {
                    "type": "normal",
                    "mean": 350,
                    "std": 100
                },
                "growth_pattern": "steady",
                "seasonality": "moderate"
            }

        elif business_type == "seasonal_business":
            return {
                "customers": 15000,
                "orders_per_customer": {
                    "mean": 12,
                    "std_dev": 8,
                    "min": 1,
                    "max": 60
                },
                "revenue_distribution": {
                    "type": "seasonal",
                    "peak_months": [11, 12],
                    "peak_multiplier": 2.5,
                    "baseline_revenue": 50000
                },
                "growth_pattern": "cyclical",
                "seasonality": "high"
            }

        elif business_type == "data_with_pii":
            return {
                "customers": 2000,
                "orders_per_customer": {
                    "mean": 10,
                    "std_dev": 6,
                    "min": 1,
                    "max": 30
                },
                "revenue_distribution": {
                    "type": "normal",
                    "mean": 150,
                    "std": 75
                },
                "growth_pattern": "moderate",
                "seasonality": "low",
                "pii_injection": {
                    "order_notes": {"rate": 0.30, "types": ["email", "phone", "ssn"]},
                    "customer_data": {"rate": 0.15, "types": ["credit_card", "address"]}
                }
            }

        elif business_type == "edge_case_scenarios":
            return {
                "customers": 1000,
                "orders_per_customer": {
                    "mean": 5,
                    "std_dev": 15,  # High variance for edge cases
                    "min": 0,       # Some customers with no orders
                    "max": 1000     # Some customers with excessive orders
                },
                "revenue_distribution": {
                    "type": "extreme",
                    "min_value": 0.01,
                    "max_value": 999999.99
                },
                "growth_pattern": "volatile",
                "seasonality": "erratic",
                "data_quality": {
                    "missing_total_price": 0.15,
                    "missing_customer": 0.10,
                    "missing_created_at": 0.05
                }
            }

    def generate_ga4_profile(self, business_type: str) -> Dict[str, Any]:
        """Generate GA4-compatible session data configuration.
        
        Args:
            business_type: Type of business profile to generate GA4 config for
            
        Returns:
            Dictionary containing GA4 profile configuration
        """
        # Base GA4 profile - can be customized per business type in future
        return {
            "daily_sessions": {
                "mean": 500,
                "std_dev": 150
            },
            "device_distribution": {
                "desktop": 0.6,
                "mobile": 0.35,
                "tablet": 0.05
            },
            "conversion_rate": 0.03,  # 3% sessions convert to orders
            "bounce_rate": 0.45
        }

"""
Business Profile Generator

Generates TDG-compatible YAML configuration files for different business scenarios.
Each profile is optimized for ERA testing with specific characteristics.
"""

from pathlib import Path

import yaml
from era_schema_mapper import ERASchemaMapper


def generate_tdg_yaml_config(business_type: str, schema_mapper: ERASchemaMapper) -> dict:
    """Generate complete TDG YAML configuration for a business type."""

    shopify_profile = schema_mapper.generate_shopify_profile(business_type)
    ga4_profile = schema_mapper.generate_ga4_profile(business_type)

    # Base configuration structure compatible with TDG
    config = {
        "profile_name": f"ERA {business_type.replace('_', ' ').title()} Testing Dataset",
        "global_settings": {
            "seed": 1337,  # Reproducible testing
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-12-31"
            }
        },
        "entities": []
    }

    # Generate customers entity
    customers_entity = {
        "entity_name": "shopify_customers",
        "count": shopify_profile["customers"],
        "field_schema": {
            "customer_id": {"provider": "uuid"},
            "first_name": {"provider": "person.first_name"},
            "last_name": {"provider": "person.last_name"},
            "email": {"provider": "person.email"},
            "phone": {"provider": "person.telephone"},
            "created_at": {"provider": "datetime.datetime", "start": 2023, "end": 2024}
        }
    }

    # Add PII fields for data_with_pii profile
    if business_type == "data_with_pii":
        customers_entity["field_schema"]["ssn"] = {"provider": "person.ssn"}
        customers_entity["field_schema"]["credit_card"] = {"provider": "payment.credit_card_number"}
        customers_entity["field_schema"]["address"] = {"provider": "address.address"}

    config["entities"].append(customers_entity)

    # Generate orders entity
    orders_per_customer = shopify_profile["orders_per_customer"]
    orders_entity = {
        "entity_name": "shopify_orders",
        "count_per_parent": {
            "parent_entity": "shopify_customers",
            "distribution": "normal",
            "mean": orders_per_customer["mean"],
            "std_dev": orders_per_customer["std_dev"],
            "min": orders_per_customer["min"],
            "max": orders_per_customer["max"]
        },
        "relationships": [
            {
                "type": "foreign_key",
                "from_entity": "shopify_customers",
                "from_field": "customer_id",
                "to_field": "customer_id"
            }
        ],
        "field_schema": {
            "id": {"provider": "uuid"},
            "order_number": {"provider": "random.randint", "a": 1000, "b": 999999},
            "created_at": {"provider": "datetime.datetime", "start": 2024, "end": 2024},
            "financial_status": {"provider": "choice", "items": ["paid", "pending", "refunded"]},
            "fulfillment_status": {"provider": "choice", "items": ["fulfilled", "unfulfilled", "shipped"]},
            "customer_id": {"provider": "placeholder"}  # Populated by relationship logic
        }
    }

    # Configure revenue distribution based on business type
    revenue_dist = shopify_profile["revenue_distribution"]
    if revenue_dist["type"] == "lognormal":
        orders_entity["field_schema"]["total_price"] = {
            "provider": "numeric.float_number",
            "distribution": {
                "type": "lognormal",
                "mean": revenue_dist["mean"],
                "std": revenue_dist["std"],
                "min": 10.0,
                "max": 2000.0
            }
        }
    elif revenue_dist["type"] == "normal":
        orders_entity["field_schema"]["total_price"] = {
            "provider": "numeric.float_number",
            "distribution": {
                "type": "normal",
                "mean": revenue_dist["mean"],
                "std": revenue_dist["std"],
                "min": 5.0,
                "max": 1000.0
            }
        }
    elif revenue_dist["type"] == "extreme":
        orders_entity["field_schema"]["total_price"] = {
            "provider": "choice",
            "items": [0.01, 999999.99, 25.00, 50.00, 100.00, 150.00],
            "weights": [0.05, 0.05, 0.3, 0.3, 0.2, 0.1]
        }
    else:
        # Default distribution
        orders_entity["field_schema"]["total_price"] = {
            "provider": "numeric.float_number",
            "distribution": {
                "type": "normal",
                "mean": 150.0,
                "std": 75.0,
                "min": 10.0,
                "max": 1000.0
            }
        }

    config["entities"].append(orders_entity)

    # Generate GA4 sessions entity
    ga4_entity = {
        "entity_name": "ga4_sessions",
        "count": int(ga4_profile["daily_sessions"]["mean"] * 30),  # ~30 days of data
        "field_schema": {
            "date": {"provider": "datetime.date", "start": 2024, "end": 2024},
            "device_category": {
                "provider": "choice",
                "items": ["desktop", "mobile", "tablet"],
                "weights": [
                    ga4_profile["device_distribution"]["desktop"],
                    ga4_profile["device_distribution"]["mobile"],
                    ga4_profile["device_distribution"]["tablet"]
                ]
            },
            "page_views": {"provider": "random.randint", "a": 1, "b": 20},
            "duration": {"provider": "random.randint", "a": 30, "b": 1800},  # 30s to 30min
            "sessions": {"provider": "choice", "items": [1]},  # Each record represents 1 session
            "users": {"provider": "choice", "items": [1]}      # Each record represents 1 user
        }
    }

    # Add data quality issues for edge case scenarios
    if business_type == "edge_case_scenarios":
        ga4_entity["field_schema"]["page_views"] = {
            "provider": "choice",
            "items": [None, 1, 1000],  # Include missing and extreme values
            "weights": [0.25, 0.70, 0.05]
        }

    config["entities"].append(ga4_entity)

    return config


def main():
    """Generate all business profile YAML files."""

    schema_mapper = ERASchemaMapper()
    profiles_dir = Path("/app/config/era_business_profiles")
    profiles_dir.mkdir(exist_ok=True)

    business_types = [
        "high_growth_startup",
        "stable_enterprise",
        "seasonal_business",
        "data_with_pii",
        "edge_case_scenarios"
    ]

    generated_files = []

    for business_type in business_types:
        try:
            # Generate configuration
            config = generate_tdg_yaml_config(business_type, schema_mapper)

            # Write YAML file
            yaml_file = profiles_dir / f"{business_type}.yaml"
            with open(yaml_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2, sort_keys=False)

            generated_files.append(str(yaml_file))
            print(f"✓ Generated {business_type}.yaml")

        except Exception as e:
            print(f"✗ Failed to generate {business_type}.yaml: {e}")

    print(f"\n✓ Successfully generated {len(generated_files)} business profile configurations")
    print(f"✓ Directory: {profiles_dir}")

    return generated_files


if __name__ == "__main__":
    main()

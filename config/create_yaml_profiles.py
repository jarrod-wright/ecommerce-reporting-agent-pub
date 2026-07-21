"""
Manual YAML Profile Generator

Creates TDG-compatible YAML files without requiring external dependencies.
"""

from pathlib import Path

from era_schema_mapper import ERASchemaMapper


def generate_yaml_content(business_type: str, schema_mapper: ERASchemaMapper) -> str:
    """Generate YAML content as string for a business profile."""

    shopify_profile = schema_mapper.generate_shopify_profile(business_type)
    ga4_profile = schema_mapper.generate_ga4_profile(business_type)

    yaml_content = f"""profile_name: "ERA {business_type.replace('_', ' ').title()} Testing Dataset"

global_settings:
  seed: 1337
  date_range:
    start: "2024-01-01"
    end: "2024-12-31"

entities:
  - entity_name: shopify_customers
    count: {shopify_profile['customers']}
    field_schema:
      customer_id:
        provider: uuid
      first_name:
        provider: person.first_name
      last_name:
        provider: person.last_name
      email:
        provider: person.email
      phone:
        provider: person.telephone
      created_at:
        provider: datetime.datetime
        start: 2023
        end: 2024"""

    if business_type == "data_with_pii":
        yaml_content += """
      ssn:
        provider: person.ssn
      credit_card:
        provider: payment.credit_card_number
      address:
        provider: address.address"""

    orders_config = shopify_profile['orders_per_customer']
    yaml_content += f"""

  - entity_name: shopify_orders
    count_per_parent:
      parent_entity: shopify_customers
      distribution: normal
      mean: {orders_config['mean']}
      std_dev: {orders_config['std_dev']}
      min: {orders_config['min']}
      max: {orders_config['max']}
    relationships:
      - type: foreign_key
        from_entity: shopify_customers
        from_field: customer_id
        to_field: customer_id
    field_schema:
      id:
        provider: uuid
      order_number:
        provider: random.randint
        a: 1000
        b: 999999
      created_at:
        provider: datetime.datetime
        start: 2024
        end: 2024"""

    # Configure total_price based on revenue distribution
    revenue_dist = shopify_profile['revenue_distribution']
    if revenue_dist['type'] == 'lognormal':
        yaml_content += f"""
      total_price:
        provider: numeric.float_number
        distribution:
          type: lognormal
          mean: {revenue_dist['mean']}
          std: {revenue_dist['std']}
          min: 10.0
          max: 2000.0"""
    elif revenue_dist['type'] == 'normal':
        yaml_content += f"""
      total_price:
        provider: numeric.float_number
        distribution:
          type: normal
          mean: {revenue_dist['mean']}
          std: {revenue_dist['std']}
          min: 5.0
          max: 1000.0"""
    elif revenue_dist['type'] == 'extreme':
        yaml_content += """
      total_price:
        provider: choice
        items: [0.01, 999999.99, 25.00, 50.00, 100.00, 150.00]
        weights: [0.05, 0.05, 0.3, 0.3, 0.2, 0.1]"""
    elif revenue_dist['type'] == 'seasonal':
        yaml_content += f"""
      total_price:
        provider: numeric.float_number
        distribution:
          type: seasonal
          baseline: {revenue_dist['baseline_revenue']}
          peak_months: {revenue_dist['peak_months']}
          peak_multiplier: {revenue_dist['peak_multiplier']}
          min: 20.0
          max: 5000.0"""

    yaml_content += """
      financial_status:
        provider: choice
        items: [paid, pending, refunded]
      fulfillment_status:
        provider: choice
        items: [fulfilled, unfulfilled, shipped]
      customer_id:
        provider: placeholder"""

    # Add GA4 sessions entity
    daily_sessions = ga4_profile['daily_sessions']['mean']
    device_dist = ga4_profile['device_distribution']

    yaml_content += f"""

  - entity_name: ga4_sessions
    count: {int(daily_sessions * 30)}
    field_schema:
      date:
        provider: datetime.date
        start: 2024
        end: 2024
      device_category:
        provider: choice
        items: [desktop, mobile, tablet]
        weights: [{device_dist['desktop']}, {device_dist['mobile']}, {device_dist['tablet']}]"""

    if business_type == "edge_case_scenarios":
        yaml_content += """
      page_views:
        provider: choice
        items: [null, 1, 1000]
        weights: [0.25, 0.70, 0.05]"""
    else:
        yaml_content += """
      page_views:
        provider: random.randint
        a: 1
        b: 20"""

    yaml_content += """
      duration:
        provider: random.randint
        a: 30
        b: 1800
      sessions:
        provider: choice
        items: [1]
      users:
        provider: choice
        items: [1]
"""

    return yaml_content


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
            # Generate YAML content
            yaml_content = generate_yaml_content(business_type, schema_mapper)

            # Write YAML file
            yaml_file = profiles_dir / f"{business_type}.yaml"
            with open(yaml_file, 'w') as f:
                f.write(yaml_content)

            generated_files.append(str(yaml_file))
            print(f"✓ Generated {business_type}.yaml ({len(yaml_content.split())} words)")

        except Exception as e:
            print(f"✗ Failed to generate {business_type}.yaml: {e}")

    print(f"\n✓ Successfully generated {len(generated_files)} business profile configurations")
    print(f"✓ Directory: {profiles_dir}")

    return generated_files


if __name__ == "__main__":
    main()

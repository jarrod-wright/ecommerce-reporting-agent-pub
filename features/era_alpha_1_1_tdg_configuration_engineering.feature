Feature: TDG Configuration Engineering for ERA Testing
  As a Test Data Architect
  I want to create comprehensive business profile configurations for TDG
  So that ERA can be tested with high-fidelity, realistic eCommerce datasets

  Background:
    Given the Test Data Generator (TDG) integration is available
    And ERA requires specific Shopify and GA4 data schemas
    And business profiles must support different eCommerce scenarios

  @configuration @business-profiles
  Scenario: Generate high growth startup business profile configuration
    Given I am creating a "high_growth_startup" business profile
    When I generate the TDG configuration
    Then the profile should specify 5000 customers
    And the orders per customer should have mean 15, std_dev 10, min 1, max 100
    And the revenue distribution should be lognormal with mean 200, std 150
    And the growth pattern should be "exponential"
    And the seasonality should be "minimal"
    And the profile should be saved to "config/era_business_profiles/high_growth_startup.yaml"

  @configuration @business-profiles
  Scenario: Generate stable enterprise business profile configuration
    Given I am creating a "stable_enterprise" business profile
    When I generate the TDG configuration
    Then the profile should specify 50000 customers
    And the orders per customer should have mean 8, std_dev 5, min 1, max 25
    And the revenue distribution should be normal with mean 350, std 100
    And the growth pattern should be "steady"
    And the seasonality should be "moderate"
    And the profile should be saved to "config/era_business_profiles/stable_enterprise.yaml"

  @configuration @business-profiles
  Scenario: Generate seasonal business profile configuration
    Given I am creating a "seasonal_business" business profile
    When I generate the TDG configuration
    Then the profile should specify 15000 customers
    And the orders per customer should have mean 12, std_dev 8, min 1, max 60
    And the revenue distribution should be seasonal with peak_months [11, 12]
    And the peak multiplier should be 2.5
    And the baseline revenue should be 50000
    And the profile should be saved to "config/era_business_profiles/seasonal_business.yaml"

  @configuration @business-profiles @pii-testing
  Scenario: Generate PII-heavy dataset profile for sanitization testing
    Given I am creating a "data_with_pii" business profile
    When I generate the TDG configuration
    Then the profile should specify 2000 customers
    And the configuration should include PII injection patterns
    And PII fields should include email, phone, ssn, credit_card, address
    And the injection rate should be 30% for order_notes
    And the injection rate should be 15% for customer_data
    And the profile should be saved to "config/era_business_profiles/data_with_pii.yaml"

  @configuration @business-profiles @edge-cases
  Scenario: Generate edge case scenarios profile for robustness testing
    Given I am creating an "edge_case_scenarios" business profile
    When I generate the TDG configuration
    Then the profile should include missing data scenarios
    And the profile should include extreme value scenarios
    And the profile should include data inconsistency scenarios
    And missing data should affect 15% of total_price fields
    And missing data should affect 10% of customer fields
    And extreme values should include 0.01 and 999999.99 for total_price
    And the profile should be saved to "config/era_business_profiles/edge_case_scenarios.yaml"

  @schema-mapping @shopify
  Scenario: Generate Shopify-compatible configuration schema
    Given I have an ERASchemaMapper instance
    When I call generate_shopify_profile with "high_growth_startup"
    Then the result should contain customer count specifications
    And the result should contain orders_per_customer distribution parameters
    And the result should contain revenue_distribution configuration
    And the result should contain growth_pattern specification
    And the result should contain seasonality specification
    And all parameters should be compatible with TDG Mimesis Schema API

  @schema-mapping @ga4
  Scenario: Generate GA4-compatible configuration schema
    Given I have an ERASchemaMapper instance
    When I call generate_ga4_profile with "high_growth_startup"
    Then the result should contain daily_sessions mean and std_dev
    And the result should contain device_distribution with desktop, mobile, tablet weights
    And the device distribution weights should sum to 1.0
    And the result should contain conversion_rate of 3%
    And the result should contain bounce_rate specification
    And all parameters should be compatible with ERA's GA4 data processing

  @validation @yaml-structure
  Scenario: Validate generated YAML configuration structure
    Given I have generated a business profile configuration
    When I parse the YAML file
    Then it should contain a valid "profile_name" field
    And it should contain "global_settings" with seed and date_range
    And it should contain an "entities" array
    And each entity should have "entity_name", count specification, and "field_schema"
    And the field_schema should use valid Mimesis provider patterns
    And the YAML should be syntactically valid and parseable

  @integration @era-compatibility
  Scenario: Validate ERA schema compatibility
    Given I have generated Shopify and GA4 profiles
    When I validate against ERA's ReportingAgentState requirements
    Then the Shopify data should include required fields: id, created_at, total_price, customer_id
    And the GA4 data should include required fields: date, device_category, page_views, duration
    And all date fields should use ISO format for created_at
    And all date fields should use YYYY-MM-DD format for GA4 dates
    And total_price should be string type for Polars compatibility
    And numeric fields should be appropriate types for Polars processing

  @performance @generation-speed
  Scenario: Validate configuration generation performance
    Given I have an ERASchemaMapper instance
    When I generate all 5 business profile configurations
    Then the total generation time should be less than 5 seconds
    And each individual profile generation should be less than 1 second
    And the generated files should be under 50KB each
    And memory usage should not exceed 100MB during generation

  @file-system @directory-structure
  Scenario: Create proper directory structure for business profiles
    Given the configuration engineering process is initiated
    When the business profiles are generated
    Then the "config/era_business_profiles/" directory should exist
    And it should contain exactly 5 YAML files
    And each file should be named according to its business type
    And each file should be readable and have appropriate permissions
    And the directory structure should be ready for TDG consumption

  @error-handling @configuration-validation
  Scenario: Handle invalid business type gracefully
    Given I have an ERASchemaMapper instance
    When I call generate_shopify_profile with an invalid business type "invalid_type"
    Then it should raise a ValueError with descriptive message
    And the error message should list valid business types
    And no partial configuration should be generated
    And the system should remain in a clean state

  @reproducibility @deterministic-generation
  Scenario: Ensure deterministic configuration generation
    Given I have an ERASchemaMapper instance
    When I generate the same business profile configuration twice
    Then both generated configurations should be identical
    And the YAML structure should be consistent
    And the parameter values should be deterministic
    And repeated calls should not introduce randomness
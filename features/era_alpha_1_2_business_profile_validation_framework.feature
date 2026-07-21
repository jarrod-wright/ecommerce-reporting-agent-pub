Feature: Business Profile Validation Framework for ERA Testing
  As a Quality Assurance Engineer
  I want to validate that TDG-generated data from business profiles meets ERA requirements
  So that I can ensure data compatibility and prevent runtime errors in ERA

  Background:
    Given the business profile YAML configurations are available
    And the TDG (Test Data Generator) is integrated and functional
    And ERA's data schema requirements are well-defined
    And the TestDataProfileValidator class is implemented

  @validation @shopify-schema
  Scenario: Validate Shopify data schema compliance for high growth startup
    Given I have a TestDataProfileValidator instance
    When I generate a dataset using "high_growth_startup" profile
    And I validate the Shopify schema compliance
    Then the generated Shopify data should contain all required fields:
      | field_name        | required |
      | id               | true     |
      | created_at       | true     |
      | total_price      | true     |
      | customer_id      | true     |
      | financial_status | true     |
      | fulfillment_status | true   |
      | order_number     | true     |
    And the total_price field should be string type for Polars compatibility
    And all created_at values should be valid ISO timestamps
    And all total_price values should be positive when converted to float
    And all customer_id values should reference existing customers

  @validation @shopify-schema
  Scenario Outline: Validate Shopify schema compliance across all business profiles
    Given I have a TestDataProfileValidator instance
    When I generate a dataset using "<business_profile>" profile
    And I validate the Shopify schema compliance
    Then the Shopify data validation should pass
    And the dataset should contain exactly "<expected_customers>" customers
    And the orders per customer should be within expected range

    Examples:
      | business_profile    | expected_customers |
      | high_growth_startup | 5000              |
      | stable_enterprise   | 50000             |
      | seasonal_business   | 15000             |
      | data_with_pii      | 2000              |
      | edge_case_scenarios | 1000              |

  @validation @ga4-schema
  Scenario: Validate GA4 session data schema compliance
    Given I have a TestDataProfileValidator instance
    When I generate a dataset using "high_growth_startup" profile
    And I validate the GA4 schema compliance
    Then the generated GA4 data should contain all required fields:
      | field_name      | required | data_type |
      | date           | true     | string    |
      | device_category | true     | string    |
      | page_views     | true     | integer   |
      | duration       | true     | integer   |
      | sessions       | true     | integer   |
      | users          | true     | integer   |
    And all date values should match YYYY-MM-DD format exactly
    And all page_views should be positive integers
    And all duration values should be positive integers (30-1800 seconds)
    And device_category should only contain: desktop, mobile, tablet

  @validation @data-types
  Scenario: Validate data type compatibility with Polars processing
    Given I have a TestDataProfileValidator instance
    When I generate a dataset using "stable_enterprise" profile
    Then the Shopify total_price field should be string type
    And the GA4 numeric fields should be integer types
    And all date fields should be parseable by pandas/polars
    And no data type conflicts should exist for ERA processing

  @validation @business-logic
  Scenario: Validate business logic constraints
    Given I have a TestDataProfileValidator instance
    When I generate a dataset using "high_growth_startup" profile
    Then all order amounts should be greater than zero
    And all order dates should be within the configured date range
    And financial_status should only contain valid values: paid, pending, refunded
    And fulfillment_status should only contain valid values: fulfilled, unfulfilled, shipped
    And customer signup dates should precede order dates

  @validation @referential-integrity
  Scenario: Validate referential integrity between customers and orders
    Given I have a TestDataProfileValidator instance
    When I generate a dataset using "seasonal_business" profile
    Then every order should reference a valid customer_id
    And no orphaned orders should exist
    And customer_id foreign key relationships should be maintained
    And the customer count should match the profile specification

  @validation @data-quality @pii-profile
  Scenario: Validate PII-heavy profile generates appropriate test data
    Given I have a TestDataProfileValidator instance
    When I generate a dataset using "data_with_pii" profile
    Then the customer data should contain PII fields: ssn, credit_card, address
    And the PII fields should contain realistic test data
    And the PII injection rate should match configuration (30% for order_notes)
    And the generated PII should be detectable by sanitization tools

  @validation @edge-cases
  Scenario: Validate edge case scenarios produce expected anomalies
    Given I have a TestDataProfileValidator instance
    When I generate a dataset using "edge_case_scenarios" profile
    Then some customers should have zero orders (edge case)
    And some orders should have extreme values (0.01 or 999999.99)
    And some data fields should be missing (15% for total_price)
    And the data should challenge ERA's robustness without breaking it

  @validation @performance
  Scenario: Validate dataset generation performance meets requirements
    Given I have a TestDataProfileValidator instance
    When I generate datasets for all business profiles
    Then each profile generation should complete within 30 seconds
    And the generated datasets should not exceed 100MB in memory
    And the validation process should complete within 60 seconds total
    And no memory leaks should occur during generation

  @validation @era-compatibility
  Scenario: Validate ERA ReportingAgentState compatibility
    Given I have a TestDataProfileValidator instance
    When I generate a dataset using "high_growth_startup" profile
    And I create a mock ERA ReportingAgentState with the data
    Then the state should accept the raw_shopify_data format
    And the state should accept the raw_ga4_data format
    And the process_data_node should process the data without errors
    And the resulting unified DataFrame should have required columns

  @validation @polars-processing
  Scenario: Validate Polars DataFrame processing compatibility
    Given I have a TestDataProfileValidator instance
    When I generate a dataset using "stable_enterprise" profile
    And I process the data through Polars operations
    Then the Shopify data should convert to Polars DataFrame successfully
    And the GA4 data should convert to Polars DataFrame successfully
    And the join operation on date field should work correctly
    And aggregation operations should produce valid results

  @validation @error-handling
  Scenario: Validate error handling for malformed profiles
    Given I have a TestDataProfileValidator instance
    When I attempt to validate a non-existent profile "invalid_profile"
    Then a clear error message should be raised
    And the error should specify available profile names
    And the system should remain in a clean state
    And no partial datasets should be generated

  @validation @file-system
  Scenario: Validate file system integration
    Given I have a TestDataProfileValidator instance
    When I validate profiles using file system paths
    Then the validator should locate YAML files correctly
    And the validator should parse YAML configurations without errors
    And the validator should handle file permission issues gracefully
    And the validator should validate file existence before processing

  @validation @concurrent-validation
  Scenario: Validate concurrent profile validation
    Given I have a TestDataProfileValidator instance
    When I validate multiple profiles concurrently
    Then each validation should complete successfully
    And no race conditions should occur
    And memory usage should remain within acceptable limits
    And the results should be deterministic and reproducible

  @integration @end-to-end
  Scenario: Complete end-to-end validation pipeline
    Given I have all business profiles configured correctly
    When I run the complete validation pipeline
    Then all 5 business profiles should pass validation
    And the generated data should be ready for ERA testing
    And performance metrics should be within acceptable ranges
    And the validation report should be comprehensive and actionable
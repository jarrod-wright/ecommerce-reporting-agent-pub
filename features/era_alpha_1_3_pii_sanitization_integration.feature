Feature: PII Sanitization Integration for ERA Testing
  As a Security Engineer
  I want to integrate TDG's PII sanitization capabilities with ERA testing workflows
  So that I can ensure complete PII removal while preserving data utility for testing

  Background:
    Given the TDG PIISanitizationPOC is available and functional
    And ERA business profiles with PII data are configured
    And the ERAPIISanitizer class is implemented
    And sanitization effectiveness must exceed 99.9% removal rate

  @pii-sanitization @integration
  Scenario: Initialize ERAPIISanitizer with TDG capabilities
    Given I am creating an ERAPIISanitizer instance
    When the sanitizer is initialized
    Then it should integrate with TDG's PIISanitizationPOC
    And it should load ERA-specific PII patterns
    And it should be ready for dataset sanitization
    And all required sanitization rules should be configured

  @pii-sanitization @shopify-data
  Scenario: Sanitize Shopify orders dataset while preserving business logic
    Given I have an ERAPIISanitizer instance
    And I have a Shopify dataset generated from "data_with_pii" profile
    When I sanitize the Shopify orders dataset
    Then all PII should be removed from customer data fields
    And all PII should be removed from order notes and descriptions
    And email addresses should be replaced with safe test emails
    And phone numbers should be masked preserving format
    And credit card numbers should be masked preserving last 4 digits
    And addresses should be replaced with generic test addresses
    And order amounts and business metrics should remain unchanged
    And referential integrity should be preserved
    And the dataset should remain usable for ERA testing

  @pii-sanitization @ga4-data
  Scenario: Sanitize GA4 sessions dataset with minimal PII risk
    Given I have an ERAPIISanitizer instance
    And I have a GA4 dataset generated from any business profile
    When I sanitize the GA4 sessions dataset
    Then any embedded PII in session data should be removed
    And device categories should remain unchanged
    And session metrics should remain unchanged
    And date information should remain unchanged
    And the dataset should remain fully functional for analytics

  @pii-sanitization @comprehensive
  Scenario: Sanitize complete ERA dataset with all data types
    Given I have an ERAPIISanitizer instance
    And I have a complete ERA dataset with Shopify and GA4 data
    And the dataset contains known PII patterns
    When I call sanitize_era_dataset with the complete dataset
    Then both Shopify and GA4 datasets should be sanitized
    And the sanitized dataset should maintain the same structure
    And all business relationships should be preserved
    And no PII should remain in any field
    And the datasets should be ready for ERA processing

  @pii-validation @effectiveness
  Scenario: Validate 99.9% PII removal effectiveness
    Given I have an ERAPIISanitizer instance
    And I have original and sanitized datasets
    When I validate the sanitization effectiveness
    Then the PII removal rate should exceed 99.9% for Shopify data
    And the PII removal rate should exceed 99.9% for GA4 data
    And the effectiveness report should provide detailed metrics
    And the report should identify any remaining PII patterns
    And the validation should use TDG's comprehensive PII detection

  @pii-patterns @detection
  Scenario Outline: Detect and sanitize specific PII types
    Given I have an ERAPIISanitizer instance
    And I have a dataset containing "<pii_type>" data
    When I sanitize the dataset
    Then all "<pii_type>" patterns should be detected
    And all "<pii_type>" instances should be sanitized using "<sanitization_method>"
    And the sanitized data should maintain "<preservation_aspect>"
    And no original "<pii_type>" data should remain

    Examples:
      | pii_type      | sanitization_method | preservation_aspect |
      | email         | replace_format     | domain structure    |
      | phone         | mask_partial       | number format       |
      | ssn           | replace            | field presence      |
      | credit_card   | mask_partial       | last 4 digits       |
      | person_name   | replace            | field structure     |
      | address       | replace            | field presence      |
      | ip_address    | replace            | format structure    |
      | date_of_birth | replace            | date format         |

  @pii-sanitization @era-specific
  Scenario: Handle ERA-specific PII patterns
    Given I have an ERAPIISanitizer instance with ERA-specific patterns loaded
    And I have a dataset with ERA-specific PII scenarios
    When I sanitize the dataset with ERA-specific rules
    Then customer IDs should be preserved (not PII)
    And order IDs should be preserved (not PII)
    And business metrics should be preserved exactly
    And temporal data should be preserved for analysis
    And device/category data should be preserved
    And only genuine PII should be sanitized

  @pii-sanitization @performance
  Scenario: Validate PII sanitization performance requirements
    Given I have an ERAPIISanitizer instance
    And I have a large dataset with 10,000+ records containing PII
    When I perform complete dataset sanitization
    Then the sanitization should complete within 60 seconds
    And memory usage should remain under 500MB during processing
    And the sanitization rate should exceed 300 records/second
    And system performance should remain stable throughout

  @pii-sanitization @data-utility
  Scenario: Preserve data utility after sanitization
    Given I have an ERAPIISanitizer instance
    And I have original business datasets with PII
    When I sanitize the complete dataset
    Then the sanitized data should maintain statistical properties
    And aggregation operations should produce meaningful results
    And join operations between tables should continue to work
    And ERA processing should produce valid insights
    And business intelligence analysis should remain accurate

  @pii-sanitization @adversarial
  Scenario: Handle adversarial PII injection scenarios
    Given I have an ERAPIISanitizer instance
    And I have a dataset with deliberately injected PII patterns
    And the PII is embedded in unexpected fields and formats
    When I sanitize the adversarial dataset
    Then even cleverly hidden PII should be detected and removed
    And obfuscated PII patterns should be identified
    And the sanitization should handle edge cases gracefully
    And the removal effectiveness should still exceed 99.9%

  @pii-sanitization @format-preservation
  Scenario: Preserve data formats required by ERA
    Given I have an ERAPIISanitizer instance
    And I have a dataset that must maintain specific formats for ERA
    When I sanitize the dataset
    Then string fields required for Polars should remain strings
    And numeric fields should maintain their numeric types
    And date fields should maintain valid date formats
    And JSON structures should remain valid JSON
    And referential keys should maintain referential integrity

  @pii-sanitization @audit-trail
  Scenario: Generate comprehensive sanitization audit trail
    Given I have an ERAPIISanitizer instance
    When I sanitize a complete ERA dataset
    Then a detailed sanitization report should be generated
    And the report should specify which fields were sanitized
    And the report should show PII detection counts by type
    And the report should show removal effectiveness metrics
    And the report should include validation results
    And the report should be suitable for compliance auditing

  @integration @end-to-end
  Scenario: Complete PII sanitization integration workflow
    Given I have all ERA business profiles configured
    And the ERAPIISanitizer is fully integrated
    When I process the complete PII sanitization workflow
    Then each business profile should be sanitized successfully
    And all PII should be removed while preserving business logic
    And effectiveness validation should pass for all profiles
    And the sanitized data should be ready for ERA testing
    And the integration should be production-ready

  @error-handling @pii-sanitization
  Scenario: Handle sanitization errors gracefully
    Given I have an ERAPIISanitizer instance
    When sanitization encounters malformed data or unexpected patterns
    Then clear error messages should be provided
    And partial sanitization should not corrupt datasets
    And the system should recover from errors gracefully
    And fallback sanitization strategies should be applied
    And error details should be logged for investigation

  @pii-sanitization @validation-reporting
  Scenario: Generate detailed validation reports
    Given I have completed PII sanitization on multiple datasets
    When I generate the effectiveness validation report
    Then the report should show removal rates for each PII type
    And the report should identify any validation failures
    And the report should provide recommendations for improvement
    And the report should include statistical confidence metrics
    And the report should be actionable for security compliance
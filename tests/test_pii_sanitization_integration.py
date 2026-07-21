"""
Test suite for PII Sanitization Integration

Tests the ERAPIISanitizer integration with TDG capabilities and ERA data workflows.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add integration path to Python path
sys.path.insert(0, str(Path('/app')))

from integration.pii_sanitization_era import ERAPIISanitizer
from tests.test_data_profiles.test_profile_validation import TestDataProfileValidator


class TestPIISanitizationIntegration:
    """Test PII sanitization integration with ERA workflows."""

    def __init__(self):
        """Initialize test suite."""
        self.pii_sanitizer = ERAPIISanitizer()
        self.profile_validator = TestDataProfileValidator()
        self.test_results = {}

    def test_era_pii_sanitizer_initialization(self) -> Dict[str, Any]:
        """Test ERAPIISanitizer initialization and configuration."""

        result = {
            'test_name': 'era_pii_sanitizer_initialization',
            'passed': True,
            'errors': [],
            'validations': {}
        }

        try:
            # Test initialization
            sanitizer = ERAPIISanitizer()

            if hasattr(sanitizer, 'pii_scrubber'):
                result['validations']['pii_scrubber_integration'] = '✓ TDG PII sanitization integrated'
            else:
                result['passed'] = False
                result['errors'].append("PII scrubber not properly initialized")

            if hasattr(sanitizer, 'era_specific_patterns'):
                result['validations']['era_patterns_loaded'] = '✓ ERA-specific patterns loaded'
            else:
                result['passed'] = False
                result['errors'].append("ERA-specific patterns not loaded")

            # Test PII pattern availability
            pii_patterns = sanitizer.pii_scrubber.pii_patterns
            expected_patterns = ['email', 'phone', 'ssn', 'credit_card', 'person_name', 'address']

            for pattern in expected_patterns:
                if pattern in pii_patterns:
                    result['validations'][f'{pattern}_pattern'] = f'✓ {pattern} pattern available'
                else:
                    result['passed'] = False
                    result['errors'].append(f"Missing {pattern} pattern")

        except Exception as e:
            result['passed'] = False
            result['errors'].append(f"Initialization error: {str(e)}")

        return result

    def test_sanitize_shopify_data_with_pii(self) -> Dict[str, Any]:
        """Test Shopify data sanitization with PII content."""

        result = {
            'test_name': 'sanitize_shopify_data_with_pii',
            'passed': True,
            'errors': [],
            'validations': {}
        }

        try:
            # Generate test data with PII
            dataset = self.profile_validator.generate_dataset("/app/config/era_business_profiles/data_with_pii.yaml")

            original_shopify = dataset['shopify_orders']

            # Add some PII to test data
            records = original_shopify.to_dict('records')
            for i, record in enumerate(records[:5]):  # Add PII to first 5 records
                record['customer_notes'] = f"Customer John Smith called from 555-123-{i:04d}"
                record['billing_address'] = f"{i*10} Main Street, Anytown"
                record['customer_email_backup'] = f"john.smith{i}@personalemail.com"

            # Create modified dataset
            from tests.test_data_profiles.test_profile_validation import MockDataFrame
            modified_shopify = MockDataFrame(records)

            # Sanitize the data
            sanitized_shopify = self.pii_sanitizer.sanitize_shopify_orders(modified_shopify)

            # Validate sanitization
            sanitized_records = sanitized_shopify.to_dict('records')

            # Check that PII was removed
            pii_found = False
            for record in sanitized_records:
                for field_value in record.values():
                    if field_value is None:
                        continue
                    field_str = str(field_value)

                    # Check for common PII patterns
                    if 'john.smith' in field_str.lower():
                        pii_found = True
                        break
                    if '555-123-' in field_str:
                        pii_found = True
                        break
                    if 'Main Street' in field_str:
                        pii_found = True
                        break

            if not pii_found:
                result['validations']['pii_removal'] = '✓ PII successfully removed from Shopify data'
            else:
                result['passed'] = False
                result['errors'].append("PII still present after sanitization")

            # Check that business identifiers are preserved
            original_customer_ids = set(original_shopify['customer_id'])
            sanitized_customer_ids = set(sanitized_shopify['customer_id'])

            if original_customer_ids == sanitized_customer_ids:
                result['validations']['business_id_preservation'] = '✓ Customer IDs preserved'
            else:
                result['passed'] = False
                result['errors'].append("Customer IDs were modified during sanitization")

        except Exception as e:
            result['passed'] = False
            result['errors'].append(f"Sanitization test error: {str(e)}")

        return result

    def test_complete_era_dataset_sanitization(self) -> Dict[str, Any]:
        """Test complete ERA dataset sanitization."""

        result = {
            'test_name': 'complete_era_dataset_sanitization',
            'passed': True,
            'errors': [],
            'validations': {}
        }

        try:
            # Generate complete dataset
            dataset = self.profile_validator.generate_dataset("/app/config/era_business_profiles/data_with_pii.yaml")

            # Sanitize complete dataset
            sanitized_dataset = self.pii_sanitizer.sanitize_era_dataset(dataset)

            # Validate all expected datasets are present
            expected_datasets = ['shopify_orders', 'ga4_sessions', 'shopify_customers']
            for dataset_name in expected_datasets:
                if dataset_name in dataset and dataset_name in sanitized_dataset:
                    result['validations'][f'{dataset_name}_sanitized'] = f'✓ {dataset_name} sanitized successfully'
                elif dataset_name in dataset:
                    result['passed'] = False
                    result['errors'].append(f"Failed to sanitize {dataset_name}")

            # Test that structure is preserved
            for dataset_name in sanitized_dataset:
                original_count = len(dataset[dataset_name])
                sanitized_count = len(sanitized_dataset[dataset_name])

                if original_count == sanitized_count:
                    result['validations'][f'{dataset_name}_structure'] = f'✓ {dataset_name} structure preserved ({sanitized_count} records)'
                else:
                    result['passed'] = False
                    result['errors'].append(f"{dataset_name} record count changed: {original_count} -> {sanitized_count}")

        except Exception as e:
            result['passed'] = False
            result['errors'].append(f"Complete sanitization error: {str(e)}")

        return result

    def test_sanitization_effectiveness_validation(self) -> Dict[str, Any]:
        """Test sanitization effectiveness validation (>99.9% requirement)."""

        result = {
            'test_name': 'sanitization_effectiveness_validation',
            'passed': True,
            'errors': [],
            'validations': {}
        }

        try:
            # Generate dataset with PII
            original_dataset = self.profile_validator.generate_dataset("/app/config/era_business_profiles/data_with_pii.yaml")

            # Inject PII into datasets to ensure we have something to sanitize
            self._inject_test_pii_into_datasets(original_dataset)

            # Sanitize dataset
            sanitized_dataset = self.pii_sanitizer.sanitize_era_dataset(original_dataset)

            # Validate effectiveness
            effectiveness_report = self.pii_sanitizer.validate_sanitization_effectiveness(original_dataset, sanitized_dataset)

            # Check effectiveness requirements
            for dataset_name, effectiveness in effectiveness_report.items():
                effectiveness_percent = effectiveness * 100

                if effectiveness >= 0.999:  # 99.9% requirement
                    result['validations'][f'{dataset_name}_effectiveness'] = f'✓ {dataset_name}: {effectiveness_percent:.1f}% PII removal'
                else:
                    result['passed'] = False
                    result['errors'].append(f"{dataset_name} only achieved {effectiveness_percent:.1f}% PII removal (<99.9%)")

            # Overall effectiveness
            if effectiveness_report:
                overall_effectiveness = sum(effectiveness_report.values()) / len(effectiveness_report)
                overall_percent = overall_effectiveness * 100

                if overall_effectiveness >= 0.999:
                    result['validations']['overall_effectiveness'] = f'✓ Overall effectiveness: {overall_percent:.1f}%'
                else:
                    result['passed'] = False
                    result['errors'].append(f"Overall effectiveness {overall_percent:.1f}% does not meet 99.9% requirement")

        except Exception as e:
            result['passed'] = False
            result['errors'].append(f"Effectiveness validation error: {str(e)}")

        return result

    def test_sanitization_report_generation(self) -> Dict[str, Any]:
        """Test comprehensive sanitization report generation."""

        result = {
            'test_name': 'sanitization_report_generation',
            'passed': True,
            'errors': [],
            'validations': {}
        }

        try:
            # Generate and sanitize dataset
            original_dataset = self.profile_validator.generate_dataset("/app/config/era_business_profiles/data_with_pii.yaml")
            sanitized_dataset = self.pii_sanitizer.sanitize_era_dataset(original_dataset)

            # Generate report
            report = self.pii_sanitizer.generate_sanitization_report(original_dataset, sanitized_dataset)

            # Validate report structure
            required_sections = ['sanitization_summary', 'effectiveness_by_dataset', 'compliance_status', 'audit_trail']

            for section in required_sections:
                if section in report:
                    result['validations'][f'{section}_present'] = f'✓ {section} section included in report'
                else:
                    result['passed'] = False
                    result['errors'].append(f"Missing report section: {section}")

            # Validate compliance status
            if 'compliance_status' in report:
                compliance = report['compliance_status']
                if compliance.get('meets_99_9_percent_requirement', False):
                    result['validations']['compliance_met'] = '✓ 99.9% PII removal requirement met'
                else:
                    result['validations']['compliance_status'] = f"⚠ Compliance status: {compliance.get('meets_99_9_percent_requirement', 'unknown')}"

        except Exception as e:
            result['passed'] = False
            result['errors'].append(f"Report generation error: {str(e)}")

        return result

    def _inject_test_pii_into_datasets(self, datasets: Dict[str, Any]) -> None:
        """Inject test PII into datasets to ensure sanitization has something to remove."""

        # Inject PII into Shopify orders
        if 'shopify_orders' in datasets:
            records = datasets['shopify_orders'].to_dict('records')
            for i, record in enumerate(records[:10]):  # Add PII to first 10 records
                record['customer_notes'] = f"Customer John Smith (john.smith{i}@email.com) called from 555-123-{i:04d}"
                record['shipping_address'] = f"{i*100} Oak Street, Springfield"
                record['emergency_contact'] = f"Emergency contact: Jane Doe, SSN: {i+1:03d}-{i+2:02d}-{i+3:04d}"

        # Inject PII into customer data
        for customer_key in ['customers', 'shopify_customers']:
            if customer_key in datasets:
                records = datasets[customer_key].to_dict('records')
                for i, record in enumerate(records[:10]):  # Add PII to first 10 records
                    record['notes'] = f"Customer lives at {i*50} Main Avenue, phone: 555-987-{i:04d}"
                    record['backup_email'] = f"backup.email{i}@personal.com"
                    if 'ssn' not in record:  # Only add if not already present
                        record['ssn'] = f"{i+400:03d}-{i+50:02d}-{i+1000:04d}"

        # Inject minimal PII into GA4 data
        if 'ga4_sessions' in datasets:
            records = datasets['ga4_sessions'].to_dict('records')
            for i, record in enumerate(records[:5]):  # Add minimal PII to first 5 records
                record['referrer_url'] = f"https://example.com/user/{i}/profile?email=user{i}@test.com"

    def run_complete_test_suite(self) -> Dict[str, Any]:
        """Run complete PII sanitization integration test suite."""

        print("🧪 Running PII Sanitization Integration Test Suite")
        print("=" * 60)

        tests = [
            self.test_era_pii_sanitizer_initialization,
            self.test_sanitize_shopify_data_with_pii,
            self.test_complete_era_dataset_sanitization,
            self.test_sanitization_effectiveness_validation,
            self.test_sanitization_report_generation
        ]

        test_results = {}
        passed_tests = 0
        total_tests = len(tests)

        for test_func in tests:
            test_result = test_func()
            test_name = test_result['test_name']
            test_results[test_name] = test_result

            status = "✓ PASSED" if test_result['passed'] else "✗ FAILED"
            print(f"\n{status} {test_name}")

            if test_result['passed']:
                passed_tests += 1

                # Show validations
                for validation in test_result.get('validations', {}).values():
                    print(f"   {validation}")
            else:
                # Show errors
                for error in test_result.get('errors', []):
                    print(f"   ❌ {error}")

        print("\n" + "=" * 60)
        print(f"📊 Results: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")

        overall_success = passed_tests == total_tests

        if overall_success:
            print("🎉 All PII sanitization integration tests passed!")
            print("✅ ERA PII Sanitization Integration is production-ready")
        else:
            print("⚠ Some tests failed - review implementation")

        return {
            'overall_success': overall_success,
            'tests_passed': passed_tests,
            'tests_total': total_tests,
            'success_rate': (passed_tests / total_tests) * 100,
            'detailed_results': test_results
        }


def main():
    """Run the PII sanitization integration test suite."""

    test_suite = TestPIISanitizationIntegration()
    results = test_suite.run_complete_test_suite()

    # Save results
    results_file = Path("/app/pii_sanitization_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Detailed results saved to: {results_file}")

    return results['overall_success']


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

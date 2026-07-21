"""
Comprehensive Business Profile Validation Suite

Integrates all validation components for complete ERA compatibility testing.
"""

import json
from pathlib import Path
from typing import Any, Dict

from .era_compatibility_validator import ERACompatibilityValidator
from .test_profile_validation import TestDataProfileValidator


class ComprehensiveProfileValidator:
    """Master validator combining all validation capabilities."""

    def __init__(self):
        """Initialize comprehensive validator."""
        self.profile_validator = TestDataProfileValidator()
        self.era_compatibility_validator = ERACompatibilityValidator()
        self.profiles_dir = Path("/app/config/era_business_profiles")

    def run_complete_validation_suite(self) -> Dict[str, Any]:
        """Run complete validation suite on all business profiles."""

        business_profiles = [
            'high_growth_startup',
            'stable_enterprise',
            'seasonal_business',
            'data_with_pii',
            'edge_case_scenarios'
        ]

        results = {
            'test_suite': 'comprehensive_profile_validation',
            'profiles_tested': len(business_profiles),
            'profiles': {},
            'summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'profiles_passed': 0,
                'profiles_failed': 0
            }
        }

        for profile_name in business_profiles:
            profile_results = self._validate_single_profile(profile_name)
            results['profiles'][profile_name] = profile_results

            # Update summary
            total_tests = len([test for test in profile_results['tests'].values()])
            passed_tests = len([test for test in profile_results['tests'].values() if test.get('passed', False)])

            results['summary']['total_tests'] += total_tests
            results['summary']['passed_tests'] += passed_tests
            results['summary']['failed_tests'] += (total_tests - passed_tests)

            if profile_results['overall_passed']:
                results['summary']['profiles_passed'] += 1
            else:
                results['summary']['profiles_failed'] += 1

        return results

    def _validate_single_profile(self, profile_name: str) -> Dict[str, Any]:
        """Run complete validation on a single profile."""

        results = {
            'profile_name': profile_name,
            'tests': {},
            'overall_passed': True,
            'error_count': 0,
            'validation_count': 0
        }

        try:
            # Generate dataset for testing
            profile_path = self.profiles_dir / f"{profile_name}.yaml"
            dataset = self.profile_validator.generate_dataset(str(profile_path))

            # Test 1: Shopify Schema Compliance
            shopify_test = self.profile_validator.test_shopify_schema_compliance(profile_name)
            results['tests']['shopify_schema'] = shopify_test
            if not shopify_test['passed']:
                results['overall_passed'] = False
            results['error_count'] += len(shopify_test.get('errors', []))
            results['validation_count'] += len(shopify_test.get('validations', {}))

            # Test 2: GA4 Schema Compliance
            ga4_test = self.profile_validator.test_ga4_schema_compliance(profile_name)
            results['tests']['ga4_schema'] = ga4_test
            if not ga4_test['passed']:
                results['overall_passed'] = False
            results['error_count'] += len(ga4_test.get('errors', []))
            results['validation_count'] += len(ga4_test.get('validations', {}))

            # Test 3: ERA State Compatibility
            era_compat_test = self.era_compatibility_validator.test_era_state_compatibility(dataset)
            results['tests']['era_compatibility'] = era_compat_test
            if not era_compat_test['passed']:
                results['overall_passed'] = False
            results['error_count'] += len(era_compat_test.get('errors', []))
            results['validation_count'] += len(era_compat_test.get('validations', {}))

            # Test 4: Performance Requirements
            performance_test = self.era_compatibility_validator.test_performance_requirements(dataset)
            results['tests']['performance'] = performance_test
            if not performance_test['passed']:
                results['overall_passed'] = False
            results['error_count'] += len(performance_test.get('errors', []))
            results['validation_count'] += len(performance_test.get('validations', {}))

            # Test 5: Data Quality Metrics
            quality_test = self.era_compatibility_validator.test_data_quality_metrics(dataset)
            results['tests']['data_quality'] = quality_test
            if not quality_test['passed']:
                results['overall_passed'] = False
            results['error_count'] += len(quality_test.get('errors', []))
            results['validation_count'] += len(quality_test.get('validations', {}))

        except Exception as e:
            results['overall_passed'] = False
            results['error_count'] += 1
            results['tests']['critical_error'] = {
                'test_name': 'critical_error',
                'passed': False,
                'errors': [f"Critical validation error: {str(e)}"],
                'validations': {}
            }

        return results

    def generate_validation_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive validation report."""

        report_lines = [
            "=" * 80,
            "🧪 COMPREHENSIVE BUSINESS PROFILE VALIDATION REPORT",
            "=" * 80,
            "",
            "📊 Summary:",
            f"   Profiles Tested: {results['profiles_tested']}",
            f"   Profiles Passed: {results['summary']['profiles_passed']}",
            f"   Profiles Failed: {results['summary']['profiles_failed']}",
            f"   Total Tests: {results['summary']['total_tests']}",
            f"   Tests Passed: {results['summary']['passed_tests']}",
            f"   Tests Failed: {results['summary']['failed_tests']}",
            f"   Success Rate: {(results['summary']['passed_tests'] / results['summary']['total_tests']) * 100:.1f}%" if results['summary']['total_tests'] > 0 else "N/A",
            "",
            "📋 Detailed Results:",
            ""
        ]

        for profile_name, profile_result in results['profiles'].items():
            status = "✅ PASSED" if profile_result['overall_passed'] else "❌ FAILED"
            report_lines.extend([
                f"🔍 {profile_name.upper()}: {status}",
                f"   Errors: {profile_result['error_count']}, Validations: {profile_result['validation_count']}",
                ""
            ])

            for test_name, test_result in profile_result['tests'].items():
                test_status = "✓" if test_result.get('passed', False) else "✗"
                report_lines.append(f"   {test_status} {test_name}")

                # Show errors
                for error in test_result.get('errors', []):
                    report_lines.append(f"     ⚠ {error}")

                # Show validations (abbreviated)
                validation_count = len(test_result.get('validations', {}))
                if validation_count > 0:
                    report_lines.append(f"     ✓ {validation_count} validations passed")

            report_lines.append("")

        report_lines.extend([
            "=" * 80,
            "🎯 VALIDATION COMPLETE",
            f"Overall Status: {'✅ ALL PROFILES VALIDATED' if results['summary']['profiles_failed'] == 0 else '❌ VALIDATION ISSUES DETECTED'}",
            "=" * 80
        ])

        return "\n".join(report_lines)


def main():
    """Run comprehensive validation suite."""

    validator = ComprehensiveProfileValidator()

    print("🚀 Starting Comprehensive Profile Validation Suite...")

    # Run complete validation
    results = validator.run_complete_validation_suite()

    # Generate and display report
    report = validator.generate_validation_report(results)
    print(report)

    # Save results to file
    results_file = Path("/app/validation_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Detailed results saved to: {results_file}")

    # Return success/failure
    return results['summary']['profiles_failed'] == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

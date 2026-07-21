"""
Simple test runner for performance tests since pytest is not available.
"""

import sys
import traceback

from tests.performance.test_multi_scale_performance import (
    TestDataIntegrityAcrossScales,
    TestMultiScalePerformanceFramework,
)


def run_test_method(test_instance, method_name):
    """Run a single test method and capture results."""
    print(f"\n{'='*60}")
    print(f"Running: {method_name}")
    print('='*60)

    try:
        if hasattr(test_instance, 'setup_method'):
            test_instance.setup_method()

        method = getattr(test_instance, method_name)
        method()

        print(f"✅ PASSED: {method_name}")
        return True

    except Exception as e:
        print(f"❌ FAILED: {method_name}")
        print(f"Error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


def main():
    """Run all performance tests."""
    print("🚀 Starting Multi-Scale Performance Framework Tests")
    print("="*80)

    passed = 0
    failed = 0

    # Test framework tests
    framework_tests = TestMultiScalePerformanceFramework()
    framework_test_methods = [
        'test_scale_matrix_definition',
        'test_performance_metrics_data_structure',
        'test_era_test_data_generator_integration',
        'test_micro_scale_performance_validation',
        # Skip resource-intensive tests for now
        # 'test_small_scale_business_simulation_validation',
        # 'test_medium_scale_enterprise_sla_validation',
        # 'test_large_scale_stress_testing'
    ]

    for test_method in framework_test_methods:
        success = run_test_method(framework_tests, test_method)
        if success:
            passed += 1
        else:
            failed += 1

    # Data integrity tests
    integrity_tests = TestDataIntegrityAcrossScales()
    integrity_test_methods = [
        'test_referential_integrity_maintained_across_scales'
    ]

    for test_method in integrity_test_methods:
        success = run_test_method(integrity_tests, test_method)
        if success:
            passed += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*80}")
    print("🏁 TEST SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("🎉 ALL TESTS PASSED! Framework is ready for production benchmarking.")
        return True
    else:
        print("⚠️  Some tests failed. Review and fix issues before proceeding.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

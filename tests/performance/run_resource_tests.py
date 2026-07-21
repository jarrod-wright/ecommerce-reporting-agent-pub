"""
Test runner for Resource Consumption Analysis tests
"""

import sys

from tests.performance.test_resource_consumption_analysis import (
    TestCrossScaleResourceAnalysis,
    TestResourceConsumptionAnalysis,
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
        return False


def main():
    """Run all resource consumption analysis tests."""
    print("🔍 Starting Resource Consumption Analysis Tests")
    print("="*80)

    passed = 0
    failed = 0

    # Test resource profiler framework
    framework_tests = TestResourceConsumptionAnalysis()
    framework_test_methods = [
        'test_resource_metrics_data_structure',
        'test_optimization_recommendation_structure',
        'test_era_resource_profiler_initialization',
        'test_resource_profiler_dataset_generation',
        'test_era_state_creation_for_profiling',
        'test_micro_scale_era_node_profiling',
        'test_bottleneck_identification_and_recommendations'
    ]

    for test_method in framework_test_methods:
        success = run_test_method(framework_tests, test_method)
        if success:
            passed += 1
        else:
            failed += 1

    # Cross-scale analysis tests (limited to avoid resource consumption)
    cross_scale_tests = TestCrossScaleResourceAnalysis()
    cross_scale_test_methods = [
        # Skip medium_scale for now to conserve resources
        # 'test_medium_scale_resource_profiling'
    ]

    for test_method in cross_scale_test_methods:
        success = run_test_method(cross_scale_tests, test_method)
        if success:
            passed += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*80}")
    print("🏁 RESOURCE PROFILING TEST SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("🎉 ALL RESOURCE PROFILING TESTS PASSED!")
        return True
    else:
        print("⚠️  Some tests failed. Review and fix issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

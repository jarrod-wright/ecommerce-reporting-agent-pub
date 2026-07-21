"""
Test runner for Concurrent Load Simulation tests
"""

import asyncio
import sys

from tests.performance.test_concurrent_load_simulation import (
    TestConcurrentLoadSimulation,
    TestStressTesting,
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

        # Handle async test methods
        if asyncio.iscoroutinefunction(method):
            asyncio.run(method())
        else:
            method()

        print(f"✅ PASSED: {method_name}")
        return True

    except Exception as e:
        print(f"❌ FAILED: {method_name}")
        print(f"Error: {str(e)}")
        return False


def main():
    """Run all concurrent load simulation tests."""
    print("🔄 Starting Concurrent Load Simulation Tests")
    print("="*80)

    passed = 0
    failed = 0

    # Test concurrent load simulation framework
    concurrent_tests = TestConcurrentLoadSimulation()
    concurrent_test_methods = [
        'test_concurrent_load_results_structure',
        'test_concurrent_load_simulator_initialization',
        'test_concurrent_dataset_generation',
        'test_basic_concurrent_load_simulation',
        'test_async_era_workflow_execution',
        'test_resource_contention_detection'
    ]

    for test_method in concurrent_test_methods:
        success = run_test_method(concurrent_tests, test_method)
        if success:
            passed += 1
        else:
            failed += 1

    # Stress testing tests (limited for resource conservation)
    stress_tests = TestStressTesting()
    stress_test_methods = [
        'test_stress_testing_configuration'
    ]

    for test_method in stress_test_methods:
        success = run_test_method(stress_tests, test_method)
        if success:
            passed += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*80}")
    print("🏁 CONCURRENT LOAD SIMULATION TEST SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("🎉 ALL CONCURRENT LOAD TESTS PASSED!")
        return True
    else:
        print("⚠️  Some tests failed. Review and fix issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
Simple test runner for Adversarial Data Generation Framework
Tests the core adversarial attack scenarios without external dependencies
"""

import sys
import traceback

sys.path.append('/app')

from tests.performance.adversarial_data_generator import AdversarialDataGenerator


def run_test(test_name, test_func):
    """Run a single test and capture results."""
    print(f"\n{'='*60}")
    print(f"🎯 Running: {test_name}")
    print('='*60)

    try:
        test_func()
        print(f"✅ PASSED: {test_name}")
        return True

    except Exception as e:
        print(f"❌ FAILED: {test_name}")
        print(f"Error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        return False


def test_adversarial_generator_initialization():
    """Test that AdversarialDataGenerator initializes correctly."""
    generator = AdversarialDataGenerator()

    assert hasattr(generator, 'adversarial_configs')
    assert hasattr(generator, 'tdg')
    assert hasattr(generator, 'attack_profiles')

    expected_scenarios = [
        "missing_data_scenarios",
        "extreme_value_scenarios",
        "data_inconsistency_scenarios",
        "pii_injection_scenarios"
    ]

    for scenario in expected_scenarios:
        assert scenario in generator.adversarial_configs, f"Missing scenario: {scenario}"


def test_missing_data_injection_attack():
    """Test missing data injection attack - Systematic null poisoning."""
    generator = AdversarialDataGenerator()

    # Generate adversarial dataset with missing data patterns
    adversarial_dataset = generator.generate_adversarial_dataset("missing_data_scenarios")

    assert 'shopify_orders' in adversarial_dataset
    assert 'ga4_sessions' in adversarial_dataset

    shopify_orders = adversarial_dataset['shopify_orders']

    # Check that we have data
    assert len(shopify_orders) > 0, "Should have generated orders"

    # Check for missing data injection
    if 'total_price' in shopify_orders.columns:
        total_price_nulls = shopify_orders['total_price'].isnull().sum()
        expected_nulls = int(len(shopify_orders) * 0.15)  # 15% null injection

        print(f"📊 Generated {len(shopify_orders)} orders")
        print(f"📊 Expected ~{expected_nulls} null prices, found {total_price_nulls}")

        # Allow for some variance in random injection
        assert total_price_nulls > 0, "Should have some missing prices"
        assert total_price_nulls <= len(shopify_orders) * 0.20, "Too many missing prices"


def test_extreme_value_injection_attack():
    """Test extreme value injection attack - Statistical boundary testing."""
    generator = AdversarialDataGenerator()

    # Generate adversarial dataset with extreme values
    adversarial_dataset = generator.generate_adversarial_dataset("extreme_value_scenarios")

    shopify_orders = adversarial_dataset['shopify_orders']
    assert len(shopify_orders) > 0, "Should have generated orders"

    if 'total_price' in shopify_orders.columns:
        prices = shopify_orders['total_price'].dropna()

        print(f"📊 Price range: ${prices.min():.2f} - ${prices.max():.2f}")

        # Check for extreme values
        extreme_low_count = (prices <= 1.0).sum()
        extreme_high_count = (prices >= 50000.0).sum()

        print(f"📊 Extreme low prices (≤$1.00): {extreme_low_count}")
        print(f"📊 Extreme high prices (≥$50,000): {extreme_high_count}")

        assert extreme_low_count > 0 or extreme_high_count > 0, "Should have extreme values"


def test_data_inconsistency_injection_attack():
    """Test data inconsistency injection attack - Logical corruption patterns."""
    generator = AdversarialDataGenerator()

    # Generate adversarial dataset with inconsistencies
    adversarial_dataset = generator.generate_adversarial_dataset("data_inconsistency_scenarios")

    shopify_orders = adversarial_dataset['shopify_orders']
    assert len(shopify_orders) > 0, "Should have generated orders"

    # Check for zero-value completed orders
    if 'total_price' in shopify_orders.columns and 'fulfillment_status' in shopify_orders.columns:
        zero_value_fulfilled = shopify_orders[
            (shopify_orders['total_price'] == 0) &
            (shopify_orders['fulfillment_status'] == 'fulfilled')
        ]
        print(f"📊 Zero-value fulfilled orders: {len(zero_value_fulfilled)}")
        assert len(zero_value_fulfilled) > 0, "Should have zero-value fulfilled orders"

    # Check for malformed email addresses
    if 'customer_email' in shopify_orders.columns:
        malformed_emails = shopify_orders[
            ~shopify_orders['customer_email'].str.contains('@', na=False)
        ]
        print(f"📊 Malformed email addresses: {len(malformed_emails)}")
        assert len(malformed_emails) > 0, "Should have malformed email addresses"


def test_pii_injection_attack():
    """Test PII injection attack - Privacy sanitization stress testing."""
    generator = AdversarialDataGenerator()

    # Generate adversarial dataset with PII injection
    adversarial_dataset = generator.generate_adversarial_dataset("pii_injection_scenarios")

    shopify_orders = adversarial_dataset['shopify_orders']
    assert len(shopify_orders) > 0, "Should have generated orders"

    # Check for email injection in order notes
    if 'order_notes' in shopify_orders.columns:
        email_pattern_count = shopify_orders['order_notes'].str.contains(
            r'@', na=False
        ).sum()
        print(f"📊 Records with email patterns: {email_pattern_count}")
        assert email_pattern_count > 0, "Should have email patterns injected"


def test_combined_attack_scenarios():
    """Test multi-vector adversarial attack - Combined hostile patterns."""
    generator = AdversarialDataGenerator()

    # Generate adversarial dataset with combined attacks
    adversarial_dataset = generator.generate_adversarial_dataset("combined_attack_scenarios")

    shopify_orders = adversarial_dataset['shopify_orders']
    assert len(shopify_orders) > 0, "Should have generated orders"

    # Should have missing data
    missing_data_count = shopify_orders.isnull().sum().sum()
    print(f"📊 Total missing data points: {missing_data_count}")
    assert missing_data_count > 0, "Should have missing data"

    # Should have some form of corruption
    total_records = len(shopify_orders)
    print(f"📊 Total records generated: {total_records}")
    assert total_records > 0, "Should have generated records"


def test_edge_case_scenarios():
    """Test edge case boundary attacks."""
    generator = AdversarialDataGenerator()

    # Test empty dataset scenario
    empty_dataset = generator.generate_adversarial_dataset("empty_dataset_scenarios")
    assert len(empty_dataset['shopify_orders']) == 0, "Empty dataset should have no orders"
    assert len(empty_dataset['ga4_sessions']) == 0, "Empty dataset should have no sessions"
    print("✅ Empty dataset scenario validated")

    # Test single entity scenario
    single_entity_dataset = generator.generate_adversarial_dataset("single_entity_scenarios")
    assert len(single_entity_dataset['shopify_orders']) <= 5, "Single entity should have minimal orders"
    print("✅ Single entity scenario validated")


def test_adversarial_result_generation():
    """Test adversarial result analysis generation."""
    generator = AdversarialDataGenerator()

    # Generate dataset and result
    dataset = generator.generate_adversarial_dataset("missing_data_scenarios")
    result = generator.generate_adversarial_result("missing_data_scenarios", dataset)

    assert hasattr(result, 'scenario_name')
    assert hasattr(result, 'dataset_size')
    assert hasattr(result, 'corruption_metrics')
    assert hasattr(result, 'attack_success_rate')
    assert hasattr(result, 'adversarial_metadata')

    print(f"📊 Adversarial Result: {result.scenario_name}")
    print(f"📊 Dataset Size: {result.dataset_size}")
    print(f"📊 Attack Success Rate: {result.attack_success_rate:.2f}")


def main():
    """Run all adversarial data generation tests."""
    print("🔄 ERA Adversarial Data Generation Framework Tests")
    print("=" * 80)

    tests = [
        ("Adversarial Generator Initialization", test_adversarial_generator_initialization),
        ("Missing Data Injection Attack", test_missing_data_injection_attack),
        ("Extreme Value Injection Attack", test_extreme_value_injection_attack),
        ("Data Inconsistency Injection Attack", test_data_inconsistency_injection_attack),
        ("PII Injection Attack", test_pii_injection_attack),
        ("Combined Attack Scenarios", test_combined_attack_scenarios),
        ("Edge Case Scenarios", test_edge_case_scenarios),
        ("Adversarial Result Generation", test_adversarial_result_generation)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        success = run_test(test_name, test_func)
        if success:
            passed += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*80}")
    print("🏁 ADVERSARIAL DATA GENERATION TEST SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("🎉 ALL ADVERSARIAL TESTS PASSED! TDD GREEN PHASE ACHIEVED!")
        print("🛡️  ERA system ready for adversarial attack simulation")
        return True
    else:
        print("⚠️  Some tests failed. Review and fix issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
Demonstration of ERA Adversarial Data Generation Framework

This script showcases the adversarial attack capabilities developed for Sprint 3
system hardening and resilience testing.
"""

import sys

sys.path.append('/app')


from tests.performance.adversarial_data_generator import AdversarialDataGenerator


def demonstrate_adversarial_attack(scenario_name: str, description: str):
    """Demonstrate a specific adversarial attack scenario."""
    print(f"\n{'='*80}")
    print(f"🎯 ADVERSARIAL ATTACK SCENARIO: {scenario_name}")
    print(f"📝 {description}")
    print('='*80)

    generator = AdversarialDataGenerator(seed=42)

    try:
        # Generate adversarial dataset
        print("🚀 Generating adversarial dataset...")
        adversarial_dataset = generator.generate_adversarial_dataset(scenario_name)

        shopify_orders = adversarial_dataset['shopify_orders']
        ga4_sessions = adversarial_dataset['ga4_sessions']

        print(f"📊 Generated {len(shopify_orders)} orders and {len(ga4_sessions)} sessions")

        # Analyze corruption patterns
        result = generator.generate_adversarial_result(scenario_name, adversarial_dataset)

        print("⚔️  ATTACK ANALYSIS:")
        print(f"   Attack Success Rate: {result.attack_success_rate:.2%}")
        print(f"   Dataset Size: {result.dataset_size:,} records")
        print("   Corruption Metrics:")
        for metric, value in result.corruption_metrics.items():
            if isinstance(value, float) and value < 1:
                print(f"     - {metric}: {value:.1%}")
            else:
                print(f"     - {metric}: {value}")

        # Show sample corrupted data
        if len(shopify_orders) > 0:
            print("\n📄 SAMPLE CORRUPTED DATA:")
            sample_fields = ['total_price', 'customer_email', 'created_at']
            available_fields = [f for f in sample_fields if f in shopify_orders.columns]
            if available_fields:
                sample = shopify_orders[available_fields].head(3)
                print(sample.to_string(index=False))

        print(f"✅ Attack scenario '{scenario_name}' executed successfully")
        return True

    except Exception as e:
        print(f"❌ Attack scenario '{scenario_name}' failed: {str(e)}")
        return False


def main():
    """Run comprehensive adversarial attack demonstration."""
    print("🔥 ERA ADVERSARIAL DATA GENERATION FRAMEWORK DEMONSTRATION")
    print("=" * 80)
    print("🎯 Mission: Systematically attack ERA system with hostile data patterns")
    print("🛡️  Goal: Identify vulnerabilities and harden system resilience")
    print("⚔️  Weapon: TDG-powered adversarial data generation")

    # Define attack scenarios to demonstrate
    attack_scenarios = [
        ("missing_data_scenarios", "Systematic null poisoning - Testing graceful degradation"),
        ("extreme_value_scenarios", "Statistical boundary testing - Breaking mathematical assumptions"),
        ("data_inconsistency_scenarios", "Logical corruption patterns - Violating business rules"),
        ("pii_injection_scenarios", "Privacy sanitization stress testing - Bypassing PII detection"),
        ("combined_attack_scenarios", "Multi-vector attack - Simultaneous hostile patterns"),
        ("volume_attack_scenarios", "Resource exhaustion testing - High-volume corruption"),
        ("empty_dataset_scenarios", "Edge case boundary attack - Testing empty data handling"),
        ("single_entity_scenarios", "Minimal data attack - Single-entity edge cases")
    ]

    successful_attacks = 0
    total_attacks = len(attack_scenarios)

    for scenario_name, description in attack_scenarios:
        success = demonstrate_adversarial_attack(scenario_name, description)
        if success:
            successful_attacks += 1

    # Final assessment
    print(f"\n{'='*80}")
    print("🏁 ADVERSARIAL ATTACK ASSESSMENT COMPLETE")
    print(f"{'='*80}")
    print(f"⚔️  Total Attack Scenarios: {total_attacks}")
    print(f"✅ Successful Attacks: {successful_attacks}")
    print(f"❌ Failed Attacks: {total_attacks - successful_attacks}")
    print(f"📊 Attack Success Rate: {successful_attacks/total_attacks:.1%}")

    if successful_attacks == total_attacks:
        print("🎉 ALL ADVERSARIAL ATTACKS SUCCESSFUL!")
        print("🛡️  ERA system ready for comprehensive resilience testing")
        print("⚔️  Adversarial framework operational and validated")
    else:
        print("⚠️  Some attacks failed - framework needs refinement")

    return successful_attacks == total_attacks


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

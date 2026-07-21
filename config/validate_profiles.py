"""
Profile Validation Script

Validates generated business profiles for correctness and ERA compatibility.
"""

from pathlib import Path

from era_schema_mapper import ERASchemaMapper


def validate_yaml_structure(yaml_content: str) -> bool:
    """Validate basic YAML structure without external libraries."""
    required_sections = [
        "profile_name:",
        "global_settings:",
        "entities:",
        "seed:",
        "date_range:",
        "start:",
        "end:"
    ]

    for section in required_sections:
        if section not in yaml_content:
            return False

    return True


def validate_entity_structure(yaml_content: str) -> bool:
    """Validate entity structure."""
    required_entities = [
        "shopify_customers",
        "shopify_orders",
        "ga4_sessions"
    ]

    for entity in required_entities:
        if f"entity_name: {entity}" not in yaml_content:
            return False

    return True


def validate_profile_files():
    """Validate all generated profile files."""

    profiles_dir = Path("/app/config/era_business_profiles")
    schema_mapper = ERASchemaMapper()

    required_files = [
        "high_growth_startup.yaml",
        "stable_enterprise.yaml",
        "seasonal_business.yaml",
        "data_with_pii.yaml",
        "edge_case_scenarios.yaml"
    ]

    validation_results = {}

    for filename in required_files:
        file_path = profiles_dir / filename
        business_type = filename.replace('.yaml', '')

        result = {
            "exists": file_path.exists(),
            "readable": False,
            "valid_yaml": False,
            "valid_entities": False,
            "size_kb": 0,
            "schema_mapping_works": False
        }

        if result["exists"]:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                result["readable"] = True
                result["size_kb"] = round(len(content) / 1024, 2)
                result["valid_yaml"] = validate_yaml_structure(content)
                result["valid_entities"] = validate_entity_structure(content)

                # Test schema mapping
                try:
                    profile = schema_mapper.generate_shopify_profile(business_type)
                    result["schema_mapping_works"] = "customers" in profile
                except Exception as e:
                    result["schema_mapping_error"] = str(e)

            except Exception as e:
                result["read_error"] = str(e)

        validation_results[business_type] = result

    return validation_results


def main():
    """Run comprehensive validation."""

    print("🔍 Validating ERA Business Profile Configurations")
    print("=" * 60)

    results = validate_profile_files()

    all_passed = True

    for business_type, result in results.items():
        status = "✓" if all([
            result["exists"],
            result["readable"],
            result["valid_yaml"],
            result["valid_entities"],
            result["schema_mapping_works"]
        ]) else "✗"

        if status == "✗":
            all_passed = False

        print(f"{status} {business_type}.yaml")
        print(f"   Exists: {result['exists']}")
        print(f"   Readable: {result['readable']}")
        print(f"   Valid YAML: {result['valid_yaml']}")
        print(f"   Valid Entities: {result['valid_entities']}")
        print(f"   Size: {result['size_kb']} KB")
        print(f"   Schema Mapping: {result['schema_mapping_works']}")

        if "read_error" in result:
            print(f"   Read Error: {result['read_error']}")
        if "schema_mapping_error" in result:
            print(f"   Schema Error: {result['schema_mapping_error']}")
        print()

    print("=" * 60)
    if all_passed:
        print("✓ All business profiles validated successfully!")
        print("✓ Ready for TDG integration and ERA testing")
    else:
        print("✗ Some validation issues found")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

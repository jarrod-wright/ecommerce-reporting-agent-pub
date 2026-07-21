"""
Test suite for ERA Schema Mapper - TDG Configuration Engineering
Tests the generation of business profile configurations for ERA testing.
"""

from pathlib import Path

import pytest
import yaml

# Import will fail initially - this drives TDD RED phase
try:
    from config.era_schema_mapper import ERASchemaMapper
except ImportError:
    ERASchemaMapper = None


class TestERASchemaMapper:
    """Test ERA Schema Mapper functionality."""

    @pytest.fixture
    def schema_mapper(self):
        """Fixture to provide ERASchemaMapper instance."""
        if ERASchemaMapper is None:
            pytest.skip("ERASchemaMapper not implemented yet")
        return ERASchemaMapper()

    def test_schema_mapper_initialization(self, schema_mapper):
        """Test ERASchemaMapper can be initialized."""
        assert schema_mapper is not None
        assert hasattr(schema_mapper, 'generate_shopify_profile')
        assert hasattr(schema_mapper, 'generate_ga4_profile')

    def test_generate_high_growth_startup_profile(self, schema_mapper):
        """Test generation of high growth startup business profile."""
        profile = schema_mapper.generate_shopify_profile("high_growth_startup")

        assert profile["customers"] == 5000
        assert profile["orders_per_customer"]["mean"] == 15
        assert profile["orders_per_customer"]["std_dev"] == 10
        assert profile["orders_per_customer"]["min"] == 1
        assert profile["orders_per_customer"]["max"] == 100
        assert profile["revenue_distribution"]["type"] == "lognormal"
        assert profile["revenue_distribution"]["mean"] == 200
        assert profile["revenue_distribution"]["std"] == 150
        assert profile["growth_pattern"] == "exponential"
        assert profile["seasonality"] == "minimal"

    def test_generate_stable_enterprise_profile(self, schema_mapper):
        """Test generation of stable enterprise business profile."""
        profile = schema_mapper.generate_shopify_profile("stable_enterprise")

        assert profile["customers"] == 50000
        assert profile["orders_per_customer"]["mean"] == 8
        assert profile["orders_per_customer"]["std_dev"] == 5
        assert profile["revenue_distribution"]["type"] == "normal"
        assert profile["growth_pattern"] == "steady"
        assert profile["seasonality"] == "moderate"

    def test_generate_ga4_profile(self, schema_mapper):
        """Test generation of GA4-compatible profile."""
        profile = schema_mapper.generate_ga4_profile("high_growth_startup")

        assert "daily_sessions" in profile
        assert profile["daily_sessions"]["mean"] == 500
        assert profile["daily_sessions"]["std_dev"] == 150

        assert "device_distribution" in profile
        device_dist = profile["device_distribution"]
        assert abs(device_dist["desktop"] + device_dist["mobile"] + device_dist["tablet"] - 1.0) < 0.001

        assert profile["conversion_rate"] == 0.03
        assert profile["bounce_rate"] == 0.45

    def test_invalid_business_type_raises_error(self, schema_mapper):
        """Test that invalid business type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            schema_mapper.generate_shopify_profile("invalid_type")

        assert "invalid_type" in str(exc_info.value)
        assert "valid business types" in str(exc_info.value).lower()


class TestBusinessProfileGeneration:
    """Test generation of complete business profile YAML files."""

    @pytest.fixture
    def profiles_dir(self):
        """Fixture for profiles directory path (resolved relative to the repo root)."""
        repo_root = Path(__file__).resolve().parent.parent
        return repo_root / "config" / "era_business_profiles"

    def test_profiles_directory_exists(self, profiles_dir):
        """Test that business profiles directory exists."""
        assert profiles_dir.exists()
        assert profiles_dir.is_dir()

    def test_high_growth_startup_yaml_exists(self, profiles_dir):
        """Test high growth startup YAML file exists and is valid."""
        yaml_file = profiles_dir / "high_growth_startup.yaml"
        assert yaml_file.exists()

        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)

        assert "profile_name" in config
        assert "global_settings" in config
        assert "entities" in config
        assert config["global_settings"]["seed"] is not None

    def test_all_required_profiles_exist(self, profiles_dir):
        """Test that all 5 required business profiles exist."""
        required_profiles = [
            "high_growth_startup.yaml",
            "stable_enterprise.yaml",
            "seasonal_business.yaml",
            "data_with_pii.yaml",
            "edge_case_scenarios.yaml"
        ]

        for profile_name in required_profiles:
            profile_path = profiles_dir / profile_name
            assert profile_path.exists(), f"Missing profile: {profile_name}"

    def test_yaml_files_are_valid(self, profiles_dir):
        """Test that all YAML files are syntactically valid."""
        for yaml_file in profiles_dir.glob("*.yaml"):
            with open(yaml_file, 'r') as f:
                try:
                    config = yaml.safe_load(f)
                    assert config is not None
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {yaml_file}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

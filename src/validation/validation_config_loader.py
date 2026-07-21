"""
ValidationConfigLoader - YAML Configuration Loading for Business Logic Validation

Implements Configuration-as-Ground-Truth pattern for pragmatic validation.
"""

import os
from typing import Dict

import yaml

from validation.structured_insight_models import GroundTruthConfiguration

# Resolve the default config directory relative to the repository root so it
# works both locally and inside the container (where the repo lives at /app).
_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
_DEFAULT_CONFIG_BASE = os.path.join(_REPO_ROOT, "config", "business_logic_validation")


class ValidationConfigLoader:
    """Loads and processes YAML configuration files for business logic validation scenarios"""

    def __init__(self, config_base_path: str = _DEFAULT_CONFIG_BASE):
        self.config_base_path = config_base_path
        self._ensure_config_directory()

    def _ensure_config_directory(self):
        """Create configuration directory if it doesn't exist"""
        os.makedirs(self.config_base_path, exist_ok=True)

    def load_scenario(self, scenario_name: str) -> GroundTruthConfiguration:
        """Load a business logic validation scenario from YAML configuration"""
        config_file_path = os.path.join(self.config_base_path, f"{scenario_name}.yaml")

        if not os.path.exists(config_file_path):
            # Create default configuration if it doesn't exist
            self._create_default_scenario_config(scenario_name, config_file_path)

        with open(config_file_path, 'r') as file:
            config_data = yaml.safe_load(file)

        return GroundTruthConfiguration(**config_data)

    def _create_default_scenario_config(self, scenario_name: str, config_file_path: str):
        """Create default configuration for known scenarios"""

        if scenario_name == "revenue_growth_validation":
            config = {
                "scenario_name": "revenue_growth_validation",
                "description": "Linear revenue growth pattern validation",
                "dataset_config": {
                    "customers_count": 1000,
                    "orders_per_customer": 8,
                    "time_period_months": 12,
                    "revenue_pattern": "linear_growth",
                    "base_monthly_revenue": 50000,
                    "noise_level": 0.05
                },
                "expected_pattern": {
                    "type": "linear_growth",
                    "growth_rate": 0.15,
                    "base_revenue": 50000,
                    "trend_direction": "positive"
                },
                "validation_criteria": [
                    {"metric": "monthly_growth_rate", "expected_value": 0.15, "tolerance": 0.05},
                    {"metric": "trend_direction", "expected_value": "positive"},
                    {"metric": "total_months_data", "expected_value": 12},
                    {"metric": "revenue_consistency", "expected_value": True}
                ],
                "expected_insights": [
                    "Revenue shows consistent month-over-month growth",
                    "Average monthly growth rate approximately 15%",
                    "Strong positive revenue trend identified",
                    "Recommend scaling successful marketing channels"
                ]
            }

        elif scenario_name == "seasonal_pattern_validation":
            config = {
                "scenario_name": "seasonal_pattern_validation",
                "description": "Holiday season revenue analysis",
                "dataset_config": {
                    "customers_count": 1000,
                    "orders_per_customer": 10,
                    "time_period_months": 12,
                    "revenue_pattern": "seasonal",
                    "peak_months": [11, 12],
                    "peak_multiplier": 2.5,
                    "baseline_revenue": 50000
                },
                "expected_pattern": {
                    "type": "seasonal",
                    "peak_months": [11, 12],
                    "peak_multiplier": 2.5,
                    "baseline_revenue": 50000
                },
                "validation_criteria": [
                    {"metric": "seasonality_detection", "expected_value": True},
                    {"metric": "peak_identification_accuracy", "expected_value": [11, 12]},
                    {"metric": "peak_magnitude_accuracy", "expected_value": 2.5, "tolerance": 0.3}
                ],
                "expected_insights": [
                    "Strong seasonal pattern detected",
                    "Holiday season shows 250% revenue increase",
                    "November and December peak months identified",
                    "Recommend inventory preparation for Q4"
                ]
            }

        elif scenario_name == "conversion_funnel_validation":
            config = {
                "scenario_name": "conversion_funnel_validation",
                "description": "Metrics calculation accuracy validation",
                "dataset_config": {
                    "sessions_count": 10000,
                    "conversion_rate": 0.03,
                    "average_order_value": 125.00,
                    "customer_acquisition_cost": 25.00
                },
                "expected_pattern": {
                    "type": "conversion_funnel",
                    "conversion_rate": 0.03,
                    "average_order_value": 125.00,
                    "cac_ratio": 5.0
                },
                "validation_criteria": [
                    {"metric": "conversion_rate_accuracy", "expected_value": 0.03, "tolerance": 0.005},
                    {"metric": "aov_accuracy", "expected_value": 125.00, "tolerance": 10.0},
                    {"metric": "cac_calculation_correctness", "expected_value": True}
                ],
                "expected_insights": [
                    "Conversion rate: 3.0%",
                    "Average order value: $125.00",
                    "Customer acquisition cost efficiency ratio: 5:1",
                    "Recommend conversion optimization focus"
                ]
            }

        else:
            # Generic default configuration
            config = {
                "scenario_name": scenario_name,
                "description": f"Default configuration for {scenario_name}",
                "dataset_config": {
                    "customers_count": 1000,
                    "orders_per_customer": 5,
                    "time_period_months": 12
                },
                "expected_pattern": {
                    "type": "generic",
                    "pattern_strength": 0.8
                },
                "validation_criteria": [
                    {"metric": "data_completeness", "expected_value": True},
                    {"metric": "pattern_detection", "expected_value": True},
                    {"metric": "insight_generation", "expected_value": True}
                ],
                "expected_insights": [
                    "Pattern analysis completed",
                    "Data validation successful",
                    "Insights generated successfully"
                ]
            }

        # Write configuration to file
        with open(config_file_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False, indent=2)

    def load_all_scenarios(self) -> Dict[str, GroundTruthConfiguration]:
        """Load all available scenario configurations"""
        scenarios = {}

        # Default scenarios to load
        default_scenarios = [
            "revenue_growth_validation",
            "seasonal_pattern_validation",
            "conversion_funnel_validation"
        ]

        for scenario_name in default_scenarios:
            scenarios[scenario_name] = self.load_scenario(scenario_name)

        # Load any additional YAML files in the config directory
        if os.path.exists(self.config_base_path):
            for filename in os.listdir(self.config_base_path):
                if filename.endswith('.yaml') and filename not in [f"{s}.yaml" for s in default_scenarios]:
                    scenario_name = filename.replace('.yaml', '')
                    scenarios[scenario_name] = self.load_scenario(scenario_name)

        return scenarios

"""
Adversarial Data Generation Framework for ERA System Attack Testing

This framework implements systematic data corruption and hostile pattern injection
to test ERA's resilience against real-world data quality issues and malicious inputs.
"""

import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# Import existing frameworks for integration
from tests.performance.scale_testing_framework import ERATestDataGenerator


@dataclass
class AdversarialProfile:
    """Configuration for a specific adversarial attack scenario."""
    name: str
    description: str
    attack_vector: str
    injection_rate: float
    target_fields: List[str]
    expected_behavior: str


@dataclass
class AdversarialResult:
    """Result of an adversarial data generation attack."""
    scenario_name: str
    dataset_size: int
    corruption_metrics: Dict[str, float]
    attack_success_rate: float
    adversarial_metadata: Dict[str, Any]


class AdversarialDataGenerator:
    """Generate adversarial datasets to systematically attack and test ERA robustness."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize the adversarial generator with attack profiles."""
        self.seed = seed or 42
        random.seed(self.seed)
        np.random.seed(self.seed)

        self.tdg = ERATestDataGenerator(seed=self.seed)
        self.adversarial_configs = self._load_adversarial_configurations()
        self.attack_profiles = self._create_attack_profiles()

    def _load_adversarial_configurations(self) -> Dict[str, Dict]:
        """Define systematic adversarial test scenarios based on BDD feature file."""
        return {
            "missing_data_scenarios": {
                "description": "Test ERA handling of missing/null data fields - Systematic null poisoning",
                "shopify_modifications": [
                    {"field": "total_price", "null_percentage": 0.15},  # 15% missing prices
                    {"field": "customer_id", "null_percentage": 0.10}, # 10% missing customer data
                    {"field": "created_at", "null_percentage": 0.05}    # 5% missing timestamps
                ],
                "ga4_modifications": [
                    {"field": "sessions", "null_percentage": 0.20},     # 20% missing session data
                    {"field": "page_views", "null_percentage": 0.25}    # 25% missing page views
                ],
                "expected_era_behavior": "graceful_degradation"
            },

            "extreme_value_scenarios": {
                "description": "Test ERA handling of extreme/outlier values - Statistical boundary testing",
                "shopify_modifications": [
                    {"field": "total_price", "extreme_values": [0.01, 999999.99]},    # Penny orders and extreme high values
                    {"field": "quantity", "extreme_values": [0, 10000]}               # Zero quantities or excessive amounts
                ],
                "ga4_modifications": [
                    {"field": "session_duration", "extreme_values": [1, 86400]},      # 1 second to 24 hour sessions
                    {"field": "page_views", "extreme_values": [1, 1000]}              # Single page view to excessive browsing
                ],
                "expected_era_behavior": "statistical_robustness"
            },

            "data_inconsistency_scenarios": {
                "description": "Test ERA handling of logically inconsistent data - Logical corruption patterns",
                "inconsistencies": [
                    {"type": "temporal", "description": "Orders with future dates"},
                    {"type": "referential", "description": "Orders referencing non-existent customers"},
                    {"type": "business_logic", "description": "Zero-value completed orders"},
                    {"type": "data_quality", "description": "Malformed email addresses and phone numbers"}
                ],
                "expected_era_behavior": "validation_and_correction"
            },

            "pii_injection_scenarios": {
                "description": "Test PII sanitization under adversarial conditions - Privacy sanitization stress testing",
                "pii_injection_patterns": [
                    {"field": "order_notes", "pii_types": ["email", "phone", "ssn"], "injection_rate": 0.30},
                    {"field": "customer_name", "pii_types": ["credit_card"], "injection_rate": 0.05},
                    {"field": "product_description", "pii_types": ["address"], "injection_rate": 0.15}
                ],
                "expected_era_behavior": "complete_pii_removal"
            },

            "combined_attack_scenarios": {
                "description": "Multi-vector adversarial attack - Combined hostile patterns",
                "attack_combinations": [
                    {"type": "missing_data", "rate": 0.10},
                    {"type": "extreme_values", "rate": 0.05},
                    {"type": "data_inconsistency", "rate": 0.15},
                    {"type": "pii_injection", "rate": 0.08}
                ],
                "expected_era_behavior": "multi_vector_resilience"
            },

            "volume_attack_scenarios": {
                "description": "Volume-based adversarial attack - Resource exhaustion testing",
                "volume_multipliers": {
                    "customers_count": 5000,   # Reduced for testing environment
                    "orders_per_customer": 10,
                    "ga4_sessions_count": 10000
                },
                "corruption_patterns": ["missing_data", "extreme_values"],
                "expected_era_behavior": "resource_resilience"
            },

            "empty_dataset_scenarios": {
                "description": "Edge case boundary attack - Empty datasets",
                "dataset_characteristics": {
                    "customers_count": 0,
                    "orders_count": 0,
                    "ga4_sessions_count": 0
                },
                "expected_era_behavior": "empty_data_handling"
            },

            "single_entity_scenarios": {
                "description": "Edge case boundary attack - Single entity datasets",
                "dataset_characteristics": {
                    "customers_count": 1,
                    "orders_count": 3,
                    "ga4_sessions_count": 5
                },
                "expected_era_behavior": "minimal_data_handling"
            },

            "temporal_boundary_scenarios": {
                "description": "Edge case boundary attack - Temporal extremes",
                "temporal_patterns": [
                    {"type": "single_day", "date_range_days": 1},
                    {"type": "multi_year", "date_range_days": 1095}  # 3 years
                ],
                "expected_era_behavior": "temporal_robustness"
            }
        }

    def _create_attack_profiles(self) -> List[AdversarialProfile]:
        """Create structured attack profiles from configurations."""
        profiles = []

        for scenario_name, config in self.adversarial_configs.items():
            profile = AdversarialProfile(
                name=scenario_name,
                description=config["description"],
                attack_vector=scenario_name.split("_")[0],  # e.g., "missing", "extreme"
                injection_rate=0.15,  # Default injection rate
                target_fields=self._extract_target_fields(config),
                expected_behavior=config.get("expected_era_behavior", "graceful_degradation")
            )
            profiles.append(profile)

        return profiles

    def _extract_target_fields(self, config: Dict) -> List[str]:
        """Extract target fields from configuration."""
        fields = []

        if "shopify_modifications" in config:
            fields.extend([mod["field"] for mod in config["shopify_modifications"]])

        if "ga4_modifications" in config:
            fields.extend([mod["field"] for mod in config["ga4_modifications"]])

        return fields

    def generate_adversarial_dataset(self, scenario_name: str) -> Dict[str, pd.DataFrame]:
        """Generate adversarial dataset for specified attack scenario."""
        if scenario_name not in self.adversarial_configs:
            raise ValueError(f"Unknown adversarial scenario: {scenario_name}")

        scenario_config = self.adversarial_configs[scenario_name]

        # Generate base dataset using TDG (different sizes for different scenarios)
        if scenario_name == "volume_attack_scenarios":
            dataset_config = scenario_config["volume_multipliers"]
        elif scenario_name in ["empty_dataset_scenarios", "single_entity_scenarios"]:
            dataset_config = scenario_config["dataset_characteristics"]
        else:
            dataset_config = {
                'customers_count': 1000,
                'orders_per_customer': 8,
                'ga4_sessions_count': 5000
            }

        # Handle empty dataset scenario
        if scenario_name == "empty_dataset_scenarios":
            return {
                'shopify_orders': pd.DataFrame(),
                'ga4_sessions': pd.DataFrame()
            }

        # Generate base dataset
        base_dataset = self.tdg.generate_era_compatible_dataset(dataset_config)

        # Apply adversarial modifications based on scenario type
        if scenario_name == "missing_data_scenarios":
            modified_dataset = self._apply_missing_data_modifications(base_dataset, scenario_config)
        elif scenario_name == "extreme_value_scenarios":
            modified_dataset = self._apply_extreme_value_modifications(base_dataset, scenario_config)
        elif scenario_name == "data_inconsistency_scenarios":
            modified_dataset = self._apply_inconsistency_modifications(base_dataset, scenario_config)
        elif scenario_name == "pii_injection_scenarios":
            modified_dataset = self._apply_pii_injection_modifications(base_dataset, scenario_config)
        elif scenario_name == "combined_attack_scenarios":
            modified_dataset = self._apply_combined_attack_modifications(base_dataset, scenario_config)
        elif scenario_name == "volume_attack_scenarios":
            modified_dataset = self._apply_volume_attack_modifications(base_dataset, scenario_config)
        elif scenario_name == "temporal_boundary_scenarios":
            modified_dataset = self._apply_temporal_boundary_modifications(base_dataset, scenario_config)
        else:
            # For other edge cases, return base dataset
            modified_dataset = base_dataset

        return modified_dataset

    def _apply_missing_data_modifications(self, dataset: Dict[str, pd.DataFrame], config: Dict) -> Dict[str, pd.DataFrame]:
        """Apply systematic null injection to create missing data attack patterns."""
        modified_dataset = dataset.copy()

        # Apply shopify modifications
        shopify_orders = modified_dataset['shopify_orders'].copy()
        for mod in config.get("shopify_modifications", []):
            field = mod["field"]
            null_percentage = mod["null_percentage"]

            if field in shopify_orders.columns:
                n_nulls = int(len(shopify_orders) * null_percentage)
                null_indices = np.random.choice(shopify_orders.index, n_nulls, replace=False)
                shopify_orders.loc[null_indices, field] = None

        modified_dataset['shopify_orders'] = shopify_orders

        # Apply GA4 modifications
        ga4_sessions = modified_dataset['ga4_sessions'].copy()
        for mod in config.get("ga4_modifications", []):
            field = mod["field"]
            null_percentage = mod["null_percentage"]

            if field in ga4_sessions.columns:
                n_nulls = int(len(ga4_sessions) * null_percentage)
                null_indices = np.random.choice(ga4_sessions.index, n_nulls, replace=False)
                ga4_sessions.loc[null_indices, field] = None

        modified_dataset['ga4_sessions'] = ga4_sessions

        return modified_dataset

    def _apply_extreme_value_modifications(self, dataset: Dict[str, pd.DataFrame], config: Dict) -> Dict[str, pd.DataFrame]:
        """Apply extreme value injection to create statistical outlier attack patterns."""
        modified_dataset = dataset.copy()

        # Apply shopify extreme value modifications
        shopify_orders = modified_dataset['shopify_orders'].copy()
        for mod in config.get("shopify_modifications", []):
            field = mod["field"]
            extreme_values = mod["extreme_values"]

            if field in shopify_orders.columns:
                # Convert field to numeric first to avoid string comparison issues
                if field == "total_price":
                    shopify_orders[field] = pd.to_numeric(shopify_orders[field], errors='coerce')

                # Inject extreme values in 10% of records
                n_extremes = int(len(shopify_orders) * 0.10)
                extreme_indices = np.random.choice(shopify_orders.index, n_extremes, replace=False)

                # Randomly assign extreme low or high values
                for idx in extreme_indices:
                    extreme_value = np.random.choice(extreme_values)
                    shopify_orders.loc[idx, field] = float(extreme_value)

        modified_dataset['shopify_orders'] = shopify_orders

        # Apply GA4 extreme value modifications
        ga4_sessions = modified_dataset['ga4_sessions'].copy()
        for mod in config.get("ga4_modifications", []):
            field = mod["field"]
            extreme_values = mod["extreme_values"]

            if field in ga4_sessions.columns:
                n_extremes = int(len(ga4_sessions) * 0.10)
                extreme_indices = np.random.choice(ga4_sessions.index, n_extremes, replace=False)

                for idx in extreme_indices:
                    extreme_value = np.random.choice(extreme_values)
                    ga4_sessions.loc[idx, field] = extreme_value

        modified_dataset['ga4_sessions'] = ga4_sessions

        return modified_dataset

    def _apply_inconsistency_modifications(self, dataset: Dict[str, pd.DataFrame], config: Dict) -> Dict[str, pd.DataFrame]:
        """Apply logical inconsistency patterns to create data corruption."""
        modified_dataset = dataset.copy()
        shopify_orders = modified_dataset['shopify_orders'].copy()

        # Inject future dates (temporal inconsistency)
        if 'created_at' in shopify_orders.columns:
            # First convert the column to datetime and remove timezone info for consistency
            shopify_orders['created_at'] = pd.to_datetime(shopify_orders['created_at'], errors='coerce')
            if shopify_orders['created_at'].dt.tz is not None:
                shopify_orders['created_at'] = shopify_orders['created_at'].dt.tz_localize(None)

            future_date_indices = np.random.choice(
                shopify_orders.index,
                int(len(shopify_orders) * 0.05),
                replace=False
            )
            future_date = datetime.now() + timedelta(days=30)
            # Convert to pandas timestamp (timezone-naive)
            future_timestamp = pd.Timestamp(future_date).tz_localize(None)
            shopify_orders.loc[future_date_indices, 'created_at'] = future_timestamp

        # Inject zero-value completed orders (business logic inconsistency)
        if 'total_price' in shopify_orders.columns:
            # Ensure we have a fulfillment_status column
            if 'fulfillment_status' not in shopify_orders.columns:
                shopify_orders['fulfillment_status'] = 'fulfilled'

            zero_value_indices = np.random.choice(
                shopify_orders.index,
                int(len(shopify_orders) * 0.03),
                replace=False
            )
            shopify_orders.loc[zero_value_indices, 'total_price'] = 0
            shopify_orders.loc[zero_value_indices, 'fulfillment_status'] = 'fulfilled'

        # Inject malformed email addresses
        if 'customer_email' not in shopify_orders.columns:
            # Create customer email column with normal emails
            shopify_orders['customer_email'] = [
                f"customer{i}@example.com" for i in range(len(shopify_orders))
            ]

        # Corrupt some email addresses
        malformed_indices = np.random.choice(
            shopify_orders.index,
            int(len(shopify_orders) * 0.05),
            replace=False
        )
        for idx in malformed_indices:
            # Remove @ symbol to make email malformed
            original_email = shopify_orders.loc[idx, 'customer_email']
            shopify_orders.loc[idx, 'customer_email'] = original_email.replace('@', '')

        modified_dataset['shopify_orders'] = shopify_orders
        return modified_dataset

    def _apply_pii_injection_modifications(self, dataset: Dict[str, pd.DataFrame], config: Dict) -> Dict[str, pd.DataFrame]:
        """Apply PII injection patterns to test sanitization robustness."""
        modified_dataset = dataset.copy()
        shopify_orders = modified_dataset['shopify_orders'].copy()

        # PII patterns for injection
        pii_patterns = {
            "email": ["john.doe@secret.com", "sensitive.user@private.org", "leaked@data.com"],
            "phone": ["123-456-7890", "555-123-4567", "800-555-0199"],
            "ssn": ["123-45-6789", "987-65-4321", "555-44-3333"],
            "credit_card": ["4532-1234-5678-9012", "5555-5555-5555-4444"],
            "address": ["123 Secret Lane, Hidden City", "456 Private St, Confidential Town"]
        }

        # Apply PII injection patterns
        for pattern_config in config.get("pii_injection_patterns", []):
            field = pattern_config["field"]
            pii_types = pattern_config["pii_types"]
            injection_rate = pattern_config["injection_rate"]

            # Ensure field exists
            if field not in shopify_orders.columns:
                if field == "order_notes":
                    shopify_orders[field] = ["Standard order"] * len(shopify_orders)
                elif field == "customer_name":
                    shopify_orders[field] = [f"Customer {i}" for i in range(len(shopify_orders))]
                elif field == "product_description":
                    shopify_orders[field] = ["Product description"] * len(shopify_orders)

            # Inject PII patterns - ensure we don't exceed available records
            n_injections = min(int(len(shopify_orders) * injection_rate), len(shopify_orders))
            if n_injections > 0:
                injection_indices = np.random.choice(shopify_orders.index, n_injections, replace=False)

                for idx in injection_indices:
                    # Select random PII type and pattern
                    pii_type = np.random.choice(pii_types)
                    if pii_type in pii_patterns:
                        pii_value = np.random.choice(pii_patterns[pii_type])
                        # Inject PII into existing field content
                        current_value = shopify_orders.loc[idx, field]
                        shopify_orders.loc[idx, field] = f"{current_value} {pii_value}"

        modified_dataset['shopify_orders'] = shopify_orders
        return modified_dataset

    def _apply_combined_attack_modifications(self, dataset: Dict[str, pd.DataFrame], config: Dict) -> Dict[str, pd.DataFrame]:
        """Apply multiple attack vectors simultaneously."""
        modified_dataset = dataset.copy()

        # Apply each attack type from the combination
        for attack_combo in config.get("attack_combinations", []):
            attack_type = attack_combo["type"]
            rate = attack_combo["rate"]

            if attack_type == "missing_data":
                # Apply missing data with specified rate across multiple fields
                missing_config = {
                    "shopify_modifications": [
                        {"field": "total_price", "null_percentage": rate},
                        {"field": "customer_id", "null_percentage": rate * 0.8}  # Slightly less for customer_id
                    ],
                    "ga4_modifications": [
                        {"field": "sessions", "null_percentage": rate * 1.2}  # Slightly more for sessions
                    ]
                }
                modified_dataset = self._apply_missing_data_modifications(modified_dataset, missing_config)

            elif attack_type == "extreme_values":
                # Apply extreme values with specified rate
                extreme_config = {
                    "shopify_modifications": [
                        {"field": "total_price", "extreme_values": [0.01, 99999.99]}
                    ]
                }
                modified_dataset = self._apply_extreme_value_modifications(modified_dataset, extreme_config)

            elif attack_type == "pii_injection":
                # Apply PII injection with specified rate
                pii_config = {
                    "pii_injection_patterns": [
                        {"field": "order_notes", "pii_types": ["email"], "injection_rate": rate}
                    ]
                }
                modified_dataset = self._apply_pii_injection_modifications(modified_dataset, pii_config)

        return modified_dataset

    def _apply_volume_attack_modifications(self, dataset: Dict[str, pd.DataFrame], config: Dict) -> Dict[str, pd.DataFrame]:
        """Apply corruption patterns to high-volume dataset."""
        modified_dataset = dataset.copy()

        # Apply standard corruption patterns to the large dataset
        corruption_patterns = config.get("corruption_patterns", ["missing_data"])

        for pattern in corruption_patterns:
            if pattern == "missing_data":
                missing_config = {
                    "shopify_modifications": [
                        {"field": "total_price", "null_percentage": 0.05}
                    ]
                }
                modified_dataset = self._apply_missing_data_modifications(modified_dataset, missing_config)

            elif pattern == "extreme_values":
                extreme_config = {
                    "shopify_modifications": [
                        {"field": "total_price", "extreme_values": [0.01, 50000.00]}
                    ]
                }
                modified_dataset = self._apply_extreme_value_modifications(modified_dataset, extreme_config)

        return modified_dataset

    def _apply_temporal_boundary_modifications(self, dataset: Dict[str, pd.DataFrame], config: Dict) -> Dict[str, pd.DataFrame]:
        """Apply temporal boundary attack patterns."""
        modified_dataset = dataset.copy()
        shopify_orders = modified_dataset['shopify_orders'].copy()

        # Apply temporal patterns
        for pattern in config.get("temporal_patterns", []):
            pattern_type = pattern["type"]
            date_range_days = pattern["date_range_days"]

            if 'created_at' in shopify_orders.columns:
                base_date = datetime.now() - timedelta(days=30)

                if pattern_type == "single_day":
                    # All orders within single day
                    shopify_orders['created_at'] = base_date

                elif pattern_type == "multi_year":
                    # Orders spread across multiple years
                    date_range = [
                        base_date - timedelta(days=date_range_days//2 + i)
                        for i in range(len(shopify_orders))
                    ]
                    shopify_orders['created_at'] = date_range[:len(shopify_orders)]

        modified_dataset['shopify_orders'] = shopify_orders
        return modified_dataset

    def generate_adversarial_result(self, scenario_name: str, dataset: Dict[str, pd.DataFrame]) -> AdversarialResult:
        """Generate comprehensive result analysis for adversarial dataset."""
        shopify_orders = dataset['shopify_orders']
        ga4_sessions = dataset['ga4_sessions']

        # Calculate corruption metrics
        corruption_metrics = {}

        if len(shopify_orders) > 0:
            # Missing data percentage
            total_cells = shopify_orders.size
            missing_cells = shopify_orders.isnull().sum().sum()
            corruption_metrics["missing_data_percentage"] = missing_cells / total_cells if total_cells > 0 else 0

            # Extreme values count (if price field exists)
            if 'total_price' in shopify_orders.columns:
                prices = shopify_orders['total_price'].dropna()
                extreme_low = (prices <= 1.0).sum()
                extreme_high = (prices >= 10000.0).sum()
                corruption_metrics["extreme_values_count"] = extreme_low + extreme_high

        # Calculate attack success rate (simplified)
        attack_success_rate = min(sum(corruption_metrics.values()) / 10, 1.0)

        return AdversarialResult(
            scenario_name=scenario_name,
            dataset_size=len(shopify_orders),
            corruption_metrics=corruption_metrics,
            attack_success_rate=attack_success_rate,
            adversarial_metadata={
                "seed": self.seed,
                "generation_timestamp": datetime.now().isoformat(),
                "attack_vectors_applied": [scenario_name]
            }
        )

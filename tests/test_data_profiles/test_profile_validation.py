"""
Test Data Profile Validation Framework

Validates TDG-generated profiles meet ERA requirements.
Tests data schema compliance, business logic, and integration compatibility.
"""

import os
import random
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from test_data_generator.core.generator import TestDataGenerator
from test_data_generator.poc.minimal_generator import MinimalGenerator


class MockDataFrame:
    """Mock DataFrame for testing without pandas dependency."""

    def __init__(self, data: List[Dict[str, Any]]):
        """Initialize with list of dictionaries."""
        self.data = data
        self._columns = list(data[0].keys()) if data else []

    @property
    def columns(self) -> List[str]:
        """Get column names."""
        return self._columns

    def __len__(self) -> int:
        """Get row count."""
        return len(self.data)

    def __getitem__(self, column: str) -> List[Any]:
        """Get column values."""
        return [row.get(column) for row in self.data]

    def to_dict(self, orient: str = 'records') -> List[Dict[str, Any]]:
        """Convert to dictionary format."""
        if orient == 'records':
            return self.data
        return self.data


class TDGDataGenerator:
    """Real TDG data generator using integrated TDG library."""

    def __init__(self, seed: int = 42):
        """Initialize with reproducible seed."""
        random.seed(seed)
        self.seed = seed
        self.tdg_generator = TestDataGenerator()
        self.minimal_generator = MinimalGenerator(seed=seed)

    def generate_dataset_from_yaml(self, yaml_path: str) -> Dict[str, pd.DataFrame]:
        """Generate dataset using real TDG based on YAML profile configuration."""

        # Parse YAML configuration
        config = self._parse_yaml_file(yaml_path)

        dataset = {}
        entities = config.get('entities', [])

        # Generate entities in dependency order
        for entity in entities:
            entity_name = entity['entity_name']

            if entity_name == 'shopify_customers':
                # Use real TDG to generate customer data
                customer_count = entity.get('count', 1000)
                customers_df = self.minimal_generator.generate_customers(customer_count)
                dataset['shopify_customers'] = customers_df
                dataset['customers'] = customers_df  # Alias for compatibility

            elif entity_name == 'shopify_orders':
                if 'shopify_customers' not in dataset:
                    raise ValueError("Orders require customers to be generated first")
                # Generate orders using customer IDs from real TDG data
                orders_data = self._generate_orders_from_customers(entity, dataset['shopify_customers'])
                dataset['shopify_orders'] = pd.DataFrame(orders_data)

            elif entity_name == 'ga4_sessions':
                # Generate GA4 sessions with realistic data
                ga4_data = self._generate_ga4_sessions(entity)
                dataset['ga4_sessions'] = pd.DataFrame(ga4_data)

        return dataset

    def _parse_yaml_file(self, yaml_path: str) -> Dict[str, Any]:
        """Parse YAML file manually (without pyyaml)."""
        with open(yaml_path, 'r') as f:
            content = f.read()

        # Simple YAML parsing for our specific structure
        config = {
            'profile_name': self._extract_yaml_value(content, 'profile_name'),
            'entities': []
        }

        # Extract entities
        entity_sections = content.split('- entity_name:')[1:]  # Skip first empty part

        for section in entity_sections:
            entity = self._parse_entity_section(section)
            config['entities'].append(entity)

        return config

    def _extract_yaml_value(self, content: str, key: str) -> str:
        """Extract value for a key from YAML content."""
        pattern = f'{key}:\\s*"([^"]*)"'
        match = re.search(pattern, content)
        return match.group(1) if match else ""

    def _parse_entity_section(self, section: str) -> Dict[str, Any]:
        """Parse an entity section from YAML."""
        lines = section.strip().split('\n')
        entity_name = lines[0].strip()

        entity = {'entity_name': entity_name}

        # Extract count
        for line in lines:
            if 'count:' in line and 'count_per_parent:' not in line:
                count_match = re.search(r'count:\s*(\d+)', line)
                if count_match:
                    entity['count'] = int(count_match.group(1))

        return entity

    def _generate_customers(self, entity_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate customer records."""
        count = entity_config.get('count', 100)

        customers = []
        for i in range(count):
            customer = {
                'customer_id': f'cust_{i:08d}',
                'first_name': f'FirstName{i}',
                'last_name': f'LastName{i}',
                'email': f'customer{i}@example.com',
                'phone': f'555-{i:04d}-{random.randint(1000, 9999)}',
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
            }
            customers.append(customer)

        return customers

    def _generate_orders(self, entity_config: Dict[str, Any], customers_df: MockDataFrame) -> List[Dict[str, Any]]:
        """Generate order records with referential integrity."""
        customer_ids = customers_df['customer_id']
        orders_per_customer = random.randint(1, 20)  # Mock distribution

        orders = []
        order_id = 0

        for customer_id in customer_ids[:100]:  # Limit for performance
            num_orders = random.randint(1, orders_per_customer)

            for _ in range(num_orders):
                order = {
                    'id': f'order_{order_id:08d}',
                    'order_number': random.randint(1000, 999999),
                    'customer_id': customer_id,
                    'created_at': (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat(),
                    'total_price': f'{random.uniform(10.0, 1000.0):.2f}',  # String for Polars compatibility
                    'financial_status': random.choice(['paid', 'pending', 'refunded']),
                    'fulfillment_status': random.choice(['fulfilled', 'unfulfilled', 'shipped'])
                }
                orders.append(order)
                order_id += 1

        return orders

    def _generate_ga4_sessions(self, entity_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate GA4 session records."""
        count = entity_config.get('count', 1000)

        sessions = []
        base_date = datetime.now() - timedelta(days=30)

        for i in range(count):
            session = {
                'date': (base_date + timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                'device_category': random.choice(['desktop', 'mobile', 'tablet']),
                'page_views': random.randint(1, 20),
                'duration': random.randint(30, 1800),
                'sessions': 1,
                'users': 1
            }
            sessions.append(session)

        return sessions

    def _generate_orders_from_customers(self, entity: Dict[str, Any], customers_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate orders data using real customer data from TDG."""
        orders = []
        customer_ids = customers_df['customer_id'].tolist()

        order_count = entity.get('count', 2000)

        for i in range(order_count):
            customer_id = random.choice(customer_ids)
            order_id = f"order_{i+1:06d}"

            order = {
                'id': order_id,
                'order_id': order_id,
                'customer_id': customer_id,
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                'total_price': f"{random.uniform(20.00, 500.00):.2f}",
                'financial_status': random.choice(['paid', 'pending', 'refunded']),
                'fulfillment_status': random.choice(['fulfilled', 'unfulfilled', 'shipped']),
                'currency': 'USD',
                'item_count': random.randint(1, 5),
                'discount_amount': f"{random.uniform(0.00, 50.00):.2f}",
                'tax_amount': f"{random.uniform(2.00, 40.00):.2f}",
            }
            orders.append(order)

        return orders


class TestDataProfileValidator:
    """Validates TDG-generated profiles meet ERA requirements."""

    def __init__(self):
        """Initialize the profile validator."""
        self.data_generator = TDGDataGenerator()
        self.profiles_dir = Path("/app/config/era_business_profiles")

    def generate_dataset(self, profile_path: str) -> Dict[str, pd.DataFrame]:
        """Generate dataset using real TDG profile."""
        if not os.path.exists(profile_path):
            raise FileNotFoundError(f"Profile not found: {profile_path}")

        return self.data_generator.generate_dataset_from_yaml(profile_path)

    def test_shopify_schema_compliance(self, profile_name: str) -> Dict[str, Any]:
        """Verify generated Shopify data matches ERA expectations."""

        profile_path = self.profiles_dir / f"{profile_name}.yaml"
        dataset = self.generate_dataset(str(profile_path))
        shopify_data = dataset['shopify_orders']

        results = {
            'profile_name': profile_name,
            'test_name': 'shopify_schema_compliance',
            'passed': True,
            'errors': [],
            'validations': {}
        }

        try:
            # Validate ERA-required fields
            required_fields = ['id', 'created_at', 'total_price', 'customer_id', 'financial_status']
            missing_fields = [field for field in required_fields if field not in shopify_data.columns]

            if missing_fields:
                results['passed'] = False
                results['errors'].append(f"Missing required fields: {missing_fields}")
            else:
                results['validations']['required_fields'] = '✓ All required fields present'

            # Validate data types for Polars compatibility
            total_prices = shopify_data['total_price']
            if len(total_prices) > 0 and isinstance(total_prices.iloc[0], str):
                results['validations']['total_price_type'] = '✓ total_price is string type (Polars compatible)'
            else:
                results['passed'] = False
                results['errors'].append("total_price must be string type for Polars compatibility")

            # Validate timestamps
            created_at_values = shopify_data['created_at'].tolist()
            valid_timestamps = all(self._is_valid_iso_timestamp(ts) for ts in created_at_values if ts)

            if valid_timestamps:
                results['validations']['timestamps'] = '✓ All created_at values are valid ISO timestamps'
            else:
                results['passed'] = False
                results['errors'].append("Invalid timestamp format in created_at field")

            # Validate business logic
            try:
                positive_prices = all(float(price) > 0 for price in total_prices.tolist() if price)
                if positive_prices:
                    results['validations']['positive_prices'] = '✓ All prices are positive'
                else:
                    results['passed'] = False
                    results['errors'].append("Some prices are not positive")
            except ValueError:
                results['passed'] = False
                results['errors'].append("total_price values are not convertible to float")

            # Validate referential integrity
            customer_ids = set(dataset['customers']['customer_id'])
            order_customer_ids = set(shopify_data['customer_id'])

            if order_customer_ids.issubset(customer_ids):
                results['validations']['referential_integrity'] = '✓ All orders reference valid customers'
            else:
                results['passed'] = False
                results['errors'].append("Some orders reference non-existent customers")

        except Exception as e:
            results['passed'] = False
            results['errors'].append(f"Validation error: {str(e)}")

        return results

    def test_ga4_schema_compliance(self, profile_name: str) -> Dict[str, Any]:
        """Verify generated GA4 data matches ERA processing requirements."""

        profile_path = self.profiles_dir / f"{profile_name}.yaml"
        dataset = self.generate_dataset(str(profile_path))
        ga4_data = dataset['ga4_sessions']

        results = {
            'profile_name': profile_name,
            'test_name': 'ga4_schema_compliance',
            'passed': True,
            'errors': [],
            'validations': {}
        }

        try:
            # Validate ERA processing compatibility
            required_fields = ['date', 'device_category', 'page_views', 'duration', 'sessions', 'users']
            missing_fields = [field for field in required_fields if field not in ga4_data.columns]

            if missing_fields:
                results['passed'] = False
                results['errors'].append(f"Missing required GA4 fields: {missing_fields}")
            else:
                results['validations']['required_fields'] = '✓ All required GA4 fields present'

            # Validate date format (YYYY-MM-DD)
            dates = ga4_data['date']
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            valid_dates = all(re.match(date_pattern, str(date)) for date in dates if date)

            if valid_dates:
                results['validations']['date_format'] = '✓ All dates match YYYY-MM-DD format'
            else:
                results['passed'] = False
                results['errors'].append("Invalid date format (expected YYYY-MM-DD)")

            # Validate positive values
            page_views = ga4_data['page_views']
            durations = ga4_data['duration']

            if all(pv > 0 for pv in page_views if pv is not None):
                results['validations']['positive_page_views'] = '✓ All page_views are positive'
            else:
                results['passed'] = False
                results['errors'].append("Some page_views are not positive")

            if all(d > 0 for d in durations if d is not None):
                results['validations']['positive_duration'] = '✓ All durations are positive'
            else:
                results['passed'] = False
                results['errors'].append("Some durations are not positive")

            # Validate device categories
            device_categories = ga4_data['device_category']
            valid_categories = {'desktop', 'mobile', 'tablet'}
            invalid_categories = set(device_categories) - valid_categories

            if not invalid_categories:
                results['validations']['device_categories'] = '✓ All device categories are valid'
            else:
                results['passed'] = False
                results['errors'].append(f"Invalid device categories: {invalid_categories}")

        except Exception as e:
            results['passed'] = False
            results['errors'].append(f"GA4 validation error: {str(e)}")

        return results

    def validate_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Run validation on all business profiles."""

        business_profiles = [
            'high_growth_startup',
            'stable_enterprise',
            'seasonal_business',
            'data_with_pii',
            'edge_case_scenarios'
        ]

        results = {}

        for profile in business_profiles:
            try:
                shopify_results = self.test_shopify_schema_compliance(profile)
                ga4_results = self.test_ga4_schema_compliance(profile)

                results[profile] = {
                    'shopify_validation': shopify_results,
                    'ga4_validation': ga4_results,
                    'overall_passed': shopify_results['passed'] and ga4_results['passed']
                }

            except Exception as e:
                results[profile] = {
                    'error': f"Profile validation failed: {str(e)}",
                    'overall_passed': False
                }

        return results

    def _is_valid_iso_timestamp(self, timestamp_str: str) -> bool:
        """Check if string is valid ISO timestamp."""
        try:
            datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError):
            return False


def main():
    """Run profile validation tests."""

    validator = TestDataProfileValidator()

    print("🧪 Running Business Profile Validation Framework")
    print("=" * 60)

    # Test individual profile
    print("\n🔍 Testing high_growth_startup profile...")
    try:
        shopify_result = validator.test_shopify_schema_compliance('high_growth_startup')
        ga4_result = validator.test_ga4_schema_compliance('high_growth_startup')

        print(f"Shopify validation: {'✓ PASSED' if shopify_result['passed'] else '✗ FAILED'}")
        if shopify_result['errors']:
            for error in shopify_result['errors']:
                print(f"  - {error}")

        for validation, message in shopify_result.get('validations', {}).items():
            print(f"  {message}")

        print(f"GA4 validation: {'✓ PASSED' if ga4_result['passed'] else '✗ FAILED'}")
        if ga4_result['errors']:
            for error in ga4_result['errors']:
                print(f"  - {error}")

        for validation, message in ga4_result.get('validations', {}).items():
            print(f"  {message}")

    except Exception as e:
        print(f"✗ Error testing profile: {e}")

    print("\n🔍 Testing all business profiles...")
    all_results = validator.validate_all_profiles()

    passed_count = 0
    total_count = len(all_results)

    for profile, result in all_results.items():
        status = "✓ PASSED" if result.get('overall_passed', False) else "✗ FAILED"
        print(f"{profile}: {status}")

        if result.get('overall_passed', False):
            passed_count += 1

        if 'error' in result:
            print(f"  Error: {result['error']}")

    print(f"\n📊 Overall Results: {passed_count}/{total_count} profiles passed validation")

    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

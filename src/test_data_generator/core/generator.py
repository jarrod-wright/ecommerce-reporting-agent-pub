"""
Stub implementation for TestDataGenerator
This is a minimal stub to resolve ImportError issues  
"""
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class TestDataGenerator:
    """Stub implementation for Test Data Generator"""

    def __init__(self):
        self.random = random.Random(42)  # Consistent seed for testing

    def generate_dataset(self,
                        size: int = 100,
                        schema: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Generate test dataset based on schema"""
        if not schema:
            schema = {
                "id": "int",
                "name": "str",
                "value": "float",
                "timestamp": "datetime"
            }

        dataset = []
        for i in range(size):
            record = {}
            for field, field_type in schema.items():
                record[field] = self._generate_value(field, field_type, i)
            dataset.append(record)

        return dataset

    def _generate_value(self, field: str, field_type: str, index: int) -> Any:
        """Generate a value based on field type"""
        if field_type == "int":
            return index
        elif field_type == "str":
            return f"{field}_{index}"
        elif field_type == "float":
            return round(self.random.uniform(0.0, 100.0), 2)
        elif field_type == "datetime":
            base = datetime(2024, 1, 1)
            return base + timedelta(days=index)
        else:
            return f"value_{index}"

    def generate_ecommerce_dataset(self, size: int = 100) -> List[Dict[str, Any]]:
        """Generate ecommerce-specific test dataset"""
        return [
            {
                "order_id": i,
                "customer_id": self.random.randint(1, 1000),
                "product_id": self.random.randint(1, 500),
                "quantity": self.random.randint(1, 10),
                "price": round(self.random.uniform(5.0, 500.0), 2),
                "order_date": datetime(2024, 1, 1) + timedelta(days=self.random.randint(0, 365)),
                "category": self.random.choice(["electronics", "clothing", "books", "home", "sports"])
            }
            for i in range(size)
        ]

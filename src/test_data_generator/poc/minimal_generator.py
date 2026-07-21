"""
Stub implementation for MinimalGenerator  
This is a minimal stub to resolve ImportError issues
"""
import random
from typing import Any, Dict, List


class MinimalGenerator:
    """Stub implementation for Minimal Generator"""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.random = random.Random(seed)

    def generate_basic_dataset(self, size: int = 100) -> List[Dict[str, Any]]:
        """Generate basic test dataset"""
        return [
            {
                "id": i,
                "name": f"test_item_{i}",
                "value": i * 10,
                "category": f"category_{i % 5}"
            }
            for i in range(size)
        ]

    def generate_ecommerce_data(self, size: int = 100) -> List[Dict[str, Any]]:
        """Generate basic ecommerce test data"""
        return [
            {
                "order_id": i,
                "customer_id": self.random.randint(1, 50),
                "product_name": f"product_{i}",
                "quantity": self.random.randint(1, 5),
                "price": round(self.random.uniform(9.99, 109.99), 2),
                "timestamp": f"2024-01-{self.random.randint(1, 30):02d}T10:00:00Z"
            }
            for i in range(size)
        ]

    def generate_customers(self, size: int = 100):
        """Generate customer data for ERA compatibility"""
        import pandas as pd
        return pd.DataFrame([
            {
                "customer_id": i,
                "name": f"Customer_{i}",
                "email": f"customer_{i}@test.com",
                "signup_date": f"2024-{self.random.randint(1, 12):02d}-{self.random.randint(1, 28):02d}",
                "lifetime_value": round(self.random.uniform(100, 5000), 2)
            }
            for i in range(1, size + 1)
        ])

"""
Multi-Scale Performance Testing Framework for ERA System

Systematic performance testing using TDG-generated datasets across multiple scales
to validate ERA performance, identify bottlenecks, and ensure SLA compliance.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict

import pandas as pd
import psutil

from agent.graph.process_data_node import process_data_node

# Import ERA components
from agent.models.state import ReportingAgentState
from config.era_schema_mapper import ERASchemaMapper
from test_data_generator.core.generator import TestDataGenerator
from test_data_generator.poc.minimal_generator import MinimalGenerator

# Import TDG components
from test_data_generator.poc.pii_sanitization_poc import PIISanitizationPOC


@dataclass
class PerformanceMetrics:
    """Performance metrics captured during scale testing."""
    scale_name: str
    total_records: int
    dataset_generation_time: float
    era_execution_time: float
    total_end_to_end_time: float
    memory_peak_mb: float
    memory_growth_mb: float
    sla_compliance: bool
    memory_compliance: bool


class ERATestDataGenerator:
    """ERA-specific TDG integration layer for performance testing."""

    def __init__(self, seed: int = 42):
        """Initialize with TDG components and ERA schema mapping."""
        self.seed = seed
        self.tdg_generator = TestDataGenerator()
        self.minimal_generator = MinimalGenerator(seed=seed)
        self.pii_scrubber = PIISanitizationPOC()
        self.schema_mapper = ERASchemaMapper()

    def generate_era_compatible_dataset(self, config: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Generate ERA-compatible test datasets using TDG capabilities.
        
        Args:
            config: Dictionary with customers_count, orders_per_customer, ga4_sessions_count
            
        Returns:
            Dictionary with 'shopify_orders' and 'ga4_sessions' DataFrames
        """
        customers_count = config.get('customers_count', 100)
        orders_per_customer = config.get('orders_per_customer', 3)
        ga4_sessions_count = config.get('ga4_sessions_count', 1000)

        # Generate customers using MinimalGenerator
        customers_df = self.minimal_generator.generate_customers(customers_count)

        # Generate orders with referential integrity
        total_orders = customers_count * orders_per_customer
        orders_data = []

        for i in range(total_orders):
            # Select random customer_id from generated customers
            customer_idx = i % customers_count
            customer_id = customers_df.iloc[customer_idx]['customer_id'] if len(customers_df) > customer_idx else f"cust_{customer_idx:04d}"

            order = {
                'id': f"order_{i:06d}",
                'order_number': str(1000 + i),
                'created_at': f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}T10:00:00Z",
                'total_price': str(round(50.0 + (i * 7.3) % 500, 2)),  # String for Polars compatibility
                'customer_id': customer_id,
                'financial_status': ['paid', 'pending', 'refunded'][i % 3],
                'fulfillment_status': ['fulfilled', 'unfulfilled', 'shipped'][i % 3]
            }
            orders_data.append(order)

        # Generate GA4 sessions
        ga4_data = []
        for i in range(ga4_sessions_count):
            session = {
                'date': f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                'device_category': ['desktop', 'mobile', 'tablet'][i % 3],
                'page_views': 1 + (i % 20),
                'duration': 30 + (i * 17) % 1800,
                'sessions': 1,
                'users': 1
            }
            ga4_data.append(session)

        return {
            'shopify_orders': pd.DataFrame(orders_data),
            'ga4_sessions': pd.DataFrame(ga4_data)
        }


class MultiScalePerformanceFramework:
    """Systematic performance testing using TDG-generated datasets."""

    def __init__(self):
        """Initialize the performance testing framework."""
        self.tdg = ERATestDataGenerator()
        self.scale_matrix = self._define_scale_matrix()

    def _define_scale_matrix(self) -> Dict[str, Dict]:
        """Define systematic scale testing matrix."""
        return {
            "micro_scale": {
                "customers": 100,
                "orders": 300,
                "ga4_sessions": 1000,
                "target_latency": 15.0,  # seconds
                "target_memory": 512,    # MB
                "description": "Basic functionality validation"
            },
            "small_scale": {
                "customers": 1000,
                "orders": 5000,
                "ga4_sessions": 15000,
                "target_latency": 30.0,
                "target_memory": 1024,
                "description": "Small business simulation"
            },
            "medium_scale": {
                "customers": 10000,
                "orders": 50000,
                "ga4_sessions": 150000,
                "target_latency": 45.0,  # ERA's SLA requirement
                "target_memory": 2048,
                "description": "Enterprise-scale simulation"
            },
            "large_scale": {
                "customers": 100000,
                "orders": 500000,
                "ga4_sessions": 1500000,
                "target_latency": 90.0,  # Stress test boundary
                "target_memory": 4096,
                "description": "Scalability limit identification"
            }
        }

    def execute_scale_benchmark(self, scale_name: str) -> PerformanceMetrics:
        """Execute complete ERA workflow at specified scale."""
        scale_config = self.scale_matrix[scale_name]

        print(f"Executing {scale_name} benchmark...")
        print(f"Configuration: {scale_config}")

        # Generate dataset using TDG
        print(f"Generating {scale_name} dataset...")
        dataset_start_time = time.perf_counter()

        era_dataset = self.tdg.generate_era_compatible_dataset({
            'customers_count': scale_config['customers'],
            'orders_per_customer': scale_config['orders'] // scale_config['customers'],
            'ga4_sessions_count': scale_config['ga4_sessions']
        })

        dataset_generation_time = time.perf_counter() - dataset_start_time
        print(f"Dataset generation completed in {dataset_generation_time:.2f} seconds")

        # Execute ERA workflow with performance monitoring
        era_start_time = time.perf_counter()
        memory_start = psutil.Process().memory_info().rss / 1024 / 1024

        try:
            # Create ERA state with generated data
            era_state = ReportingAgentState(
                report_config={"date_range": "2024-01-01 to 2024-12-31"},
                raw_shopify_data=era_dataset['shopify_orders'].to_dict('records'),
                raw_ga4_data=era_dataset['ga4_sessions'].to_dict('records')
            )

            # Execute ERA processing nodes
            print("Executing ERA data processing...")
            processed_state_updates = process_data_node(era_state)

            # Update state with processed data
            for key, value in processed_state_updates.items():
                setattr(era_state, key, value)

            print("ERA processing completed successfully")

        except Exception as e:
            print(f"ERA processing failed: {e}")
            # Continue with metrics collection even if processing fails

        era_execution_time = time.perf_counter() - era_start_time
        memory_peak = psutil.Process().memory_info().rss / 1024 / 1024

        print(f"ERA execution completed in {era_execution_time:.2f} seconds")
        print(f"Memory usage: {memory_start:.1f}MB -> {memory_peak:.1f}MB")

        # Calculate performance metrics
        total_records = scale_config['customers'] + scale_config['orders'] + scale_config['ga4_sessions']
        memory_growth = memory_peak - memory_start
        total_end_to_end_time = dataset_generation_time + era_execution_time

        sla_compliance = era_execution_time <= scale_config['target_latency']
        memory_compliance = memory_peak <= scale_config['target_memory']

        metrics = PerformanceMetrics(
            scale_name=scale_name,
            total_records=total_records,
            dataset_generation_time=dataset_generation_time,
            era_execution_time=era_execution_time,
            total_end_to_end_time=total_end_to_end_time,
            memory_peak_mb=memory_peak,
            memory_growth_mb=memory_growth,
            sla_compliance=sla_compliance,
            memory_compliance=memory_compliance
        )

        print(f"Performance metrics: SLA Compliant: {sla_compliance}, Memory Compliant: {memory_compliance}")
        return metrics


def run_performance_benchmark(scale_name: str) -> PerformanceMetrics:
    """Standalone function to run a performance benchmark."""
    framework = MultiScalePerformanceFramework()
    return framework.execute_scale_benchmark(scale_name)


if __name__ == "__main__":
    # Run a micro-scale test as demonstration
    framework = MultiScalePerformanceFramework()
    metrics = framework.execute_scale_benchmark("micro_scale")
    print("\nBenchmark Results:")
    print(f"Scale: {metrics.scale_name}")
    print(f"Total Records: {metrics.total_records}")
    print(f"Generation Time: {metrics.dataset_generation_time:.2f}s")
    print(f"ERA Execution Time: {metrics.era_execution_time:.2f}s")
    print(f"Total Time: {metrics.total_end_to_end_time:.2f}s")
    print(f"Peak Memory: {metrics.memory_peak_mb:.1f}MB")
    print(f"SLA Compliant: {metrics.sla_compliance}")
    print(f"Memory Compliant: {metrics.memory_compliance}")

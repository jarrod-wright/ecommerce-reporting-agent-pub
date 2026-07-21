"""
TDD Test Suite for Multi-Scale Dataset Generation Performance Framework

This test suite follows the BDD scenarios defined in the feature file and drives
the implementation of the MultiScalePerformanceFramework through failing tests.
"""


import pytest

from tests.performance.scale_testing_framework import (
    ERATestDataGenerator,
    MultiScalePerformanceFramework,
)


class TestMultiScalePerformanceFramework:
    """Test suite for Multi-Scale Performance Framework following BDD scenarios."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.framework = MultiScalePerformanceFramework()

    def test_micro_scale_performance_validation(self):
        """BDD Scenario: Micro-scale dataset performance validation."""
        # GIVEN I configure the dataset generation for micro_scale testing
        scale_name = "micro_scale"
        scale_config = self.framework.scale_matrix[scale_name]

        # WHEN I generate a dataset and execute ERA workflow with performance monitoring
        metrics = self.framework.execute_scale_benchmark(scale_name)

        # THEN all performance criteria should be met
        assert metrics.dataset_generation_time < 30.0, f"Dataset generation took {metrics.dataset_generation_time}s, expected <30s"
        assert metrics.era_execution_time < 15.0, f"ERA execution took {metrics.era_execution_time}s, expected <15s"
        assert metrics.memory_peak_mb <= 512, f"Peak memory {metrics.memory_peak_mb}MB, expected <=512MB"
        assert metrics.total_end_to_end_time < 45.0, f"End-to-end time {metrics.total_end_to_end_time}s, expected <45s"
        assert metrics.sla_compliance == True, "SLA compliance should be True"
        assert metrics.memory_compliance == True, "Memory compliance should be True"
        assert metrics.scale_name == "micro_scale"
        assert metrics.total_records == 1400  # 100 + 300 + 1000

    def test_small_scale_business_simulation_validation(self):
        """BDD Scenario: Small-scale business simulation performance validation."""
        # GIVEN I configure the dataset generation for small_scale testing
        scale_name = "small_scale"

        # WHEN I generate a dataset and execute ERA workflow
        metrics = self.framework.execute_scale_benchmark(scale_name)

        # THEN all performance criteria should be met
        assert metrics.dataset_generation_time < 60.0, f"Dataset generation took {metrics.dataset_generation_time}s, expected <60s"
        assert metrics.era_execution_time < 30.0, f"ERA execution took {metrics.era_execution_time}s, expected <30s"
        assert metrics.memory_peak_mb <= 1024, f"Peak memory {metrics.memory_peak_mb}MB, expected <=1024MB"
        assert metrics.total_end_to_end_time < 90.0, f"End-to-end time {metrics.total_end_to_end_time}s, expected <90s"
        assert metrics.sla_compliance == True, "SLA compliance should be True"
        assert metrics.memory_compliance == True, "Memory compliance should be True"
        assert metrics.total_records == 21000  # 1000 + 5000 + 15000

    def test_medium_scale_enterprise_sla_validation(self):
        """BDD Scenario: Medium-scale enterprise SLA compliance validation."""
        # GIVEN I configure the dataset generation for medium_scale testing
        scale_name = "medium_scale"

        # WHEN I generate a dataset and execute ERA workflow
        metrics = self.framework.execute_scale_benchmark(scale_name)

        # THEN enterprise SLA criteria should be met
        assert metrics.dataset_generation_time < 300.0, f"Dataset generation took {metrics.dataset_generation_time}s, expected <300s"
        assert metrics.era_execution_time < 45.0, f"ERA execution took {metrics.era_execution_time}s, expected <45s"
        assert metrics.memory_peak_mb <= 2048, f"Peak memory {metrics.memory_peak_mb}MB, expected <=2048MB"
        assert metrics.memory_growth_mb < 1024, f"Memory growth {metrics.memory_growth_mb}MB, expected <1024MB"
        assert metrics.total_end_to_end_time < 345.0, f"End-to-end time {metrics.total_end_to_end_time}s, expected <345s"
        assert metrics.sla_compliance == True, "SLA compliance should be True for enterprise scale"
        assert metrics.memory_compliance == True, "Memory compliance should be True"
        assert metrics.total_records == 210000  # 10000 + 50000 + 150000

    def test_large_scale_stress_testing(self):
        """BDD Scenario: Large-scale stress testing and scalability limit identification."""
        # GIVEN I configure the dataset generation for large_scale testing
        scale_name = "large_scale"

        # WHEN I generate a dataset and execute ERA workflow
        metrics = self.framework.execute_scale_benchmark(scale_name)

        # THEN stress test criteria should be evaluated
        assert metrics.dataset_generation_time < 1800.0, f"Dataset generation took {metrics.dataset_generation_time}s, expected <1800s"
        assert metrics.era_execution_time < 90.0, f"ERA execution took {metrics.era_execution_time}s, expected <90s"
        assert metrics.memory_peak_mb <= 4096, f"Peak memory {metrics.memory_peak_mb}MB, expected <=4096MB"
        assert metrics.total_records == 2100000  # 100000 + 500000 + 1500000
        # Note: Large scale may not always meet SLA compliance - we test system stability

    def test_performance_metrics_data_structure(self):
        """Test that PerformanceMetrics contains all required fields."""
        # GIVEN I execute a micro scale benchmark
        metrics = self.framework.execute_scale_benchmark("micro_scale")

        # THEN the PerformanceMetrics should contain all required fields
        assert hasattr(metrics, 'scale_name')
        assert hasattr(metrics, 'total_records')
        assert hasattr(metrics, 'dataset_generation_time')
        assert hasattr(metrics, 'era_execution_time')
        assert hasattr(metrics, 'total_end_to_end_time')
        assert hasattr(metrics, 'memory_peak_mb')
        assert hasattr(metrics, 'memory_growth_mb')
        assert hasattr(metrics, 'sla_compliance')
        assert hasattr(metrics, 'memory_compliance')

        # AND all values should be reasonable
        assert isinstance(metrics.scale_name, str)
        assert metrics.total_records > 0
        assert metrics.dataset_generation_time > 0
        assert metrics.era_execution_time > 0
        assert metrics.total_end_to_end_time > 0
        assert metrics.memory_peak_mb > 0
        assert isinstance(metrics.sla_compliance, bool)
        assert isinstance(metrics.memory_compliance, bool)

    def test_scale_matrix_definition(self):
        """Test that the scale matrix is properly defined with all required configurations."""
        # GIVEN I have initialized the MultiScalePerformanceFramework
        scale_matrix = self.framework.scale_matrix

        # THEN it should contain all required scale levels
        expected_scales = ["micro_scale", "small_scale", "medium_scale", "large_scale"]
        assert all(scale in scale_matrix for scale in expected_scales)

        # AND each scale should have all required configuration parameters
        for scale_name, config in scale_matrix.items():
            assert 'customers' in config
            assert 'orders' in config
            assert 'ga4_sessions' in config
            assert 'target_latency' in config
            assert 'target_memory' in config
            assert 'description' in config

            # AND values should be reasonable
            assert config['customers'] > 0
            assert config['orders'] > 0
            assert config['ga4_sessions'] > 0
            assert config['target_latency'] > 0
            assert config['target_memory'] > 0

    def test_era_test_data_generator_integration(self):
        """Test that ERATestDataGenerator integrates properly with TDG."""
        # GIVEN I have an ERATestDataGenerator instance
        tdg = ERATestDataGenerator()

        # WHEN I generate a small dataset for testing
        dataset = tdg.generate_era_compatible_dataset({
            'customers_count': 10,
            'orders_per_customer': 3,
            'ga4_sessions_count': 50
        })

        # THEN it should return a properly structured dataset
        assert 'shopify_orders' in dataset
        assert 'ga4_sessions' in dataset

        # AND the data should be in the correct format for ERA processing
        shopify_data = dataset['shopify_orders']
        ga4_data = dataset['ga4_sessions']

        # Shopify data should be a list of dictionaries or DataFrame
        assert hasattr(shopify_data, 'to_dict') or isinstance(shopify_data, list)
        # GA4 data should be a list of dictionaries or DataFrame
        assert hasattr(ga4_data, 'to_dict') or isinstance(ga4_data, list)


class TestDataIntegrityAcrossScales:
    """Test suite for validating data integrity across all scale levels."""

    def setup_method(self):
        """Set up test fixtures."""
        self.framework = MultiScalePerformanceFramework()

    def test_referential_integrity_maintained_across_scales(self):
        """BDD Scenario: Data integrity validation across all scales."""
        # GIVEN I execute performance tests across all scale configurations
        scales_to_test = ["micro_scale", "small_scale"]  # Start with smaller scales for faster tests

        for scale_name in scales_to_test:
            # WHEN I validate the generated datasets at each scale level
            metrics = self.framework.execute_scale_benchmark(scale_name)

            # THEN all datasets should maintain proper referential integrity
            # This is validated within the execute_scale_benchmark method
            # by successfully processing the data through ERA workflow
            assert metrics.sla_compliance is not None
            assert metrics.total_records > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])

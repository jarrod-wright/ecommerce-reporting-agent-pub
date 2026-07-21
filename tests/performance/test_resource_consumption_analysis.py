"""
TDD Test Suite for Resource Consumption Analysis Framework

This test suite follows the BDD scenarios defined in the feature file and drives
the implementation of the ERAResourceProfiler through failing tests.
"""

import math

from monitoring.resource_profiler import (
    ERAResourceProfiler,
    OptimizationRecommendation,
    ResourceMetrics,
)
from tests.performance.scale_testing_framework import ERATestDataGenerator


class TestResourceConsumptionAnalysis:
    """Test suite for Resource Consumption Analysis Framework following BDD scenarios."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.profiler = ERAResourceProfiler()
        self.tdg = ERATestDataGenerator()

    def test_resource_metrics_data_structure(self):
        """Test that ResourceMetrics contains all required fields."""
        # GIVEN I have a ResourceMetrics instance with test data
        metrics = ResourceMetrics(
            execution_time=1.5,
            memory_growth_mb=50.0,
            cpu_utilization=15.5,
            memory_efficiency=0.25,
            bottleneck_indicator="low"
        )

        # THEN the ResourceMetrics should contain all required fields
        assert hasattr(metrics, 'execution_time')
        assert hasattr(metrics, 'memory_growth_mb')
        assert hasattr(metrics, 'cpu_utilization')
        assert hasattr(metrics, 'memory_efficiency')
        assert hasattr(metrics, 'bottleneck_indicator')

        # AND all values should be correct types
        assert isinstance(metrics.execution_time, float)
        assert isinstance(metrics.memory_growth_mb, float)
        assert isinstance(metrics.cpu_utilization, float)
        assert isinstance(metrics.memory_efficiency, float)
        assert isinstance(metrics.bottleneck_indicator, str)

    def test_optimization_recommendation_structure(self):
        """Test that OptimizationRecommendation contains all required fields."""
        # GIVEN I have an OptimizationRecommendation instance
        recommendation = OptimizationRecommendation(
            node_name="process_data",
            optimization_type="memory",
            description="Consider implementing data streaming",
            expected_improvement="30-50% memory reduction",
            implementation_effort="Medium"
        )

        # THEN it should contain all required fields
        assert hasattr(recommendation, 'node_name')
        assert hasattr(recommendation, 'optimization_type')
        assert hasattr(recommendation, 'description')
        assert hasattr(recommendation, 'expected_improvement')
        assert hasattr(recommendation, 'implementation_effort')

        # AND values should be correct types
        assert isinstance(recommendation.node_name, str)
        assert isinstance(recommendation.optimization_type, str)
        assert isinstance(recommendation.description, str)

    def test_era_resource_profiler_initialization(self):
        """Test that ERAResourceProfiler initializes correctly."""
        # GIVEN I initialize an ERAResourceProfiler
        profiler = ERAResourceProfiler()

        # THEN it should have required methods
        assert hasattr(profiler, 'profile_era_workflow_stages')
        assert hasattr(profiler, 'identify_optimization_opportunities')
        assert hasattr(profiler, 'generate_scale_dataset')
        assert hasattr(profiler, 'create_initial_state')

    def test_micro_scale_era_node_profiling(self):
        """BDD Scenario: Individual ERA node resource profiling with micro-scale dataset."""
        # GIVEN I configure the resource profiler for micro_scale testing
        dataset_scale = "micro_scale"

        # WHEN I execute resource profiling across all ERA workflow stages
        profiling_results = self.profiler.profile_era_workflow_stages(dataset_scale)

        # THEN profiling results should contain all expected ERA nodes
        expected_nodes = ["fetch_data_simulation", "process_data", "generate_insights",
                         "generate_visualizations", "compile_report"]

        for node_name in expected_nodes:
            assert node_name in profiling_results
            metrics = profiling_results[node_name]

            # AND each node should have valid ResourceMetrics
            assert isinstance(metrics, ResourceMetrics)
            assert metrics.execution_time > 0
            # Memory growth can be negative when GC frees memory during profiling
            assert math.isfinite(metrics.memory_growth_mb)
            assert isinstance(metrics.bottleneck_indicator, str)

        # AND specific performance criteria should be met for micro-scale
        # fetch_data_simulation should be fast and low-memory
        fetch_metrics = profiling_results["fetch_data_simulation"]
        assert fetch_metrics.execution_time < 1.0, f"fetch_data took {fetch_metrics.execution_time}s, expected <1s"
        assert fetch_metrics.memory_growth_mb < 50, f"fetch_data used {fetch_metrics.memory_growth_mb}MB, expected <50MB"

        # process_data should be reasonably fast
        process_metrics = profiling_results["process_data"]
        assert process_metrics.execution_time < 5.0, f"process_data took {process_metrics.execution_time}s, expected <5s"
        assert process_metrics.memory_growth_mb < 100, f"process_data used {process_metrics.memory_growth_mb}MB, expected <100MB"

    def test_bottleneck_identification_and_recommendations(self):
        """BDD Scenario: Bottleneck identification and optimization recommendation generation."""
        # GIVEN I have executed resource profiling
        profiling_results = self.profiler.profile_era_workflow_stages("micro_scale")

        # WHEN I analyze the profiling results for bottleneck identification
        recommendations = self.profiler.identify_optimization_opportunities(profiling_results)

        # THEN optimization recommendations should be generated
        assert isinstance(recommendations, list)

        # AND each recommendation should have required fields
        for rec in recommendations:
            assert isinstance(rec, OptimizationRecommendation)
            assert rec.node_name in ["fetch_data_simulation", "process_data", "generate_insights",
                                   "generate_visualizations", "compile_report"]
            assert rec.optimization_type in ["memory", "latency", "cpu"]
            assert len(rec.description) > 0
            assert len(rec.expected_improvement) > 0
            assert rec.implementation_effort in ["Low", "Medium", "High"]

    def test_resource_profiler_dataset_generation(self):
        """Test that resource profiler can generate datasets using TDG integration."""
        # GIVEN I have a resource profiler instance
        profiler = self.profiler

        # WHEN I generate a scale dataset for testing
        era_dataset = profiler.generate_scale_dataset("micro_scale")

        # THEN it should return properly structured ERA-compatible data
        assert 'shopify_orders' in era_dataset
        assert 'ga4_sessions' in era_dataset

        # AND the data should be suitable for ERA processing
        shopify_data = era_dataset['shopify_orders']
        ga4_data = era_dataset['ga4_sessions']

        assert len(shopify_data) > 0
        assert len(ga4_data) > 0

    def test_era_state_creation_for_profiling(self):
        """Test that profiler can create initial ERA state for workflow execution."""
        # GIVEN I have a resource profiler with test dataset
        era_dataset = self.profiler.generate_scale_dataset("micro_scale")

        # WHEN I create an initial ERA state
        initial_state = self.profiler.create_initial_state(era_dataset)

        # THEN the state should be properly configured for ERA workflow
        assert hasattr(initial_state, 'report_config')
        assert hasattr(initial_state, 'raw_shopify_data')
        assert hasattr(initial_state, 'raw_ga4_data')

        # AND it should contain the generated data
        assert initial_state.raw_shopify_data is not None
        assert initial_state.raw_ga4_data is not None
        assert len(initial_state.raw_shopify_data) > 0
        assert len(initial_state.raw_ga4_data) > 0


class TestCrossScaleResourceAnalysis:
    """Test suite for cross-scale resource consumption analysis."""

    def setup_method(self):
        """Set up test fixtures."""
        self.profiler = ERAResourceProfiler()

    def test_medium_scale_resource_profiling(self):
        """BDD Scenario: Resource consumption analysis under medium-scale load."""
        # GIVEN I configure the resource profiler for medium_scale testing
        dataset_scale = "medium_scale"

        # WHEN I execute comprehensive resource profiling
        profiling_results = self.profiler.profile_era_workflow_stages(dataset_scale)

        # THEN the profiling should complete successfully
        assert len(profiling_results) > 0

        # AND process_data stage should handle larger datasets efficiently
        if "process_data" in profiling_results:
            process_metrics = profiling_results["process_data"]
            assert process_metrics.execution_time < 10.0, f"process_data took {process_metrics.execution_time}s, expected <10s"
            assert process_metrics.memory_growth_mb < 300, f"process_data used {process_metrics.memory_growth_mb}MB, expected <300MB"


if __name__ == "__main__":
    # Run basic tests without pytest
    print("🧪 Running Resource Consumption Analysis Tests")

    test_suite = TestResourceConsumptionAnalysis()

    try:
        test_suite.setup_method()
        test_suite.test_resource_metrics_data_structure()
        print("✅ test_resource_metrics_data_structure PASSED")

        test_suite.test_optimization_recommendation_structure()
        print("✅ test_optimization_recommendation_structure PASSED")

        test_suite.test_era_resource_profiler_initialization()
        print("✅ test_era_resource_profiler_initialization PASSED")

        print("🎉 Basic structure tests passed! Ready to implement framework.")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("📝 This is expected - we're in RED phase of TDD!")

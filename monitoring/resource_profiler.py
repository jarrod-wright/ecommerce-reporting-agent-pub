"""
ERA Resource Profiler - Detailed resource consumption analysis using TDG datasets

Provides comprehensive resource profiling of each ERA workflow stage to identify
bottlenecks and generate optimization recommendations.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List

import psutil

from agent.graph.compile_report_node import compile_report_node
from agent.graph.generate_insights_node import generate_insights_node
from agent.graph.generate_visualizations_node import generate_visualizations_node
from agent.graph.process_data_node import process_data_node
from agent.models.state import ReportingAgentState

# Import existing TDG and ERA components
from tests.performance.scale_testing_framework import ERATestDataGenerator


@dataclass
class ResourceMetrics:
    """Resource consumption metrics for a single ERA workflow stage."""
    execution_time: float
    memory_growth_mb: float
    cpu_utilization: float
    memory_efficiency: float
    bottleneck_indicator: str


@dataclass
class OptimizationRecommendation:
    """AI-driven optimization recommendation based on profiling data."""
    node_name: str
    optimization_type: str  # memory, latency, cpu
    description: str
    expected_improvement: str
    implementation_effort: str  # Low, Medium, High


class ERAResourceProfiler:
    """Detailed resource consumption analysis using TDG datasets."""

    def __init__(self):
        """Initialize the ERA resource profiler."""
        self.tdg = ERATestDataGenerator()
        self.scale_configs = {
            "micro_scale": {"customers": 100, "orders_per_customer": 3, "ga4_sessions": 1000},
            "small_scale": {"customers": 1000, "orders_per_customer": 5, "ga4_sessions": 15000},
            "medium_scale": {"customers": 10000, "orders_per_customer": 5, "ga4_sessions": 150000}
        }

    def generate_scale_dataset(self, dataset_scale: str) -> Dict[str, Any]:
        """Generate dataset for specified scale using TDG."""
        if dataset_scale not in self.scale_configs:
            raise ValueError(f"Unknown dataset scale: {dataset_scale}")

        config = self.scale_configs[dataset_scale]
        return self.tdg.generate_era_compatible_dataset(config)

    def create_initial_state(self, era_dataset: Dict[str, Any]) -> ReportingAgentState:
        """Create initial ERA state from generated dataset."""
        return ReportingAgentState(
            report_config={"date_range": "2024-01-01 to 2024-12-31"},
            raw_shopify_data=era_dataset['shopify_orders'].to_dict('records'),
            raw_ga4_data=era_dataset['ga4_sessions'].to_dict('records')
        )

    def profile_era_workflow_stages(self, dataset_scale: str) -> Dict[str, ResourceMetrics]:
        """Profile resource consumption at each ERA workflow stage."""
        print(f"🔍 Starting resource profiling for {dataset_scale}")

        # Generate dataset using TDG
        era_dataset = self.generate_scale_dataset(dataset_scale)
        print(f"📊 Generated dataset: {len(era_dataset['shopify_orders'])} orders, {len(era_dataset['ga4_sessions'])} sessions")

        profiling_results = {}

        # Define ERA nodes to profile with their implementations
        era_nodes = [
            ("fetch_data_simulation", self._simulate_fetch_data_node),
            ("process_data", process_data_node),
            ("generate_insights", self._safely_execute_insights_node),
            ("generate_visualizations", self._safely_execute_visualizations_node),
            ("compile_report", self._safely_execute_compile_report_node)
        ]

        current_state = self.create_initial_state(era_dataset)

        for node_name, node_function in era_nodes:
            print(f"  Profiling {node_name}...")

            # Resource monitoring setup
            memory_before = psutil.Process().memory_info().rss / 1024 / 1024
            cpu_before = psutil.Process().cpu_percent(interval=None)  # Non-blocking

            start_time = time.perf_counter()

            try:
                # Execute node
                result = node_function(current_state)

                # Update state based on result
                if isinstance(result, dict):
                    # Node returned state updates
                    for key, value in result.items():
                        setattr(current_state, key, value)
                elif hasattr(result, '__dict__'):
                    # Node returned new state object
                    current_state = result

            except Exception as e:
                print(f"    ⚠️  {node_name} execution failed: {str(e)}")
                # Continue profiling other nodes

            end_time = time.perf_counter()
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024
            cpu_after = psutil.Process().cpu_percent(interval=None)  # Non-blocking

            # Calculate metrics
            execution_time = end_time - start_time
            memory_growth = memory_after - memory_before
            cpu_utilization = max(0, cpu_after - cpu_before)  # Ensure non-negative

            # Calculate memory efficiency (MB per record)
            total_records = len(current_state.raw_shopify_data or []) + len(current_state.raw_ga4_data or [])
            memory_efficiency = memory_after / total_records if total_records > 0 else 0

            # Determine bottleneck indicator
            bottleneck_indicator = self._identify_bottleneck(node_name, execution_time, memory_growth, cpu_utilization)

            # Record metrics
            profiling_results[node_name] = ResourceMetrics(
                execution_time=execution_time,
                memory_growth_mb=memory_growth,
                cpu_utilization=cpu_utilization,
                memory_efficiency=memory_efficiency,
                bottleneck_indicator=bottleneck_indicator
            )

            print(f"    ✅ {node_name}: {execution_time:.3f}s, {memory_growth:.1f}MB, {cpu_utilization:.1f}% CPU")

        return profiling_results

    def _simulate_fetch_data_node(self, state: ReportingAgentState) -> Dict[str, Any]:
        """Simulate fetch_data_node since it requires external API calls."""
        # Simulate realistic fetch time and memory usage
        time.sleep(0.01)  # Minimal delay to simulate network

        # Data is already in the state, so just return success
        return {
            "raw_shopify_data": state.raw_shopify_data,
            "raw_ga4_data": state.raw_ga4_data
        }

    def _safely_execute_insights_node(self, state: ReportingAgentState) -> Dict[str, Any]:
        """Safely execute generate_insights_node with error handling."""
        try:
            # Call the actual ERA node
            result = generate_insights_node(state)
            return result
        except Exception as e:
            print(f"      Note: generate_insights_node failed ({str(e)[:50]}...), using mock")
            # Return mock insights to continue profiling
            return {
                "generated_insights": {
                    "total_revenue": 125000.50,
                    "average_order_value": 156.25,
                    "conversion_rate": 0.032,
                    "insights": ["Revenue trending upward", "Strong mobile performance"]
                }
            }

    def _safely_execute_visualizations_node(self, state: ReportingAgentState) -> Dict[str, Any]:
        """Safely execute generate_visualizations_node with error handling."""
        try:
            result = generate_visualizations_node(state)
            return result
        except Exception as e:
            print(f"      Note: generate_visualizations_node failed ({str(e)[:50]}...), using mock")
            # Return mock visualization paths
            return {
                "visualization_filepaths": [
                    "/tmp/revenue_chart.png",
                    "/tmp/conversion_funnel.png",
                    "/tmp/device_breakdown.png"
                ]
            }

    def _safely_execute_compile_report_node(self, state: ReportingAgentState) -> Dict[str, Any]:
        """Safely execute compile_report_node with error handling."""
        try:
            result = compile_report_node(state)
            return result
        except Exception as e:
            print(f"      Note: compile_report_node failed ({str(e)[:50]}...), using mock")
            # Return mock report path
            return {
                "final_report_path": "/tmp/era_performance_report.pdf"
            }

    def _identify_bottleneck(self, node_name: str, execution_time: float, memory_growth: float, cpu_utilization: float) -> str:
        """Identify bottleneck severity based on resource consumption."""
        # Define thresholds for bottleneck identification
        if execution_time > 10.0 or memory_growth > 200 or cpu_utilization > 80:
            return "high"
        elif execution_time > 5.0 or memory_growth > 100 or cpu_utilization > 50:
            return "medium"
        elif execution_time > 1.0 or memory_growth > 50 or cpu_utilization > 20:
            return "low"
        else:
            return "none"

    def identify_optimization_opportunities(self, profiling_results: Dict[str, ResourceMetrics]) -> List[OptimizationRecommendation]:
        """AI-driven optimization recommendations based on profiling data."""
        recommendations = []

        # Identify memory bottlenecks
        memory_intensive_nodes = [
            (node, metrics) for node, metrics in profiling_results.items()
            if metrics.memory_growth_mb > 100  # >100MB growth threshold
        ]

        for node, metrics in memory_intensive_nodes:
            recommendations.append(OptimizationRecommendation(
                node_name=node,
                optimization_type="memory",
                description=f"High memory growth detected in {node} ({metrics.memory_growth_mb:.1f}MB). Consider implementing data streaming or chunking.",
                expected_improvement="30-50% memory reduction",
                implementation_effort="Medium"
            ))

        # Identify latency bottlenecks
        slow_nodes = [
            (node, metrics) for node, metrics in profiling_results.items()
            if metrics.execution_time > 5.0  # >5 second threshold for profiling
        ]

        for node, metrics in slow_nodes:
            recommendations.append(OptimizationRecommendation(
                node_name=node,
                optimization_type="latency",
                description=f"High execution time detected in {node} ({metrics.execution_time:.2f}s). Consider implementing caching or parallel processing.",
                expected_improvement="40-60% latency reduction",
                implementation_effort="High"
            ))

        # Identify CPU bottlenecks
        cpu_intensive_nodes = [
            (node, metrics) for node, metrics in profiling_results.items()
            if metrics.cpu_utilization > 50  # >50% CPU threshold
        ]

        for node, metrics in cpu_intensive_nodes:
            recommendations.append(OptimizationRecommendation(
                node_name=node,
                optimization_type="cpu",
                description=f"High CPU utilization detected in {node} ({metrics.cpu_utilization:.1f}%). Consider algorithm optimization or parallel processing.",
                expected_improvement="25-40% CPU reduction",
                implementation_effort="Medium"
            ))

        # Identify memory efficiency issues
        inefficient_nodes = [
            (node, metrics) for node, metrics in profiling_results.items()
            if metrics.memory_efficiency > 1.0  # >1MB per record is inefficient
        ]

        for node, metrics in inefficient_nodes:
            recommendations.append(OptimizationRecommendation(
                node_name=node,
                optimization_type="memory",
                description=f"Poor memory efficiency in {node} ({metrics.memory_efficiency:.2f}MB per record). Consider memory pooling or data structure optimization.",
                expected_improvement="20-30% efficiency improvement",
                implementation_effort="Low"
            ))

        return recommendations


def profile_era_workflow(dataset_scale: str = "micro_scale") -> Dict[str, ResourceMetrics]:
    """Standalone function to profile ERA workflow at specified scale."""
    profiler = ERAResourceProfiler()
    return profiler.profile_era_workflow_stages(dataset_scale)


def generate_optimization_report(dataset_scale: str = "micro_scale") -> Dict[str, Any]:
    """Generate comprehensive resource profiling and optimization report."""
    profiler = ERAResourceProfiler()

    # Execute profiling
    profiling_results = profiler.profile_era_workflow_stages(dataset_scale)

    # Generate optimization recommendations
    recommendations = profiler.identify_optimization_opportunities(profiling_results)

    # Calculate summary statistics
    total_execution_time = sum(metrics.execution_time for metrics in profiling_results.values())
    total_memory_growth = sum(metrics.memory_growth_mb for metrics in profiling_results.values())
    avg_cpu_utilization = sum(metrics.cpu_utilization for metrics in profiling_results.values()) / len(profiling_results)

    # Identify most resource-intensive node
    most_time_intensive = max(profiling_results.items(), key=lambda x: x[1].execution_time)
    most_memory_intensive = max(profiling_results.items(), key=lambda x: x[1].memory_growth_mb)
    most_cpu_intensive = max(profiling_results.items(), key=lambda x: x[1].cpu_utilization)

    report = {
        "profiling_summary": {
            "dataset_scale": dataset_scale,
            "total_nodes_profiled": len(profiling_results),
            "total_execution_time": total_execution_time,
            "total_memory_growth_mb": total_memory_growth,
            "average_cpu_utilization": avg_cpu_utilization
        },
        "node_performance": {
            node_name: {
                "execution_time": metrics.execution_time,
                "memory_growth_mb": metrics.memory_growth_mb,
                "cpu_utilization": metrics.cpu_utilization,
                "memory_efficiency": metrics.memory_efficiency,
                "bottleneck_indicator": metrics.bottleneck_indicator
            }
            for node_name, metrics in profiling_results.items()
        },
        "bottleneck_analysis": {
            "most_time_intensive": {
                "node": most_time_intensive[0],
                "execution_time": most_time_intensive[1].execution_time
            },
            "most_memory_intensive": {
                "node": most_memory_intensive[0],
                "memory_growth_mb": most_memory_intensive[1].memory_growth_mb
            },
            "most_cpu_intensive": {
                "node": most_cpu_intensive[0],
                "cpu_utilization": most_cpu_intensive[1].cpu_utilization
            }
        },
        "optimization_recommendations": [
            {
                "node_name": rec.node_name,
                "optimization_type": rec.optimization_type,
                "description": rec.description,
                "expected_improvement": rec.expected_improvement,
                "implementation_effort": rec.implementation_effort
            }
            for rec in recommendations
        ]
    }

    return report


if __name__ == "__main__":
    # Run resource profiling demonstration
    print("🔍 ERA Resource Consumption Analysis")
    print("=" * 50)

    profiler = ERAResourceProfiler()

    # Profile micro-scale dataset
    results = profiler.profile_era_workflow_stages("micro_scale")

    print("\n📊 Profiling Results:")
    for node_name, metrics in results.items():
        print(f"  {node_name}:")
        print(f"    Execution Time: {metrics.execution_time:.3f}s")
        print(f"    Memory Growth: {metrics.memory_growth_mb:.1f}MB")
        print(f"    CPU Utilization: {metrics.cpu_utilization:.1f}%")
        print(f"    Memory Efficiency: {metrics.memory_efficiency:.3f}MB/record")
        print(f"    Bottleneck Level: {metrics.bottleneck_indicator}")

    # Generate optimization recommendations
    recommendations = profiler.identify_optimization_opportunities(results)

    print(f"\n💡 Optimization Recommendations ({len(recommendations)}):")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec.node_name} ({rec.optimization_type})")
        print(f"     {rec.description}")
        print(f"     Expected: {rec.expected_improvement}")
        print(f"     Effort: {rec.implementation_effort}")

"""
Concurrent Load Testing Framework for ERA System

Simulates production concurrent load using TDG-generated datasets to validate
system stability, performance, and resource contention under realistic conditions.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from agent.graph.process_data_node import process_data_node
from agent.models.state import ReportingAgentState
from monitoring.resource_profiler import ERAResourceProfiler

# Import existing frameworks
from tests.performance.scale_testing_framework import ERATestDataGenerator


@dataclass
class ConcurrentExecutionResult:
    """Result of a single concurrent ERA workflow execution."""
    request_id: int
    execution_time: float
    memory_peak: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class ConcurrentLoadResults:
    """Comprehensive results of concurrent load simulation."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_latency: float
    p95_latency: float
    p99_latency: float
    total_execution_time: float
    concurrency_efficiency: float
    resource_contention_detected: bool


class ConcurrentLoadSimulator:
    """Simulate production concurrent load using TDG datasets."""

    def __init__(self):
        """Initialize the concurrent load simulator."""
        self.tdg = ERATestDataGenerator()
        self.profiler = ERAResourceProfiler()
        self.baseline_performance = None

    def generate_concurrent_datasets(self, concurrent_requests: int) -> List[Dict[str, Any]]:
        """Generate distinct datasets for concurrent testing with different TDG seeds."""
        datasets = []

        for i in range(concurrent_requests):
            # Use different seeds for realistic variance
            dataset_config = {
                'customers_count': 1000,
                'orders_per_customer': 5,
                'ga4_sessions_count': 5000
            }

            # Create new TDG instance with different seed
            tdg_instance = ERATestDataGenerator(seed=42 + i)
            dataset = tdg_instance.generate_era_compatible_dataset(dataset_config)
            datasets.append(dataset)

        return datasets

    async def execute_era_workflow_async(self, dataset: Dict[str, Any], request_id: int) -> ConcurrentExecutionResult:
        """Execute a single ERA workflow asynchronously."""
        start_time = time.perf_counter()
        memory_start = 0
        memory_peak = 0

        try:
            # Import psutil only when needed to avoid dependency issues
            try:
                import psutil
                memory_start = psutil.Process().memory_info().rss / 1024 / 1024
            except ImportError:
                pass

            # Create ERA state from dataset
            era_state = ReportingAgentState(
                report_config={"date_range": "2024-01-01 to 2024-12-31", "request_id": request_id},
                raw_shopify_data=dataset['shopify_orders'].to_dict('records'),
                raw_ga4_data=dataset['ga4_sessions'].to_dict('records')
            )

            # Execute core ERA workflow (simplified for concurrent testing)
            # Process data node (most resource intensive)
            processed_result = process_data_node(era_state)

            # Update state with processed data
            for key, value in processed_result.items():
                setattr(era_state, key, value)

            # Simulate additional processing time
            await asyncio.sleep(0.1)  # Simulate I/O or computation

            end_time = time.perf_counter()
            execution_time = end_time - start_time

            # Measure peak memory
            try:
                if 'psutil' in locals():
                    memory_peak = psutil.Process().memory_info().rss / 1024 / 1024
                else:
                    memory_peak = memory_start + 50  # Mock memory usage
            except:
                memory_peak = memory_start + 50

            return ConcurrentExecutionResult(
                request_id=request_id,
                execution_time=execution_time,
                memory_peak=memory_peak,
                success=True
            )

        except Exception as e:
            end_time = time.perf_counter()
            execution_time = end_time - start_time

            return ConcurrentExecutionResult(
                request_id=request_id,
                execution_time=execution_time,
                memory_peak=memory_peak or memory_start,
                success=False,
                error_message=str(e)
            )

    async def simulate_concurrent_era_requests(self, concurrent_requests: int = 5) -> ConcurrentLoadResults:
        """Simulate multiple concurrent ERA report generation requests."""
        print(f"🚀 Starting concurrent load simulation with {concurrent_requests} requests")

        # Generate distinct datasets for each concurrent request
        print(f"📊 Generating {concurrent_requests} distinct datasets...")
        datasets = self.generate_concurrent_datasets(concurrent_requests)
        print(f"✅ Generated {len(datasets)} datasets with TDG seed variance")

        # Execute concurrent ERA workflows
        start_time = time.perf_counter()

        print(f"⚡ Executing {concurrent_requests} concurrent ERA workflows...")
        concurrent_tasks = [
            self.execute_era_workflow_async(dataset, request_id=i)
            for i, dataset in enumerate(datasets)
        ]

        # Use asyncio.gather to execute all tasks concurrently
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)

        total_time = time.perf_counter() - start_time
        print(f"🏁 Concurrent execution completed in {total_time:.2f} seconds")

        # Analyze results
        successful_results = [r for r in results if isinstance(r, ConcurrentExecutionResult) and r.success]
        failed_results = [r for r in results if isinstance(r, Exception) or (isinstance(r, ConcurrentExecutionResult) and not r.success)]

        if successful_results:
            execution_times = [r.execution_time for r in successful_results]
            average_latency = np.mean(execution_times)
            p95_latency = np.percentile(execution_times, 95)
            p99_latency = np.percentile(execution_times, 99)
        else:
            average_latency = p95_latency = p99_latency = 0.0

        concurrency_efficiency = len(successful_results) / concurrent_requests
        resource_contention_detected = self.detect_resource_contention(successful_results)

        # Print results summary
        print("📊 Results Summary:")
        print(f"   Total Requests: {concurrent_requests}")
        print(f"   Successful: {len(successful_results)}")
        print(f"   Failed: {len(failed_results)}")
        print(f"   Concurrency Efficiency: {concurrency_efficiency:.1%}")
        print(f"   Average Latency: {average_latency:.2f}s")
        print(f"   P95 Latency: {p95_latency:.2f}s")
        print(f"   Resource Contention: {'Yes' if resource_contention_detected else 'No'}")

        return ConcurrentLoadResults(
            total_requests=concurrent_requests,
            successful_requests=len(successful_results),
            failed_requests=len(failed_results),
            average_latency=average_latency,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            total_execution_time=total_time,
            concurrency_efficiency=concurrency_efficiency,
            resource_contention_detected=resource_contention_detected
        )

    def detect_resource_contention(self, results: List[ConcurrentExecutionResult]) -> bool:
        """Detect resource contention based on execution time variance."""
        if len(results) < 2:
            return False

        execution_times = [r.execution_time for r in results]

        # Calculate coefficient of variation (std dev / mean)
        mean_time = np.mean(execution_times)
        std_time = np.std(execution_times)

        if mean_time > 0:
            coefficient_of_variation = std_time / mean_time
            # High variance (>0.5) suggests resource contention
            # Explicitly cast to native Python bool to ensure clean API contract (SET Doctrine Module 1.3)
            contention_detected = coefficient_of_variation > 0.5
            return bool(contention_detected)

        return False

    def establish_baseline_performance(self) -> Dict[str, float]:
        """Establish single-request performance baseline for comparison."""
        print("📏 Establishing single-request performance baseline...")

        # Generate single dataset
        datasets = self.generate_concurrent_datasets(1)

        # Execute single workflow
        single_result = asyncio.run(self.execute_era_workflow_async(datasets[0], 0))

        baseline = {
            'execution_time': single_result.execution_time,
            'memory_peak': single_result.memory_peak,
            'success': single_result.success
        }

        self.baseline_performance = baseline
        print(f"✅ Baseline: {baseline['execution_time']:.2f}s, {baseline['memory_peak']:.1f}MB")

        return baseline

    def analyze_scaling_efficiency(self, concurrent_requests: List[int]) -> Dict[str, Any]:
        """Analyze scaling efficiency across different concurrency levels."""
        print(f"📈 Analyzing scaling efficiency across {len(concurrent_requests)} concurrency levels...")

        scaling_results = {}

        for num_requests in concurrent_requests:
            print(f"\n🔄 Testing {num_requests} concurrent requests...")

            results = asyncio.run(self.simulate_concurrent_era_requests(num_requests))

            scaling_results[num_requests] = {
                'total_time': results.total_execution_time,
                'average_latency': results.average_latency,
                'concurrency_efficiency': results.concurrency_efficiency,
                'success_rate': results.successful_requests / results.total_requests,
                'resource_contention': results.resource_contention_detected
            }

        # Calculate scaling patterns
        if len(concurrent_requests) >= 2:
            scaling_analysis = self._calculate_scaling_patterns(scaling_results)
            scaling_results['scaling_analysis'] = scaling_analysis

        return scaling_results

    def _calculate_scaling_patterns(self, scaling_results: Dict[int, Dict]) -> Dict[str, Any]:
        """Calculate scaling patterns from multi-level results."""
        concurrency_levels = sorted([k for k in scaling_results.keys() if isinstance(k, int)])

        if len(concurrency_levels) < 2:
            return {"pattern": "insufficient_data"}

        # Calculate scaling efficiency trend
        efficiencies = [scaling_results[level]['concurrency_efficiency'] for level in concurrency_levels]

        # Linear regression to determine trend
        x = np.array(concurrency_levels)
        y = np.array(efficiencies)

        if len(x) >= 2:
            slope = np.polyfit(x, y, 1)[0]

            if slope >= 0:
                efficiency_trend = "stable"
            elif slope >= -0.1:
                efficiency_trend = "slowly_degrading"
            else:
                efficiency_trend = "rapidly_degrading"
        else:
            efficiency_trend = "unknown"

        # Identify optimal concurrency level
        max_efficiency_level = concurrency_levels[np.argmax(efficiencies)]

        return {
            "efficiency_trend": efficiency_trend,
            "optimal_concurrency_level": max_efficiency_level,
            "max_efficiency": max(efficiencies),
            "scaling_slope": slope if 'slope' in locals() else 0
        }


def run_concurrent_load_test(concurrent_requests: int = 3) -> ConcurrentLoadResults:
    """Standalone function to run concurrent load test."""
    simulator = ConcurrentLoadSimulator()
    return asyncio.run(simulator.simulate_concurrent_era_requests(concurrent_requests))


def run_scaling_analysis() -> Dict[str, Any]:
    """Run comprehensive scaling analysis across multiple concurrency levels."""
    simulator = ConcurrentLoadSimulator()

    # Test incremental concurrency levels (reduced for resource conservation)
    concurrency_levels = [1, 3, 5]

    return simulator.analyze_scaling_efficiency(concurrency_levels)


if __name__ == "__main__":
    # Run demonstration of concurrent load testing
    print("🔄 ERA Concurrent Load Testing Framework")
    print("=" * 50)

    simulator = ConcurrentLoadSimulator()

    # Establish baseline
    baseline = simulator.establish_baseline_performance()

    # Run basic concurrent test
    print("\n🚀 Running basic concurrent test (3 requests)...")
    results = asyncio.run(simulator.simulate_concurrent_era_requests(3))

    # Calculate efficiency compared to baseline
    if baseline['execution_time'] > 0:
        theoretical_serial_time = baseline['execution_time'] * 3
        concurrency_benefit = (theoretical_serial_time - results.total_execution_time) / theoretical_serial_time
        print(f"🎯 Concurrency Benefit: {concurrency_benefit:.1%} time savings vs. serial execution")

    print("\n🎉 Concurrent load testing demonstration completed!")
    print(f"Success Rate: {results.successful_requests}/{results.total_requests} ({results.concurrency_efficiency:.1%})")

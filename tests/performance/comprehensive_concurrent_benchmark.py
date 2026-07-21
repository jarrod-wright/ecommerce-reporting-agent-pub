"""
Comprehensive Concurrent Load Benchmark Suite

Executes complete concurrent load testing with detailed analysis and reporting.
"""

import asyncio
import json
import time
from typing import Any, Dict, List

from tests.performance.concurrent_load_testing import ConcurrentLoadSimulator


class ComprehensiveConcurrentBenchmark:
    """Execute comprehensive concurrent load benchmarking with detailed reporting."""

    def __init__(self):
        """Initialize the comprehensive concurrent benchmark suite."""
        self.simulator = ConcurrentLoadSimulator()
        self.results = []

    def execute_concurrent_benchmarks(self) -> Dict[str, Any]:
        """Execute concurrent benchmarks across multiple scenarios."""
        print("🚀 Starting Comprehensive Concurrent Load Benchmark Suite")
        print("=" * 80)

        # Define test scenarios (conservative for resource management)
        test_scenarios = [
            {"name": "baseline", "concurrent_requests": 1, "description": "Single request baseline"},
            {"name": "light_load", "concurrent_requests": 3, "description": "Light concurrent load"},
            {"name": "moderate_load", "concurrent_requests": 5, "description": "Moderate concurrent load"}
        ]

        benchmark_results = []

        for scenario in test_scenarios:
            print(f"\n📊 Executing {scenario['name'].upper()} Scenario")
            print(f"Description: {scenario['description']}")
            print("-" * 60)

            try:
                start_time = time.time()

                # Execute concurrent load test
                results = asyncio.run(
                    self.simulator.simulate_concurrent_era_requests(
                        scenario['concurrent_requests']
                    )
                )

                end_time = time.time()

                # Store results with scenario metadata
                scenario_result = {
                    "scenario_name": scenario['name'],
                    "scenario_description": scenario['description'],
                    "concurrent_requests": scenario['concurrent_requests'],
                    "benchmark_time": end_time - start_time,
                    "results": results
                }

                benchmark_results.append(scenario_result)

                # Print scenario summary
                self._print_scenario_summary(scenario_result)

                if results.concurrency_efficiency >= 0.8:
                    print(f"✅ {scenario['name'].upper()} EXCELLENT - High efficiency achieved")
                elif results.concurrency_efficiency >= 0.6:
                    print(f"👍 {scenario['name'].upper()} GOOD - Acceptable efficiency")
                else:
                    print(f"⚠️  {scenario['name'].upper()} ATTENTION - Efficiency below optimal")

            except Exception as e:
                print(f"❌ {scenario['name'].upper()} FAILED: {str(e)}")
                continue

        # Generate comprehensive analysis
        comprehensive_analysis = self._generate_comprehensive_analysis(benchmark_results)

        return {
            "individual_scenarios": benchmark_results,
            "comprehensive_analysis": comprehensive_analysis,
            "benchmark_metadata": {
                "scenarios_executed": len(benchmark_results),
                "total_concurrent_requests_tested": sum(s["concurrent_requests"] for s in benchmark_results),
                "benchmark_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "framework_version": "ERA-ALPHA-2.3"
            }
        }

    def _print_scenario_summary(self, scenario_result: Dict[str, Any]):
        """Print detailed summary for a single scenario."""
        results = scenario_result["results"]

        print(f"   Concurrent Requests: {scenario_result['concurrent_requests']}")
        print(f"   Total Execution Time: {results.total_execution_time:.2f}s")
        print(f"   Successful Requests: {results.successful_requests}/{results.total_requests}")
        print(f"   Success Rate: {(results.successful_requests/results.total_requests)*100:.1f}%")
        print(f"   Concurrency Efficiency: {results.concurrency_efficiency:.1%}")
        print(f"   Average Latency: {results.average_latency:.2f}s")
        print(f"   P95 Latency: {results.p95_latency:.2f}s")
        print(f"   P99 Latency: {results.p99_latency:.2f}s")
        print(f"   Resource Contention: {'Detected' if results.resource_contention_detected else 'None'}")

    def _generate_comprehensive_analysis(self, benchmark_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive analysis across all scenarios."""

        if len(benchmark_results) < 2:
            return {"analysis": "insufficient_scenarios_for_analysis"}

        # Extract scaling patterns
        concurrency_levels = [s["concurrent_requests"] for s in benchmark_results]
        efficiencies = [s["results"].concurrency_efficiency for s in benchmark_results]
        total_times = [s["results"].total_execution_time for s in benchmark_results]
        avg_latencies = [s["results"].average_latency for s in benchmark_results]

        # Analyze scaling efficiency
        scaling_analysis = self._analyze_concurrent_scaling(concurrency_levels, efficiencies, total_times)

        # Analyze performance stability
        stability_analysis = self._analyze_performance_stability(benchmark_results)

        # Generate optimization recommendations
        optimization_recommendations = self._generate_concurrent_optimization_recommendations(benchmark_results)

        # Determine optimal concurrency level
        optimal_scenario = max(benchmark_results, key=lambda s: s["results"].concurrency_efficiency)

        return {
            "scaling_analysis": scaling_analysis,
            "stability_analysis": stability_analysis,
            "optimization_recommendations": optimization_recommendations,
            "optimal_concurrency": {
                "level": optimal_scenario["concurrent_requests"],
                "efficiency": optimal_scenario["results"].concurrency_efficiency,
                "scenario_name": optimal_scenario["scenario_name"]
            },
            "performance_summary": {
                "max_concurrency_tested": max(concurrency_levels),
                "highest_efficiency_achieved": max(efficiencies),
                "total_requests_processed": sum(s["results"].successful_requests for s in benchmark_results),
                "overall_success_rate": sum(s["results"].successful_requests for s in benchmark_results) / sum(s["results"].total_requests for s in benchmark_results)
            }
        }

    def _analyze_concurrent_scaling(self, concurrency_levels: List[int], efficiencies: List[float], total_times: List[float]) -> Dict[str, Any]:
        """Analyze how performance scales with concurrency level."""

        if len(concurrency_levels) < 2:
            return {"pattern": "insufficient_data"}

        # Calculate scaling patterns
        efficiency_trend = "stable" if max(efficiencies) - min(efficiencies) <= 0.2 else "variable"

        # Determine if time scaling is sub-linear (good) or super-linear (bad)
        if len(total_times) >= 2:
            time_scaling_factor = total_times[-1] / total_times[0]
            concurrency_scaling_factor = concurrency_levels[-1] / concurrency_levels[0]

            if time_scaling_factor < concurrency_scaling_factor:
                scaling_pattern = "sub_linear_excellent"
            elif time_scaling_factor <= concurrency_scaling_factor * 1.2:
                scaling_pattern = "near_linear_good"
            else:
                scaling_pattern = "super_linear_concerning"
        else:
            scaling_pattern = "unknown"

        return {
            "efficiency_trend": efficiency_trend,
            "scaling_pattern": scaling_pattern,
            "max_efficiency": max(efficiencies),
            "min_efficiency": min(efficiencies),
            "efficiency_variance": max(efficiencies) - min(efficiencies)
        }

    def _analyze_performance_stability(self, benchmark_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance stability across scenarios."""

        # Collect stability metrics
        success_rates = [s["results"].successful_requests / s["results"].total_requests for s in benchmark_results]
        resource_contentions = [s["results"].resource_contention_detected for s in benchmark_results]

        # Calculate stability score
        avg_success_rate = sum(success_rates) / len(success_rates)
        contention_frequency = sum(resource_contentions) / len(resource_contentions)

        # Determine stability level
        if avg_success_rate >= 0.95 and contention_frequency <= 0.2:
            stability_level = "excellent"
        elif avg_success_rate >= 0.8 and contention_frequency <= 0.5:
            stability_level = "good"
        elif avg_success_rate >= 0.6:
            stability_level = "moderate"
        else:
            stability_level = "poor"

        return {
            "stability_level": stability_level,
            "average_success_rate": avg_success_rate,
            "resource_contention_frequency": contention_frequency,
            "performance_consistency": "high" if max(success_rates) - min(success_rates) <= 0.1 else "variable"
        }

    def _generate_concurrent_optimization_recommendations(self, benchmark_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on concurrent performance analysis."""

        recommendations = []

        # Analyze for efficiency issues
        low_efficiency_scenarios = [s for s in benchmark_results if s["results"].concurrency_efficiency < 0.7]

        if low_efficiency_scenarios:
            recommendations.append({
                "category": "concurrency_efficiency",
                "priority": "high",
                "description": f"Low concurrency efficiency detected in {len(low_efficiency_scenarios)} scenarios",
                "recommendation": "Consider optimizing async coordination or reducing resource contention",
                "expected_improvement": "20-40% improvement in concurrency efficiency",
                "affected_scenarios": [s["scenario_name"] for s in low_efficiency_scenarios]
            })

        # Analyze for resource contention
        contention_scenarios = [s for s in benchmark_results if s["results"].resource_contention_detected]

        if contention_scenarios:
            recommendations.append({
                "category": "resource_contention",
                "priority": "medium",
                "description": f"Resource contention detected in {len(contention_scenarios)} scenarios",
                "recommendation": "Implement resource pooling or optimize memory usage patterns",
                "expected_improvement": "15-30% reduction in latency variance",
                "affected_scenarios": [s["scenario_name"] for s in contention_scenarios]
            })

        # Analyze for latency issues
        high_latency_scenarios = [s for s in benchmark_results if s["results"].p95_latency > 60.0]

        if high_latency_scenarios:
            recommendations.append({
                "category": "latency_optimization",
                "priority": "medium",
                "description": f"High P95 latency (>60s) in {len(high_latency_scenarios)} scenarios",
                "recommendation": "Optimize individual workflow stages or implement caching",
                "expected_improvement": "30-50% latency reduction",
                "affected_scenarios": [s["scenario_name"] for s in high_latency_scenarios]
            })

        return recommendations

    def save_comprehensive_report(self, report: Dict[str, Any], filename: str = "era_alpha_2_3_concurrent_load_report.json"):
        """Save the comprehensive concurrent load report to file."""
        with open(f"/app/docs/05_claude_reports/{filename}", 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📄 Comprehensive concurrent load report saved to /app/docs/05_claude_reports/{filename}")

    def print_executive_summary(self, report: Dict[str, Any]):
        """Print executive summary of concurrent load testing results."""
        print("\n🎯 EXECUTIVE SUMMARY - CONCURRENT LOAD TESTING")
        print("=" * 80)

        metadata = report["benchmark_metadata"]
        analysis = report["comprehensive_analysis"]

        print(f"📊 Scenarios Executed: {metadata['scenarios_executed']}")
        print(f"🔄 Total Concurrent Requests Tested: {metadata['total_concurrent_requests_tested']}")

        if "optimal_concurrency" in analysis:
            optimal = analysis["optimal_concurrency"]
            print(f"🎯 Optimal Concurrency Level: {optimal['level']} requests ({optimal['efficiency']:.1%} efficiency)")

        if "performance_summary" in analysis:
            perf = analysis["performance_summary"]
            print(f"📈 Highest Efficiency Achieved: {perf['highest_efficiency_achieved']:.1%}")
            print(f"✅ Overall Success Rate: {perf['overall_success_rate']:.1%}")
            print(f"📊 Total Successful Requests: {perf['total_requests_processed']}")

        if "scaling_analysis" in analysis:
            scaling = analysis["scaling_analysis"]
            print(f"⚡ Scaling Pattern: {scaling['scaling_pattern'].replace('_', ' ').title()}")

        if "stability_analysis" in analysis:
            stability = analysis["stability_analysis"]
            print(f"🛡️  System Stability: {stability['stability_level'].title()}")

        recommendations = analysis.get("optimization_recommendations", [])
        high_priority = [r for r in recommendations if r.get("priority") == "high"]
        print(f"💡 High-Priority Optimizations: {len(high_priority)}")

        # Overall assessment
        if analysis.get("performance_summary", {}).get("overall_success_rate", 0) >= 0.95:
            assessment = "EXCELLENT - Production ready for concurrent load"
        elif analysis.get("stability_analysis", {}).get("stability_level") in ["excellent", "good"]:
            assessment = "GOOD - Minor optimizations recommended"
        else:
            assessment = "ATTENTION - Significant concurrent performance issues identified"

        print(f"🏆 Overall Assessment: {assessment}")


def main():
    """Execute comprehensive concurrent load benchmark suite."""
    benchmark_suite = ComprehensiveConcurrentBenchmark()

    # Execute all concurrent benchmarks
    report = benchmark_suite.execute_concurrent_benchmarks()

    # Print executive summary
    benchmark_suite.print_executive_summary(report)

    # Save detailed report
    benchmark_suite.save_comprehensive_report(report)

    return report


if __name__ == "__main__":
    main()

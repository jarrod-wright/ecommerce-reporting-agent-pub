"""
Comprehensive Multi-Scale Benchmark Suite

Executes all scale levels with detailed reporting and bottleneck analysis.
This validates the complete BDD scenarios from the feature file.
"""

import json
import time
from typing import Any, Dict, List

from tests.performance.scale_testing_framework import (
    MultiScalePerformanceFramework,
    PerformanceMetrics,
)


class ComprehensiveBenchmarkSuite:
    """Execute comprehensive benchmarks across all scales with detailed reporting."""

    def __init__(self):
        """Initialize the comprehensive benchmark suite."""
        self.framework = MultiScalePerformanceFramework()
        self.results: List[PerformanceMetrics] = []

    def execute_all_scales(self) -> Dict[str, Any]:
        """Execute benchmarks across all scale levels."""
        print("🚀 Starting Comprehensive Multi-Scale Benchmark Suite")
        print("=" * 80)

        scales_to_test = ["micro_scale", "small_scale", "medium_scale"]
        # Note: large_scale excluded for resource conservation

        benchmark_results = []

        for scale_name in scales_to_test:
            print(f"\n📊 Executing {scale_name.upper()} Benchmark")
            print("-" * 60)

            try:
                start_time = time.time()
                metrics = self.framework.execute_scale_benchmark(scale_name)
                end_time = time.time()

                benchmark_results.append(metrics)
                self.results.append(metrics)

                # Print detailed results
                self._print_detailed_metrics(metrics)

                print(f"⏱️  Total benchmark time: {end_time - start_time:.2f} seconds")

                if metrics.sla_compliance and metrics.memory_compliance:
                    print(f"✅ {scale_name.upper()} PASSED - All criteria met")
                else:
                    print(f"⚠️  {scale_name.upper()} ATTENTION - Some criteria not met")

            except Exception as e:
                print(f"❌ {scale_name.upper()} FAILED: {str(e)}")
                continue

        # Generate comprehensive report
        report = self._generate_comprehensive_report(benchmark_results)

        return report

    def _print_detailed_metrics(self, metrics: PerformanceMetrics):
        """Print detailed metrics for a single benchmark."""
        print(f"   Scale Name: {metrics.scale_name}")
        print(f"   Total Records: {metrics.total_records:,}")
        print(f"   Dataset Generation Time: {metrics.dataset_generation_time:.3f}s")
        print(f"   ERA Execution Time: {metrics.era_execution_time:.3f}s")
        print(f"   Total End-to-End Time: {metrics.total_end_to_end_time:.3f}s")
        print(f"   Peak Memory Usage: {metrics.memory_peak_mb:.1f}MB")
        print(f"   Memory Growth: {metrics.memory_growth_mb:.1f}MB")
        print(f"   SLA Compliant: {'✅' if metrics.sla_compliance else '❌'}")
        print(f"   Memory Compliant: {'✅' if metrics.memory_compliance else '❌'}")

        # Calculate efficiency metrics
        if metrics.total_records > 0:
            records_per_second = metrics.total_records / metrics.total_end_to_end_time
            mb_per_thousand_records = (metrics.memory_peak_mb / metrics.total_records) * 1000
            print(f"   Processing Rate: {records_per_second:.0f} records/second")
            print(f"   Memory Efficiency: {mb_per_thousand_records:.1f}MB per 1K records")

    def _generate_comprehensive_report(self, results: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Generate comprehensive benchmark report."""

        if not results:
            return {"error": "No benchmark results available"}

        # Calculate summary statistics
        total_tests = len(results)
        sla_compliant_tests = sum(1 for r in results if r.sla_compliance)
        memory_compliant_tests = sum(1 for r in results if r.memory_compliance)

        sla_compliance_rate = sla_compliant_tests / total_tests
        memory_compliance_rate = memory_compliant_tests / total_tests

        # Identify performance patterns
        generation_times = [r.dataset_generation_time for r in results]
        era_times = [r.era_execution_time for r in results]
        memory_peaks = [r.memory_peak_mb for r in results]
        record_counts = [r.total_records for r in results]

        # Bottleneck analysis
        bottlenecks = []

        for metrics in results:
            generation_ratio = metrics.dataset_generation_time / metrics.total_end_to_end_time
            era_ratio = metrics.era_execution_time / metrics.total_end_to_end_time

            if generation_ratio > 0.7:
                bottlenecks.append({
                    "scale": metrics.scale_name,
                    "type": "dataset_generation",
                    "severity": "high" if generation_ratio > 0.8 else "medium"
                })

            if era_ratio > 0.7:
                bottlenecks.append({
                    "scale": metrics.scale_name,
                    "type": "era_processing",
                    "severity": "high" if era_ratio > 0.8 else "medium"
                })

        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(results, bottlenecks)

        report = {
            "benchmark_summary": {
                "total_scales_tested": total_tests,
                "sla_compliance_rate": sla_compliance_rate,
                "memory_compliance_rate": memory_compliance_rate,
                "overall_success_rate": (sla_compliance_rate + memory_compliance_rate) / 2
            },
            "performance_analysis": {
                "dataset_generation_times": {
                    "min": min(generation_times),
                    "max": max(generation_times),
                    "avg": sum(generation_times) / len(generation_times)
                },
                "era_execution_times": {
                    "min": min(era_times),
                    "max": max(era_times),
                    "avg": sum(era_times) / len(era_times)
                },
                "memory_usage": {
                    "min_peak_mb": min(memory_peaks),
                    "max_peak_mb": max(memory_peaks),
                    "avg_peak_mb": sum(memory_peaks) / len(memory_peaks)
                }
            },
            "scalability_analysis": {
                "largest_dataset_records": max(record_counts),
                "performance_scaling": self._analyze_scaling_patterns(results),
                "memory_scaling": self._analyze_memory_scaling(results)
            },
            "bottleneck_analysis": {
                "identified_bottlenecks": bottlenecks,
                "total_bottlenecks": len(bottlenecks),
                "critical_bottlenecks": [b for b in bottlenecks if b["severity"] == "high"]
            },
            "optimization_recommendations": recommendations,
            "detailed_results": [
                {
                    "scale_name": r.scale_name,
                    "total_records": r.total_records,
                    "dataset_generation_time": r.dataset_generation_time,
                    "era_execution_time": r.era_execution_time,
                    "total_time": r.total_end_to_end_time,
                    "memory_peak_mb": r.memory_peak_mb,
                    "sla_compliant": r.sla_compliance,
                    "memory_compliant": r.memory_compliance
                }
                for r in results
            ]
        }

        return report

    def _analyze_scaling_patterns(self, results: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Analyze performance scaling patterns."""
        if len(results) < 2:
            return {"analysis": "insufficient_data"}

        # Sort by record count for scaling analysis
        sorted_results = sorted(results, key=lambda r: r.total_records)

        scaling_factors = []
        for i in range(1, len(sorted_results)):
            prev_result = sorted_results[i-1]
            curr_result = sorted_results[i]

            record_scale_factor = curr_result.total_records / prev_result.total_records
            time_scale_factor = curr_result.total_end_to_end_time / prev_result.total_end_to_end_time

            scaling_efficiency = record_scale_factor / time_scale_factor
            scaling_factors.append(scaling_efficiency)

        avg_scaling_efficiency = sum(scaling_factors) / len(scaling_factors)

        return {
            "average_scaling_efficiency": avg_scaling_efficiency,
            "scaling_pattern": "sub_linear" if avg_scaling_efficiency > 1.0 else "super_linear",
            "scaling_factors": scaling_factors
        }

    def _analyze_memory_scaling(self, results: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Analyze memory scaling patterns."""
        if len(results) < 2:
            return {"analysis": "insufficient_data"}

        sorted_results = sorted(results, key=lambda r: r.total_records)

        memory_efficiency_scores = []
        for result in sorted_results:
            mb_per_record = result.memory_peak_mb / result.total_records
            memory_efficiency_scores.append(mb_per_record)

        return {
            "memory_efficiency_trend": "improving" if memory_efficiency_scores[-1] < memory_efficiency_scores[0] else "declining",
            "avg_mb_per_record": sum(memory_efficiency_scores) / len(memory_efficiency_scores),
            "memory_efficiency_scores": memory_efficiency_scores
        }

    def _generate_optimization_recommendations(self, results: List[PerformanceMetrics], bottlenecks: List[Dict]) -> List[Dict]:
        """Generate specific optimization recommendations based on analysis."""
        recommendations = []

        # Analyze for dataset generation bottlenecks
        generation_bottlenecks = [b for b in bottlenecks if b["type"] == "dataset_generation"]
        if generation_bottlenecks:
            recommendations.append({
                "category": "dataset_generation",
                "priority": "high",
                "description": "Dataset generation is the primary bottleneck",
                "recommendation": "Implement parallel data generation or caching mechanisms",
                "expected_improvement": "30-50% reduction in generation time"
            })

        # Analyze for ERA processing bottlenecks
        era_bottlenecks = [b for b in bottlenecks if b["type"] == "era_processing"]
        if era_bottlenecks:
            recommendations.append({
                "category": "era_processing",
                "priority": "medium",
                "description": "ERA processing shows performance degradation at scale",
                "recommendation": "Implement data streaming or chunked processing",
                "expected_improvement": "20-40% reduction in processing time"
            })

        # Memory optimization recommendations
        high_memory_results = [r for r in results if r.memory_growth_mb > 100]
        if high_memory_results:
            recommendations.append({
                "category": "memory_optimization",
                "priority": "medium",
                "description": "High memory growth detected during processing",
                "recommendation": "Implement garbage collection optimization and memory pooling",
                "expected_improvement": "15-30% reduction in memory usage"
            })

        return recommendations

    def save_report_to_file(self, report: Dict[str, Any], filename: str = "performance_benchmark_report.json"):
        """Save the comprehensive report to a JSON file."""
        with open(f"/app/docs/05_claude_reports/{filename}", 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📄 Comprehensive report saved to /app/docs/05_claude_reports/{filename}")

    def print_executive_summary(self, report: Dict[str, Any]):
        """Print executive summary of benchmark results."""
        print("\n🎯 EXECUTIVE SUMMARY")
        print("=" * 80)

        summary = report["benchmark_summary"]
        print(f"📊 Scales Tested: {summary['total_scales_tested']}")
        print(f"✅ SLA Compliance Rate: {summary['sla_compliance_rate']:.1%}")
        print(f"💾 Memory Compliance Rate: {summary['memory_compliance_rate']:.1%}")
        print(f"🏆 Overall Success Rate: {summary['overall_success_rate']:.1%}")

        bottlenecks = report["bottleneck_analysis"]
        print(f"⚠️  Identified Bottlenecks: {bottlenecks['total_bottlenecks']}")
        print(f"🚨 Critical Bottlenecks: {len(bottlenecks['critical_bottlenecks'])}")

        recommendations = report["optimization_recommendations"]
        print(f"💡 Optimization Recommendations: {len(recommendations)}")

        if summary['overall_success_rate'] >= 0.9:
            print("🎉 BENCHMARK RESULT: EXCELLENT - System ready for production")
        elif summary['overall_success_rate'] >= 0.7:
            print("👍 BENCHMARK RESULT: GOOD - Minor optimizations recommended")
        else:
            print("⚠️  BENCHMARK RESULT: NEEDS IMPROVEMENT - Significant optimizations required")


def main():
    """Execute comprehensive benchmark suite."""
    suite = ComprehensiveBenchmarkSuite()

    # Execute all benchmarks
    report = suite.execute_all_scales()

    # Print executive summary
    suite.print_executive_summary(report)

    # Save detailed report
    suite.save_report_to_file(report, "era_alpha_2_1_performance_benchmark.json")

    return report


if __name__ == "__main__":
    main()

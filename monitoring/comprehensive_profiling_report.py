"""
Comprehensive Resource Profiling Report Generator

Generates detailed cross-scale resource consumption analysis with optimization recommendations.
"""

import json
import time
from typing import Any, Dict, List

from monitoring.resource_profiler import (
    ERAResourceProfiler,
    generate_optimization_report,
)


class ComprehensiveProfilingReport:
    """Generate comprehensive cross-scale resource profiling reports."""

    def __init__(self):
        """Initialize the comprehensive profiling report generator."""
        self.profiler = ERAResourceProfiler()
        self.results = {}

    def execute_cross_scale_analysis(self) -> Dict[str, Any]:
        """Execute resource profiling across multiple scales."""
        print("🔍 Executing Cross-Scale Resource Profiling Analysis")
        print("=" * 70)

        scales_to_profile = ["micro_scale", "small_scale"]
        # Note: medium_scale excluded to conserve resources during testing

        scale_results = {}

        for scale_name in scales_to_profile:
            print(f"\n📊 Profiling {scale_name.upper()}")
            print("-" * 50)

            start_time = time.time()

            try:
                # Generate comprehensive report for this scale
                scale_report = generate_optimization_report(scale_name)
                scale_results[scale_name] = scale_report

                end_time = time.time()

                # Print summary
                summary = scale_report["profiling_summary"]
                print(f"  ✅ {scale_name} completed in {end_time - start_time:.2f}s")
                print(f"     Nodes Profiled: {summary['total_nodes_profiled']}")
                print(f"     Total Execution Time: {summary['total_execution_time']:.3f}s")
                print(f"     Memory Growth: {summary['total_memory_growth_mb']:.1f}MB")
                print(f"     Avg CPU Utilization: {summary['average_cpu_utilization']:.1f}%")
                print(f"     Optimization Recommendations: {len(scale_report['optimization_recommendations'])}")

            except Exception as e:
                print(f"  ❌ {scale_name} failed: {str(e)}")
                continue

        # Generate cross-scale analysis
        cross_scale_report = self._generate_cross_scale_analysis(scale_results)

        return {
            "individual_scale_results": scale_results,
            "cross_scale_analysis": cross_scale_report,
            "analysis_metadata": {
                "scales_analyzed": list(scale_results.keys()),
                "total_scales": len(scale_results),
                "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "framework_version": "ERA-ALPHA-2.2"
            }
        }

    def _generate_cross_scale_analysis(self, scale_results: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate cross-scale resource consumption pattern analysis."""

        if len(scale_results) < 2:
            return {"analysis": "insufficient_data_for_cross_scale_analysis"}

        # Extract node performance across scales
        node_performance_across_scales = {}

        for scale_name, scale_data in scale_results.items():
            node_data = scale_data["node_performance"]

            for node_name, node_metrics in node_data.items():
                if node_name not in node_performance_across_scales:
                    node_performance_across_scales[node_name] = {}

                node_performance_across_scales[node_name][scale_name] = node_metrics

        # Analyze scaling patterns for each node
        scaling_analysis = {}

        for node_name, scale_data in node_performance_across_scales.items():
            scaling_analysis[node_name] = self._analyze_node_scaling_pattern(scale_data)

        # Identify cross-scale bottlenecks
        cross_scale_bottlenecks = self._identify_cross_scale_bottlenecks(scale_results)

        # Generate consolidated recommendations
        consolidated_recommendations = self._generate_consolidated_recommendations(scale_results)

        return {
            "node_scaling_patterns": scaling_analysis,
            "cross_scale_bottlenecks": cross_scale_bottlenecks,
            "consolidated_recommendations": consolidated_recommendations,
            "overall_scaling_efficiency": self._calculate_overall_scaling_efficiency(scale_results)
        }

    def _analyze_node_scaling_pattern(self, node_scale_data: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze how a specific node's performance scales across dataset sizes."""

        scales = list(node_scale_data.keys())
        if len(scales) < 2:
            return {"pattern": "insufficient_data"}

        # Extract metrics
        execution_times = [node_scale_data[scale]["execution_time"] for scale in scales]
        memory_growths = [node_scale_data[scale]["memory_growth_mb"] for scale in scales]
        memory_efficiencies = [node_scale_data[scale]["memory_efficiency"] for scale in scales]

        # Calculate scaling factors
        time_scaling_factor = execution_times[-1] / execution_times[0] if execution_times[0] > 0 else 1
        memory_scaling_factor = memory_growths[-1] / memory_growths[0] if memory_growths[0] > 0 else 1

        # Determine scaling pattern
        if time_scaling_factor <= 1.5:
            time_pattern = "excellent_scaling"
        elif time_scaling_factor <= 3.0:
            time_pattern = "good_scaling"
        elif time_scaling_factor <= 5.0:
            time_pattern = "moderate_scaling"
        else:
            time_pattern = "poor_scaling"

        return {
            "execution_time_scaling_factor": time_scaling_factor,
            "memory_scaling_factor": memory_scaling_factor,
            "time_scaling_pattern": time_pattern,
            "memory_efficiency_trend": "improving" if memory_efficiencies[-1] < memory_efficiencies[0] else "degrading",
            "performance_across_scales": node_scale_data
        }

    def _identify_cross_scale_bottlenecks(self, scale_results: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Identify bottlenecks that appear consistently across scales."""

        cross_scale_bottlenecks = []

        # Get bottleneck analysis from each scale
        scale_bottlenecks = {}
        for scale_name, scale_data in scale_results.items():
            bottleneck_data = scale_data["bottleneck_analysis"]
            scale_bottlenecks[scale_name] = bottleneck_data

        # Identify nodes that are consistently resource-intensive
        all_scales = list(scale_results.keys())

        # Find nodes that appear as most time-intensive across scales
        time_intensive_nodes = set()
        for scale_name, bottleneck_data in scale_bottlenecks.items():
            time_intensive_nodes.add(bottleneck_data["most_time_intensive"]["node"])

        # Find nodes that appear as most memory-intensive across scales
        memory_intensive_nodes = set()
        for scale_name, bottleneck_data in scale_bottlenecks.items():
            memory_intensive_nodes.add(bottleneck_data["most_memory_intensive"]["node"])

        # Create cross-scale bottleneck entries
        for node in time_intensive_nodes:
            if sum(1 for scale in scale_bottlenecks if scale_bottlenecks[scale]["most_time_intensive"]["node"] == node) >= len(all_scales) * 0.5:
                cross_scale_bottlenecks.append({
                    "node_name": node,
                    "bottleneck_type": "execution_time",
                    "consistency": "high",
                    "scales_affected": [scale for scale in all_scales if scale_bottlenecks[scale]["most_time_intensive"]["node"] == node]
                })

        for node in memory_intensive_nodes:
            if sum(1 for scale in scale_bottlenecks if scale_bottlenecks[scale]["most_memory_intensive"]["node"] == node) >= len(all_scales) * 0.5:
                cross_scale_bottlenecks.append({
                    "node_name": node,
                    "bottleneck_type": "memory_consumption",
                    "consistency": "high",
                    "scales_affected": [scale for scale in all_scales if scale_bottlenecks[scale]["most_memory_intensive"]["node"] == node]
                })

        return cross_scale_bottlenecks

    def _generate_consolidated_recommendations(self, scale_results: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Generate consolidated optimization recommendations across all scales."""

        # Collect all recommendations from all scales
        all_recommendations = []
        for scale_name, scale_data in scale_results.items():
            for rec in scale_data["optimization_recommendations"]:
                rec["source_scale"] = scale_name
                all_recommendations.append(rec)

        # Group recommendations by node and optimization type
        grouped_recommendations = {}
        for rec in all_recommendations:
            key = f"{rec['node_name']}_{rec['optimization_type']}"
            if key not in grouped_recommendations:
                grouped_recommendations[key] = []
            grouped_recommendations[key].append(rec)

        # Create consolidated recommendations
        consolidated = []
        for key, recs in grouped_recommendations.items():
            if len(recs) >= 2:  # Recommendation appears in multiple scales
                consolidated.append({
                    "node_name": recs[0]["node_name"],
                    "optimization_type": recs[0]["optimization_type"],
                    "description": f"Cross-scale optimization opportunity: {recs[0]['description']}",
                    "expected_improvement": recs[0]["expected_improvement"],
                    "implementation_effort": recs[0]["implementation_effort"],
                    "priority": "high",  # Cross-scale issues are high priority
                    "scales_affected": [rec["source_scale"] for rec in recs],
                    "consistency": f"Appears in {len(recs)}/{len(scale_results)} scales"
                })

        return consolidated

    def _calculate_overall_scaling_efficiency(self, scale_results: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate overall system scaling efficiency."""

        if len(scale_results) < 2:
            return {"efficiency": "insufficient_data"}

        scales = sorted(scale_results.keys())

        # Get total execution times
        total_times = []
        for scale in scales:
            total_times.append(scale_results[scale]["profiling_summary"]["total_execution_time"])

        # Calculate overall scaling factor
        overall_scaling_factor = total_times[-1] / total_times[0] if total_times[0] > 0 else 1

        # Determine efficiency rating
        if overall_scaling_factor <= 2.0:
            efficiency_rating = "excellent"
        elif overall_scaling_factor <= 4.0:
            efficiency_rating = "good"
        elif overall_scaling_factor <= 8.0:
            efficiency_rating = "moderate"
        else:
            efficiency_rating = "poor"

        return {
            "overall_scaling_factor": overall_scaling_factor,
            "efficiency_rating": efficiency_rating,
            "total_execution_times": dict(zip(scales, total_times)),
            "scaling_linearity": "sub_linear" if overall_scaling_factor < len(scales) else "super_linear"
        }

    def save_comprehensive_report(self, report: Dict[str, Any], filename: str = "era_alpha_2_2_resource_profiling_report.json"):
        """Save the comprehensive profiling report to file."""
        with open(f"/app/docs/05_claude_reports/{filename}", 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📄 Comprehensive profiling report saved to /app/docs/05_claude_reports/{filename}")

    def print_executive_summary(self, report: Dict[str, Any]):
        """Print executive summary of resource profiling results."""
        print("\n🎯 EXECUTIVE SUMMARY - RESOURCE CONSUMPTION ANALYSIS")
        print("=" * 80)

        metadata = report["analysis_metadata"]
        print(f"📊 Scales Analyzed: {metadata['total_scales']} ({', '.join(metadata['scales_analyzed'])})")

        cross_scale = report["cross_scale_analysis"]

        if "overall_scaling_efficiency" in cross_scale:
            scaling = cross_scale["overall_scaling_efficiency"]
            print(f"⚡ Overall Scaling Efficiency: {scaling['efficiency_rating'].upper()}")
            print(f"📈 Scaling Factor: {scaling['overall_scaling_factor']:.2f}x")
            print(f"📉 Scaling Pattern: {scaling['scaling_linearity']}")

        if "cross_scale_bottlenecks" in cross_scale:
            bottlenecks = cross_scale["cross_scale_bottlenecks"]
            print(f"🚨 Cross-Scale Bottlenecks: {len(bottlenecks)}")

        if "consolidated_recommendations" in cross_scale:
            recommendations = cross_scale["consolidated_recommendations"]
            high_priority = [r for r in recommendations if r.get("priority") == "high"]
            print(f"💡 High-Priority Recommendations: {len(high_priority)}")
            print(f"💡 Total Optimization Opportunities: {len(recommendations)}")

        # Determine overall assessment
        if len(cross_scale.get("cross_scale_bottlenecks", [])) == 0:
            assessment = "EXCELLENT - No significant bottlenecks identified"
        elif len(cross_scale.get("consolidated_recommendations", [])) <= 2:
            assessment = "GOOD - Minor optimization opportunities available"
        else:
            assessment = "ATTENTION - Multiple optimization opportunities identified"

        print(f"🏆 Overall Assessment: {assessment}")


def main():
    """Execute comprehensive cross-scale resource profiling analysis."""
    report_generator = ComprehensiveProfilingReport()

    # Execute cross-scale analysis
    comprehensive_report = report_generator.execute_cross_scale_analysis()

    # Print executive summary
    report_generator.print_executive_summary(comprehensive_report)

    # Save detailed report
    report_generator.save_comprehensive_report(comprehensive_report)

    return comprehensive_report


if __name__ == "__main__":
    main()

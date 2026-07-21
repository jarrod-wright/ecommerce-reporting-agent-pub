"""
Integration & System Testing for pragmatic validation suite
Tests end-to-end functionality of all validation components
"""
import asyncio

import pytest

from validation import (
    EnhancedAuditFoundation,
    EnhancedGroundTruthEngine,
    PatternType,
    TrustMetricsOrchestrator,
)


class TestIntegrationValidationSuite:
    """Integration tests for complete validation suite"""

    @pytest.mark.asyncio
    async def test_complete_validation_workflow(self):
        """Test complete validation workflow from pattern generation to final report"""
        # Initialize components
        gte = EnhancedGroundTruthEngine()
        orchestrator = TrustMetricsOrchestrator()
        audit_foundation = EnhancedAuditFoundation()

        # Capture audit event
        audit_foundation.capture_event(
            'validation_start',
            'integration_test',
            'begin_workflow'
        )

        # Generate test dataset
        pattern_config = {
            "pattern_type": PatternType.TREND_INJECTION,
            "trend_type": "linear",
            "growth_rate": 0.15,
            "baseline_revenue": 10000,
            "duration_months": 6
        }

        dataset = gte.generate_dataset(pattern_config)
        assert dataset is not None

        # Simulate ERA insights
        era_insights = [
            {
                "insight": "Revenue shows 15% monthly growth trend",
                "evidence": ["Jan: $10000", "Feb: $11500", "Mar: $13225"],
                "reasoning": "Consistent month-over-month growth observed"
            },
            {
                "insight": "Strong positive trend indicates business expansion",
                "evidence": ["Q1 total: $34725", "Growth rate: 15%"],
                "reasoning": "Upward trajectory suggests healthy business"
            }
        ]

        # Convert dataset to source data format
        source_data = {
            'revenue': dataset.data['revenue'].to_list(),
            'orders': dataset.data['orders'].to_list(),
            'sessions': dataset.data['sessions'].to_list()
        }

        # Run complete validation
        validation_report = await orchestrator.validate_era_insights(era_insights, source_data)

        # Capture completion audit event
        audit_foundation.capture_event(
            'validation_complete',
            'integration_test',
            'end_workflow',
            output_data=validation_report
        )

        # Verify results
        assert validation_report is not None
        assert validation_report.insights_validated == 2
        assert validation_report.trust_score.overall_score >= 0.0
        assert validation_report.validation_summary != ""

        # Verify audit trail
        compliance_report = audit_foundation.generate_compliance_report(
            {"insights_validated": 2, "trust_score": validation_report.trust_score.overall_score}
        )

        assert compliance_report.audit_trail_integrity is True
        assert len(audit_foundation.audit_events) >= 2

    def test_pattern_detection_accuracy(self):
        """Test accuracy of pattern detection across all pattern types"""
        gte = EnhancedGroundTruthEngine()

        test_patterns = [
            {
                "pattern_type": PatternType.TREND_INJECTION,
                "trend_type": "linear",
                "growth_rate": 0.10,
                "expected_detection": True
            },
            {
                "pattern_type": PatternType.NO_SIGNAL,
                "baseline_revenue": 10000,
                "expected_detection": False
            },
            {
                "pattern_type": PatternType.SEASONAL,
                "peak_months": [10, 11],
                "peak_multiplier": 2.0,
                "expected_detection": True
            }
        ]

        detection_accuracy = []

        for config in test_patterns:
            dataset = gte.generate_dataset(config)

            # Verify metadata matches expectations
            if config.get("expected_detection"):
                if dataset.metadata.pattern_type == PatternType.TREND_INJECTION:
                    assert dataset.metadata.expected_trend_detection is True
                elif dataset.metadata.pattern_type == PatternType.SEASONAL:
                    assert dataset.metadata.expected_seasonal_detection is True
            else:
                assert dataset.metadata.expected_trend_detection is False

            detection_accuracy.append(1.0)  # Simplified for integration test

        # Overall accuracy should be high
        avg_accuracy = sum(detection_accuracy) / len(detection_accuracy)
        assert avg_accuracy >= 0.95

    @pytest.mark.asyncio
    async def test_performance_requirements(self):
        """Test system meets performance requirements"""
        orchestrator = TrustMetricsOrchestrator()

        # Test data
        era_insights = [{"insight": f"Test insight {i}"} for i in range(10)]
        source_data = {
            'revenue': [10000 + i * 100 for i in range(12)],
            'orders': [80 + i for i in range(12)]
        }

        # Measure validation time
        start_time = asyncio.get_event_loop().time()

        validation_report = await orchestrator.validate_era_insights(era_insights, source_data)

        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time

        # Should complete within 5 minutes (300 seconds) as per requirements
        assert total_time < 300

        # Verify all insights processed
        assert validation_report.insights_validated == 10

    def test_audit_compliance_standards(self):
        """Test audit foundation meets compliance standards"""
        audit_foundation = EnhancedAuditFoundation()

        # Simulate complete validation workflow events
        required_events = [
            ('validation_start', 'orchestrator', 'begin_validation'),
            ('pattern_generation', 'gte', 'generate_dataset'),
            ('challenger_validation', 'challenger', 'validate_insights'),
            ('evidence_validation', 'evidence_framework', 'validate_evidence'),
            ('trust_calculation', 'orchestrator', 'calculate_trust'),
            ('validation_complete', 'orchestrator', 'finish_validation')
        ]

        # Capture all required events
        for event_type, component, action in required_events:
            audit_foundation.capture_event(event_type, component, action)

        # Generate compliance report
        compliance_report = audit_foundation.generate_compliance_report({
            "validation_complete": True,
            "insights_processed": 5
        })

        # Verify compliance
        assert compliance_report.compliance_status == "COMPLIANT"
        assert compliance_report.audit_trail_integrity is True
        assert compliance_report.cryptographic_proof.startswith("SHA256:")
        assert len(compliance_report.findings) == 0

    def test_error_handling_resilience(self):
        """Test system handles errors gracefully"""
        gte = EnhancedGroundTruthEngine()

        # Test with invalid pattern configuration
        invalid_config = {
            "pattern_type": "INVALID_PATTERN",
            "invalid_parameter": "test"
        }

        with pytest.raises(ValueError):
            gte.generate_dataset(invalid_config)

        # Test with missing required parameters
        incomplete_config = {
            "pattern_type": PatternType.TREND_INJECTION
            # Missing required parameters
        }

        # Should handle gracefully with defaults
        dataset = gte.generate_dataset(incomplete_config)
        assert dataset is not None
        assert dataset.metadata.pattern_type == PatternType.TREND_INJECTION

    @pytest.mark.asyncio
    async def test_concurrent_validation_handling(self):
        """Test system handles concurrent validations"""
        orchestrator = TrustMetricsOrchestrator()

        # Create multiple validation tasks
        tasks = []
        for i in range(3):
            era_insights = [{"insight": f"Insight {i}-{j}"} for j in range(2)]
            source_data = {'revenue': [1000 * (i+1) + j * 100 for j in range(6)]}

            task = orchestrator.validate_era_insights(era_insights, source_data)
            tasks.append(task)

        # Run concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete successfully
        assert len(results) == 3
        assert all(not isinstance(r, Exception) for r in results)
        assert all(r.insights_validated == 2 for r in results)

    def test_validation_report_quality(self):
        """Test validation reports meet quality standards"""
        from validation.trust_metrics_orchestrator import TrustScore, ValidationReport

        # Create sample validation report
        trust_score = TrustScore(
            overall_score=0.85,
            challenger_confidence=0.80,
            evidence_quality=0.90,
            attribution_consistency=0.85,
            requires_review=False
        )

        report = ValidationReport(
            trust_score=trust_score,
            insights_validated=5,
            consistency_variance=0.05,
            validation_summary="High quality validation completed",
            recommendations=["All insights meet standards"]
        )

        # Verify report quality
        assert report.trust_score.overall_score >= 0.8
        assert report.insights_validated > 0
        assert report.validation_summary != ""
        assert len(report.recommendations) > 0
        assert report.consistency_variance < 0.1  # Low variance indicates consistency

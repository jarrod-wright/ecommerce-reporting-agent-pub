"""
Trust Metrics & Validation Orchestration (Chunk 3.2.5)
Orchestrates validation workflow and aggregates trust metrics
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .enhanced_ground_truth_engine import EnhancedGroundTruthEngine
from .lean_attribution_engine import AttributionResult, LeanAttributionEngine
from .local_challenger_model import InsightValidationResult, LocalChallengerModel
from .structured_evidence_framework import EvidenceFramework, StructuredInsight


@dataclass
class TrustScore:
    """Aggregated trust score with component breakdowns"""
    overall_score: float
    challenger_confidence: float
    evidence_quality: float
    attribution_consistency: float
    validation_timestamp: datetime = field(default_factory=datetime.now)
    requires_review: bool = False


@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    trust_score: TrustScore
    insights_validated: int
    consistency_variance: float
    validation_summary: str
    recommendations: List[str] = field(default_factory=list)


class TrustMetricsOrchestrator:
    """Orchestrates validation workflow and trust metrics aggregation"""

    def __init__(self):
        self.challenger_model = LocalChallengerModel()
        self.ground_truth_engine = EnhancedGroundTruthEngine()
        self.evidence_framework = EvidenceFramework()
        self.attribution_engine = LeanAttributionEngine()

        # Trust score weights (aligned with MVP Launch profile)
        self.weights = {
            'challenger_confidence': 0.4,
            'evidence_quality': 0.3,
            'attribution_consistency': 0.3
        }

        self.trust_threshold = 0.6
        self.consistency_threshold = 0.8

        self.logger = logging.getLogger(__name__)

    async def validate_era_insights(self,
                                  era_insights: List[Dict[str, Any]],
                                  source_data: Dict[str, Any]) -> ValidationReport:
        """Complete validation workflow for ERA insights"""

        # Initialize challenger model
        if not self.challenger_model.is_initialized:
            try:
                await self.challenger_model.initialize()
            except Exception as e:
                self.logger.warning(f"Challenger model initialization failed: {e}")

        validation_results = []
        consistency_scores = []

        for insight in era_insights:
            # Step 1: Challenger validation
            challenger_result = await self._validate_with_challenger(insight)

            # Step 2: Evidence validation
            evidence_result = self._validate_evidence(insight, source_data)

            # Step 3: Attribution analysis
            attribution_result = self._analyze_attribution(insight, source_data)

            # Aggregate results
            trust_score = self._calculate_trust_score(
                challenger_result,
                evidence_result,
                attribution_result
            )

            validation_results.append({
                'insight': insight,
                'trust_score': trust_score,
                'challenger_result': challenger_result,
                'evidence_result': evidence_result,
                'attribution_result': attribution_result
            })

            consistency_scores.append(trust_score.overall_score)

        # Calculate cross-run consistency
        consistency_variance = self._calculate_consistency_variance(consistency_scores)

        # Generate overall trust score
        overall_trust = self._aggregate_trust_scores([r['trust_score'] for r in validation_results])

        # Generate validation report
        return ValidationReport(
            trust_score=overall_trust,
            insights_validated=len(validation_results),
            consistency_variance=consistency_variance,
            validation_summary=self._generate_validation_summary(validation_results),
            recommendations=self._generate_recommendations(validation_results)
        )

    async def _validate_with_challenger(self, insight: Dict[str, Any]) -> Optional[InsightValidationResult]:
        """Validate insight using challenger model"""
        try:
            if self.challenger_model.is_initialized:
                return await self.challenger_model.validate_insight(insight)
            else:
                # Fallback validation without challenger
                return InsightValidationResult(
                    logical_consistency_score=0.5,
                    factual_accuracy_score=0.5,
                    evidence_support_score=0.5,
                    overall_confidence=0.5,
                    requires_human_review=True,
                    concerns=["Challenger model unavailable"],
                    validation_reasoning="Fallback validation - challenger model not available"
                )
        except Exception as e:
            self.logger.error(f"Challenger validation failed: {e}")
            return None

    def _validate_evidence(self,
                          insight: Dict[str, Any],
                          source_data: Dict[str, Any]) -> StructuredInsight:
        """Validate evidence citations"""
        insight_text = insight.get('insight', '')
        return self.evidence_framework.enhance_insight_with_evidence(insight_text, source_data)

    def _analyze_attribution(self,
                           insight: Dict[str, Any],
                           source_data: Dict[str, Any]) -> Optional[AttributionResult]:
        """Analyze feature attribution"""
        try:
            # Convert source_data to DataFrame for attribution analysis
            import polars as pl

            # Simple conversion - in real implementation would be more robust
            data_dict = {}
            for key, values in source_data.items():
                if isinstance(values, list) and len(values) > 0:
                    data_dict[key] = values

            if not data_dict:
                return None

            # Ensure all lists are same length
            min_length = min(len(v) for v in data_dict.values())
            for key in data_dict:
                data_dict[key] = data_dict[key][:min_length]

            df = pl.DataFrame(data_dict)

            # Use first numeric column as target
            numeric_columns = [col for col in df.columns if df[col].dtype in [pl.Float64, pl.Float32, pl.Int64]]
            if numeric_columns:
                target = numeric_columns[0]
                return self.attribution_engine.analyze_feature_importance(df, target)

            return None
        except Exception as e:
            self.logger.error(f"Attribution analysis failed: {e}")
            return None

    def _calculate_trust_score(self,
                             challenger_result: Optional[InsightValidationResult],
                             evidence_result: StructuredInsight,
                             attribution_result: Optional[AttributionResult]) -> TrustScore:
        """Calculate aggregated trust score"""

        # Component scores
        challenger_confidence = challenger_result.overall_confidence if challenger_result else 0.5
        evidence_quality = evidence_result.evidence_quality_score
        attribution_consistency = attribution_result.confidence_score if attribution_result else 0.5

        # Weighted aggregation
        overall_score = (
            self.weights['challenger_confidence'] * challenger_confidence +
            self.weights['evidence_quality'] * evidence_quality +
            self.weights['attribution_consistency'] * attribution_consistency
        )

        # Determine if review is required
        requires_review = (
            overall_score < self.trust_threshold or
            (challenger_result and challenger_result.requires_human_review)
        )

        return TrustScore(
            overall_score=overall_score,
            challenger_confidence=challenger_confidence,
            evidence_quality=evidence_quality,
            attribution_consistency=attribution_consistency,
            requires_review=requires_review
        )

    def _calculate_consistency_variance(self, scores: List[float]) -> float:
        """Calculate variance in trust scores across insights"""
        if len(scores) < 2:
            return 0.0

        import numpy as np
        return float(np.var(scores))

    def _aggregate_trust_scores(self, trust_scores: List[TrustScore]) -> TrustScore:
        """Aggregate multiple trust scores into overall score"""
        if not trust_scores:
            return TrustScore(
                overall_score=0.0,
                challenger_confidence=0.0,
                evidence_quality=0.0,
                attribution_consistency=0.0,
                requires_review=True
            )

        avg_overall = sum(ts.overall_score for ts in trust_scores) / len(trust_scores)
        avg_challenger = sum(ts.challenger_confidence for ts in trust_scores) / len(trust_scores)
        avg_evidence = sum(ts.evidence_quality for ts in trust_scores) / len(trust_scores)
        avg_attribution = sum(ts.attribution_consistency for ts in trust_scores) / len(trust_scores)

        any_requires_review = any(ts.requires_review for ts in trust_scores)

        return TrustScore(
            overall_score=avg_overall,
            challenger_confidence=avg_challenger,
            evidence_quality=avg_evidence,
            attribution_consistency=avg_attribution,
            requires_review=any_requires_review
        )

    def _generate_validation_summary(self, validation_results: List[Dict[str, Any]]) -> str:
        """Generate validation summary text"""
        total_insights = len(validation_results)
        high_trust = sum(1 for r in validation_results if r['trust_score'].overall_score >= self.trust_threshold)
        require_review = sum(1 for r in validation_results if r['trust_score'].requires_review)

        return (f"Validated {total_insights} insights. "
                f"{high_trust} achieved high trust scores. "
                f"{require_review} require human review.")

    def _generate_recommendations(self, validation_results: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        low_trust_count = sum(1 for r in validation_results
                             if r['trust_score'].overall_score < self.trust_threshold)

        if low_trust_count > 0:
            recommendations.append(f"Review {low_trust_count} insights with low trust scores")

        evidence_issues = sum(1 for r in validation_results
                            if r['evidence_result'].evidence_quality_score < 0.7)

        if evidence_issues > 0:
            recommendations.append(f"Improve evidence quality for {evidence_issues} insights")

        challenger_issues = sum(1 for r in validation_results
                              if r['challenger_result'] and r['challenger_result'].overall_confidence < 0.7)

        if challenger_issues > 0:
            recommendations.append(f"Address challenger concerns for {challenger_issues} insights")

        return recommendations or ["All insights meet validation standards"]

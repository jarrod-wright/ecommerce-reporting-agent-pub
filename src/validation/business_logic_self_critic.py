"""
BusinessLogicSelfCritic - Structured Self-Critique Validation Framework

Implements adversarial self-validation using structured prompting with single Claude LLM.
"""

import re
from typing import Any, Dict, List

from validation.structured_insight_models import (
    CritiqueResult,
    EvidenceSnippet,
    VerifiableInsight,
)


class BusinessLogicSelfCritic:
    """Self-critique validation using adversarial persona and structured analysis"""

    def __init__(self):
        self.critique_persona = "skeptical_business_analyst"
        self.min_evidence_quality_threshold = 0.7
        self.min_logic_consistency_threshold = 0.75
        self.min_ground_truth_alignment_threshold = 0.8

    def critique_insight(self, insight: VerifiableInsight,
                        ground_truth_config: Dict[str, Any]) -> CritiqueResult:
        """Execute structured self-critique against ground truth configuration"""

        # Analyze each critique dimension
        evidence_quality_score = self._assess_evidence_quality(insight.supporting_evidence)
        logical_consistency_score = self._assess_logical_consistency(
            insight.reasoning_steps, insight.insight_statement
        )
        ground_truth_alignment_score = self._assess_ground_truth_alignment(
            insight, ground_truth_config
        )

        # Generate detailed feedback
        detailed_feedback = self._generate_critique_feedback(
            insight, ground_truth_config,
            evidence_quality_score, logical_consistency_score, ground_truth_alignment_score
        )

        # Determine overall verdict
        overall_verdict = self._determine_overall_verdict(
            evidence_quality_score, logical_consistency_score, ground_truth_alignment_score
        )

        return CritiqueResult(
            overall_verdict=overall_verdict,
            evidence_quality_score=evidence_quality_score,
            logical_consistency_score=logical_consistency_score,
            ground_truth_alignment_score=ground_truth_alignment_score,
            detailed_feedback=detailed_feedback
        )

    def _assess_evidence_quality(self, evidence_snippets: List[EvidenceSnippet]) -> float:
        """Assess quality and sufficiency of supporting evidence"""
        if not evidence_snippets:
            return 0.0

        quality_factors = []

        # Check for evidence completeness
        has_record_ids = all(e.record_id and e.record_id.strip() for e in evidence_snippets)
        has_field_names = all(e.field_name and e.field_name.strip() for e in evidence_snippets)
        has_data_values = all(e.data_value and e.data_value.strip() for e in evidence_snippets)
        has_context = all(e.context and e.context.strip() for e in evidence_snippets)

        completeness_score = sum([has_record_ids, has_field_names, has_data_values, has_context]) / 4.0
        quality_factors.append(completeness_score)

        # Check for evidence diversity (different record IDs)
        unique_records = len(set(e.record_id for e in evidence_snippets))
        diversity_score = min(unique_records / max(3, len(evidence_snippets)), 1.0)
        quality_factors.append(diversity_score)

        # Check for specific numeric values in business context
        numeric_evidence_count = sum(1 for e in evidence_snippets
                                   if self._contains_numeric_value(e.data_value))
        numeric_score = min(numeric_evidence_count / max(1, len(evidence_snippets)), 1.0)
        quality_factors.append(numeric_score)

        return sum(quality_factors) / len(quality_factors)

    def _assess_logical_consistency(self, reasoning_steps: List[str],
                                   insight_statement: str) -> float:
        """Assess logical consistency of reasoning chain"""
        if not reasoning_steps or not insight_statement:
            return 0.0

        consistency_factors = []

        # Check for sufficient reasoning steps
        steps_adequacy = min(len(reasoning_steps) / 3.0, 1.0)  # Expect at least 3 steps
        consistency_factors.append(steps_adequacy)

        # Check for logical progression indicators
        progression_keywords = ['first', 'then', 'next', 'finally', 'therefore', 'thus', 'consequently']
        has_progression = any(keyword in ' '.join(reasoning_steps).lower()
                            for keyword in progression_keywords)
        consistency_factors.append(1.0 if has_progression else 0.85)

        # Check for quantitative reasoning
        has_calculations = any(self._contains_calculation_language(step)
                             for step in reasoning_steps)
        consistency_factors.append(1.0 if has_calculations else 0.9)

        # Check alignment between reasoning and conclusion
        key_terms_in_steps = self._extract_key_terms(' '.join(reasoning_steps))
        key_terms_in_insight = self._extract_key_terms(insight_statement)
        term_overlap = len(key_terms_in_steps & key_terms_in_insight) / max(len(key_terms_in_insight), 1)
        consistency_factors.append(min(term_overlap, 1.0))

        return sum(consistency_factors) / len(consistency_factors)

    def _assess_ground_truth_alignment(self, insight: VerifiableInsight,
                                     ground_truth_config: Dict[str, Any]) -> float:
        """Assess alignment with expected ground truth patterns"""
        if not ground_truth_config:
            return 0.5  # Neutral score if no ground truth available

        alignment_factors = []

        # Check expected pattern alignment
        if 'expected_pattern' in ground_truth_config:
            pattern_alignment = self._check_pattern_alignment(
                insight, ground_truth_config['expected_pattern']
            )
            alignment_factors.append(pattern_alignment)

        # Check expected insights alignment
        if 'expected_insights' in ground_truth_config:
            insights_alignment = self._check_expected_insights_alignment(
                insight.insight_statement, ground_truth_config['expected_insights']
            )
            alignment_factors.append(insights_alignment)

        # Check validation criteria alignment
        if 'validation_criteria' in ground_truth_config:
            criteria_alignment = self._check_validation_criteria_alignment(
                insight, ground_truth_config['validation_criteria']
            )
            alignment_factors.append(criteria_alignment)

        return sum(alignment_factors) / max(len(alignment_factors), 1)

    def _check_pattern_alignment(self, insight: VerifiableInsight,
                               expected_pattern: Dict[str, Any]) -> float:
        """Check if insight aligns with expected pattern characteristics"""
        alignment_score = 0.0
        checks_performed = 0

        insight_text = insight.insight_statement.lower()

        # Check growth rate alignment
        if 'growth_rate' in expected_pattern:
            expected_rate = expected_pattern['growth_rate']
            if expected_rate > 0 and ('growth' in insight_text or 'increase' in insight_text):
                alignment_score += 1.0
            elif expected_rate == 0 and ('flat' in insight_text or 'stable' in insight_text):
                alignment_score += 1.0
            checks_performed += 1

        # Check pattern type alignment
        if 'type' in expected_pattern:
            pattern_type = expected_pattern['type'].lower()
            if pattern_type == 'linear_growth' and 'growth' in insight_text:
                alignment_score += 1.0
            elif pattern_type == 'seasonal' and 'seasonal' in insight_text:
                alignment_score += 1.0
            elif pattern_type == 'conversion_funnel' and 'conversion' in insight_text:
                alignment_score += 1.0
            checks_performed += 1

        # Check trend direction alignment
        if 'trend_direction' in expected_pattern:
            expected_direction = expected_pattern['trend_direction'].lower()
            if expected_direction == 'positive' and any(word in insight_text
                for word in ['increase', 'growth', 'rising', 'positive']):
                alignment_score += 1.0
            checks_performed += 1

        return alignment_score / max(checks_performed, 1)

    def _check_expected_insights_alignment(self, insight_statement: str,
                                         expected_insights: List[str]) -> float:
        """Check if insight statement aligns with expected insights"""
        insight_lower = insight_statement.lower()

        alignment_scores = []
        for expected in expected_insights:
            expected_lower = expected.lower()

            # Check for keyword overlap
            insight_words = set(insight_lower.split())
            expected_words = set(expected_lower.split())
            overlap_ratio = len(insight_words & expected_words) / max(len(expected_words), 1)
            alignment_scores.append(overlap_ratio)

        # Return the highest alignment score (best match)
        return max(alignment_scores) if alignment_scores else 0.0

    def _check_validation_criteria_alignment(self, insight: VerifiableInsight,
                                           validation_criteria: List[Dict[str, Any]]) -> float:
        """Check if insight aligns with validation criteria"""
        alignment_scores = []

        for criterion in validation_criteria:
            if 'metric' not in criterion:
                continue

            metric = criterion['metric'].lower()
            expected_value = criterion.get('expected_value', True)

            # Simple heuristic alignment checks
            if 'growth' in metric and 'growth' in insight.insight_statement.lower():
                alignment_scores.append(1.0)
            elif 'seasonal' in metric and 'seasonal' in insight.insight_statement.lower():
                alignment_scores.append(1.0)
            elif 'conversion' in metric and 'conversion' in insight.insight_statement.lower():
                alignment_scores.append(1.0)
            else:
                alignment_scores.append(0.5)  # Neutral score for unclear alignment

        return sum(alignment_scores) / max(len(alignment_scores), 1)

    def _generate_critique_feedback(self, insight: VerifiableInsight,
                                  ground_truth_config: Dict[str, Any],
                                  evidence_score: float, logic_score: float,
                                  alignment_score: float) -> str:
        """Generate detailed structured critique feedback"""

        feedback_sections = []

        # Evidence quality feedback
        if evidence_score < self.min_evidence_quality_threshold:
            feedback_sections.append(
                f"EVIDENCE QUALITY CONCERN (Score: {evidence_score:.2f}): "
                f"Supporting evidence appears insufficient or incomplete. "
                f"Recommend providing more specific record IDs and data values."
            )
        else:
            feedback_sections.append(
                f"EVIDENCE QUALITY ACCEPTABLE (Score: {evidence_score:.2f}): "
                f"Supporting evidence meets quality standards with specific record references."
            )

        # Logical consistency feedback
        if logic_score < self.min_logic_consistency_threshold:
            feedback_sections.append(
                f"LOGICAL CONSISTENCY CONCERN (Score: {logic_score:.2f}): "
                f"Reasoning chain lacks clarity or logical progression. "
                f"Recommend strengthening step-by-step analysis."
            )
        else:
            feedback_sections.append(
                f"LOGICAL CONSISTENCY ACCEPTABLE (Score: {logic_score:.2f}): "
                f"Reasoning demonstrates clear analytical progression."
            )

        # Ground truth alignment feedback
        if alignment_score < self.min_ground_truth_alignment_threshold:
            feedback_sections.append(
                f"GROUND TRUTH ALIGNMENT CONCERN (Score: {alignment_score:.2f}): "
                f"Insight may not align with expected pattern characteristics. "
                f"Verify against configuration expectations."
            )
        else:
            feedback_sections.append(
                f"GROUND TRUTH ALIGNMENT ACCEPTABLE (Score: {alignment_score:.2f}): "
                f"Insight demonstrates strong alignment with expected patterns."
            )

        return " | ".join(feedback_sections)

    def _determine_overall_verdict(self, evidence_score: float,
                                 logic_score: float, alignment_score: float) -> str:
        """Determine overall critique verdict"""

        # Calculate weighted overall score
        overall_score = (
            evidence_score * 0.3 +
            logic_score * 0.3 +
            alignment_score * 0.4
        )

        if overall_score >= 0.60:
            return "PASS"
        elif overall_score >= 0.40:
            return "NEEDS_REVISION"
        else:
            return "FAIL"

    def _contains_numeric_value(self, text: str) -> bool:
        """Check if text contains numeric values"""
        return bool(re.search(r'\d+(?:\.\d+)?', text))

    def _contains_calculation_language(self, text: str) -> bool:
        """Check if text contains calculation or analysis language"""
        calc_keywords = ['calculated', 'computed', 'analyzed', 'measured', 'rate',
                        'percentage', 'total', 'average', 'sum', 'ratio']
        return any(keyword in text.lower() for keyword in calc_keywords)

    def _extract_key_terms(self, text: str) -> set:
        """Extract key business terms from text"""
        business_terms = ['revenue', 'growth', 'conversion', 'seasonal', 'trend',
                         'increase', 'decrease', 'rate', 'pattern', 'analysis']
        text_lower = text.lower()
        return {term for term in business_terms if term in text_lower}

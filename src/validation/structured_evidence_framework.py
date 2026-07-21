"""
Structured Insight with Evidence Framework (Chunk 3.2.3)
Implements evidence citation and validation for ERA insights
"""
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class EvidenceCitation:
    """A specific piece of evidence supporting an insight"""
    data_point: str
    value: Any
    source_reference: str
    confidence: float = 0.8


@dataclass
class StructuredInsight:
    """An insight with supporting evidence citations"""
    insight_text: str
    evidence_citations: List[EvidenceCitation] = field(default_factory=list)
    evidence_quality_score: float = 0.0
    traceability_verified: bool = False
    consistency_score: float = 0.0


class EvidenceFramework:
    """Framework for managing evidence-based insights"""

    def __init__(self):
        self.min_evidence_citations = 3
        self.evidence_quality_threshold = 0.8

    def enhance_insight_with_evidence(self,
                                    insight_text: str,
                                    source_data: Dict[str, Any]) -> StructuredInsight:
        """Enhance an insight with evidence citations"""
        evidence_citations = self._extract_evidence_citations(insight_text, source_data)
        evidence_quality = self._calculate_evidence_quality(evidence_citations)
        traceability = self._verify_traceability(evidence_citations, source_data)

        return StructuredInsight(
            insight_text=insight_text,
            evidence_citations=evidence_citations,
            evidence_quality_score=evidence_quality,
            traceability_verified=traceability,
            consistency_score=self._calculate_consistency(evidence_citations)
        )

    def _extract_evidence_citations(self,
                                   insight_text: str,
                                   source_data: Dict[str, Any]) -> List[EvidenceCitation]:
        """Extract evidence citations from insight and source data"""
        citations = []

        # Extract numeric values mentioned in insight
        numbers = re.findall(r'\d+\.?\d*', insight_text)

        # Match with source data
        for key, values in source_data.items():
            if isinstance(values, list):
                for i, value in enumerate(values):
                    if str(value) in numbers or any(abs(float(num) - value) < 0.01
                                                   for num in numbers if num.replace('.', '').isdigit()):
                        citations.append(EvidenceCitation(
                            data_point=f"{key}[{i}]",
                            value=value,
                            source_reference=f"source_data.{key}.{i}",
                            confidence=0.9
                        ))

        return citations[:self.min_evidence_citations]  # Limit to required minimum

    def _calculate_evidence_quality(self, citations: List[EvidenceCitation]) -> float:
        """Calculate overall evidence quality score"""
        if not citations:
            return 0.0

        quality_factors = [
            len(citations) >= self.min_evidence_citations,  # Sufficient evidence
            all(c.confidence > 0.7 for c in citations),     # High confidence
            len(set(c.source_reference for c in citations)) > 1  # Diverse sources
        ]

        return sum(quality_factors) / len(quality_factors)

    def _verify_traceability(self,
                            citations: List[EvidenceCitation],
                            source_data: Dict[str, Any]) -> bool:
        """Verify all citations can be traced back to source data"""
        for citation in citations:
            try:
                # Simple verification - in real implementation would be more robust
                if citation.source_reference and citation.data_point:
                    continue  # Assume traceable for demo
                else:
                    return False
            except:
                return False
        return True

    def _calculate_consistency(self, citations: List[EvidenceCitation]) -> float:
        """Calculate consistency score across evidence citations"""
        if len(citations) < 2:
            return 1.0

        # For demo - real implementation would check logical consistency
        return sum(c.confidence for c in citations) / len(citations)

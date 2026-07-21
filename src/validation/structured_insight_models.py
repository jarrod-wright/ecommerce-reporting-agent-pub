"""
Structured Insight Models for Pragmatic Business Logic Validation

Pydantic models implementing the "Structured Insight with Evidence" pattern
using simple, verifiable data evidence instead of complex statistical objects.
"""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class EvidenceSnippet(BaseModel):
    """Simple, verifiable evidence pointing to actual data records"""
    record_id: str = Field(description="Unique identifier for this data point")
    field_name: str = Field(description="Data field being referenced")
    data_value: str = Field(description="Actual data value observed")
    context: str = Field(description="Brief context for this evidence")


class VerifiableInsight(BaseModel):
    """Business insight with direct data evidence and reasoning chain"""
    insight_id: str = Field(description="Unique insight identifier")
    insight_statement: str = Field(description="Clear business finding")
    confidence_level: str = Field(description="High/Medium/Low confidence rating")
    supporting_evidence: List[EvidenceSnippet] = Field(description="Direct data evidence")
    reasoning_steps: List[str] = Field(description="Step-by-step logical reasoning")


class ERABusinessValidationReport(BaseModel):
    """Complete verifiable business validation report"""
    report_id: str = Field(description="Unique validation cycle identifier")
    scenario_name: str = Field(description="Business scenario being validated")
    insights: List[VerifiableInsight] = Field(description="Structured insights with evidence")
    validation_timestamp: str = Field(description="When validation was performed")
    overall_assessment: str = Field(description="PASS/FAIL/PARTIAL validation result")


class CritiqueResult(BaseModel):
    """Result of self-critique validation"""
    overall_verdict: str = Field(description="PASS/FAIL/NEEDS_REVISION verdict")
    evidence_quality_score: float = Field(ge=0, le=1, description="Quality of supporting evidence")
    logical_consistency_score: float = Field(ge=0, le=1, description="Logical reasoning quality")
    ground_truth_alignment_score: float = Field(ge=0, le=1, description="Alignment with expected patterns")
    detailed_feedback: str = Field(description="Specific critique feedback")


class ValidationCycleResult(BaseModel):
    """Complete result of a business logic validation cycle"""
    scenario_name: str = Field(description="Business scenario validated")
    overall_trustworthiness_score: float = Field(ge=0, le=1, description="Overall trustworthiness assessment")
    ground_truth_alignment: float = Field(ge=0, le=1, description="Alignment with configuration expectations")
    self_critique_consensus: float = Field(ge=0, le=1, description="Self-critique validation consensus")
    evidence_quality_score: float = Field(ge=0, le=1, description="Quality of provided evidence")
    falsifiability_success_count: int = Field(description="Number of false positives correctly rejected")
    detailed_assessment: str = Field(description="Comprehensive assessment summary")


class FalsifiabilityTest(BaseModel):
    """Configuration for a falsifiability test scenario"""
    name: str = Field(description="Test name identifier")
    config_override: Dict[str, Any] = Field(description="Configuration modifications for negative testing")
    expected_insight_absence: str = Field(description="What patterns should NOT be found")
    failure_condition: str = Field(description="What constitutes a test failure")


class FalsifiabilityResults(BaseModel):
    """Results from falsifiability testing"""
    successful_rejections: int = Field(description="Number of false patterns correctly rejected")
    false_positive_prevention_success: bool = Field(description="Whether false positives were prevented")
    rejected_claims: str = Field(description="Description of claims that were correctly rejected")
    confidence_calibration_success: bool = Field(description="Whether confidence was appropriately calibrated")


class GroundTruthConfiguration(BaseModel):
    """Ground truth configuration loaded from YAML"""
    scenario_name: str = Field(description="Business scenario identifier")
    description: str = Field(description="Scenario description")
    dataset_config: Dict[str, Any] = Field(description="TDG dataset configuration")
    expected_pattern: Dict[str, Any] = Field(description="Expected business pattern characteristics")
    validation_criteria: List[Dict[str, Any]] = Field(description="Validation success criteria")
    expected_insights: List[str] = Field(description="Expected insight statements")


class EvidenceVerificationResult(BaseModel):
    """Result of evidence verification against actual dataset"""
    quality_score: float = Field(ge=0, le=1, description="Overall evidence quality score")
    all_records_valid: bool = Field(description="Whether all record IDs exist in dataset")
    all_values_accurate: bool = Field(description="Whether all data values match dataset")
    invalid_references: List[str] = Field(default=[], description="List of invalid record references")
    value_mismatches: List[str] = Field(default=[], description="List of value mismatches found")
    verification_details: str = Field(description="Detailed verification analysis")


class TrustworthinessAssessment(BaseModel):
    """Final trustworthiness tier assessment"""
    tier: str = Field(description="Green/Yellow/Red trustworthiness tier")
    overall_score: float = Field(ge=0, le=1, description="Overall trustworthiness score")
    component_scores: Dict[str, float] = Field(description="Individual component scores")
    certification_status: str = Field(description="TRUSTWORTHY/CONDITIONAL/NOT_TRUSTWORTHY")
    recommendations: List[str] = Field(description="Specific improvement recommendations")

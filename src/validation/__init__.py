"""
Validation module for the eCommerce Reporting Agent
Implements pragmatic business logic validation suite
"""

from .enhanced_audit_foundation import (
    AuditEvent,
    ComplianceReport,
    EnhancedAuditFoundation,
)
from .enhanced_ground_truth_engine import (
    EnhancedGroundTruthEngine,
    GeneratedDataset,
    NoSignalPattern,
    PatternMetadata,
    PatternType,
    SeasonalPattern,
    TrendInjectionPattern,
)
from .lean_attribution_engine import AttributionResult, LeanAttributionEngine
from .local_challenger_model import (
    ChallengerResponse,
    InsightValidationResult,
    LocalChallengerModel,
)
from .structured_evidence_framework import (
    EvidenceCitation,
    EvidenceFramework,
    StructuredInsight,
)
from .trust_metrics_orchestrator import (
    TrustMetricsOrchestrator,
    TrustScore,
    ValidationReport,
)

__all__ = [
    'LocalChallengerModel',
    'ChallengerResponse',
    'InsightValidationResult',
    'EnhancedGroundTruthEngine',
    'PatternType',
    'PatternMetadata',
    'GeneratedDataset',
    'TrendInjectionPattern',
    'NoSignalPattern',
    'SeasonalPattern',
    'EvidenceFramework',
    'StructuredInsight',
    'EvidenceCitation',
    'LeanAttributionEngine',
    'AttributionResult',
    'TrustMetricsOrchestrator',
    'TrustScore',
    'ValidationReport',
    'EnhancedAuditFoundation',
    'AuditEvent',
    'ComplianceReport'
]

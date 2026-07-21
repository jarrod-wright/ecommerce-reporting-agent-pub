"""
Enhanced Audit Foundation (Chunk 3.2.6)
Implements enhanced audit trail and compliance reporting
"""
import hashlib
import hmac
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class AuditEvent:
    """Individual audit event with metadata"""
    event_id: str
    timestamp: datetime
    event_type: str
    component: str
    action: str
    input_data_hash: str
    output_data_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None


@dataclass
class ComplianceReport:
    """Comprehensive compliance report"""
    report_id: str
    generation_timestamp: datetime
    validation_summary: Dict[str, Any]
    audit_trail_integrity: bool
    cryptographic_proof: str
    compliance_status: str
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class EnhancedAuditFoundation:
    """Enhanced audit foundation with cryptographic integrity"""

    def __init__(self, secret_key: str = "era-audit-key-2024"):
        self.secret_key = secret_key.encode('utf-8')
        self.audit_events: List[AuditEvent] = []
        self.logger = logging.getLogger(__name__)

        # Compliance standards
        self.required_events = [
            'validation_start',
            'pattern_generation',
            'challenger_validation',
            'evidence_validation',
            'trust_calculation',
            'validation_complete'
        ]

    def capture_event(self,
                     event_type: str,
                     component: str,
                     action: str,
                     input_data: Any = None,
                     output_data: Any = None,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Capture and cryptographically sign an audit event"""

        event_id = self._generate_event_id()
        timestamp = datetime.now()

        # Hash input and output data
        input_hash = self._hash_data(input_data) if input_data else ""
        output_hash = self._hash_data(output_data) if output_data else ""

        # Create audit event
        event = AuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            component=component,
            action=action,
            input_data_hash=input_hash,
            output_data_hash=output_hash,
            metadata=metadata or {}
        )

        # Cryptographically sign the event
        event.signature = self._sign_event(event)

        # Store event
        self.audit_events.append(event)

        self.logger.info(f"Audit event captured: {event_type}.{component}.{action}")
        return event_id

    def verify_audit_integrity(self) -> bool:
        """Verify cryptographic integrity of audit trail"""
        try:
            for event in self.audit_events:
                expected_signature = self._sign_event(event)
                if event.signature != expected_signature:
                    self.logger.error(f"Integrity violation in event {event.event_id}")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Audit integrity verification failed: {e}")
            return False

    def generate_compliance_report(self,
                                 validation_summary: Dict[str, Any]) -> ComplianceReport:
        """Generate comprehensive compliance report"""

        report_id = f"COMPLIANCE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Verify audit trail integrity
        integrity_verified = self.verify_audit_integrity()

        # Check compliance completeness
        captured_events = set(event.event_type for event in self.audit_events)
        missing_events = set(self.required_events) - captured_events

        # Determine compliance status
        if integrity_verified and not missing_events:
            compliance_status = "COMPLIANT"
        elif integrity_verified:
            compliance_status = "PARTIAL_COMPLIANCE"
        else:
            compliance_status = "NON_COMPLIANT"

        # Generate findings
        findings = []
        if missing_events:
            findings.append(f"Missing required audit events: {', '.join(missing_events)}")
        if not integrity_verified:
            findings.append("Audit trail integrity compromised")

        # Generate cryptographic proof
        proof = self._generate_cryptographic_proof()

        # Generate recommendations
        recommendations = self._generate_compliance_recommendations(missing_events, integrity_verified)

        return ComplianceReport(
            report_id=report_id,
            generation_timestamp=datetime.now(),
            validation_summary=validation_summary,
            audit_trail_integrity=integrity_verified,
            cryptographic_proof=proof,
            compliance_status=compliance_status,
            findings=findings,
            recommendations=recommendations
        )

    def export_audit_trail(self, output_path: str) -> bool:
        """Export audit trail to file"""
        try:
            audit_data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_events': len(self.audit_events),
                'integrity_verified': self.verify_audit_integrity(),
                'events': [asdict(event) for event in self.audit_events]
            }

            # Convert datetime objects to ISO format
            for event_data in audit_data['events']:
                if isinstance(event_data['timestamp'], datetime):
                    event_data['timestamp'] = event_data['timestamp'].isoformat()

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(audit_data, f, indent=2, default=str)

            self.logger.info(f"Audit trail exported to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export audit trail: {e}")
            return False

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp_ms = int(datetime.now().timestamp() * 1000)
        return f"EVT-{timestamp_ms}-{len(self.audit_events):04d}"

    def _hash_data(self, data: Any) -> str:
        """Generate SHA-256 hash of data"""
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
        except Exception:
            return hashlib.sha256(str(data).encode('utf-8')).hexdigest()

    def _sign_event(self, event: AuditEvent) -> str:
        """Generate HMAC signature for event"""
        # Create signature payload (excluding the signature field itself)
        payload_data = {
            'event_id': event.event_id,
            'timestamp': event.timestamp.isoformat(),
            'event_type': event.event_type,
            'component': event.component,
            'action': event.action,
            'input_data_hash': event.input_data_hash,
            'output_data_hash': event.output_data_hash,
            'metadata': event.metadata
        }

        payload_str = json.dumps(payload_data, sort_keys=True)
        return hmac.new(
            self.secret_key,
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _generate_cryptographic_proof(self) -> str:
        """Generate cryptographic proof of audit trail"""
        if not self.audit_events:
            return ""

        # Create chain hash of all events
        chain_data = []
        for event in self.audit_events:
            chain_data.append(event.signature or "")

        chain_str = ''.join(chain_data)
        proof = hashlib.sha256(chain_str.encode('utf-8')).hexdigest()

        return f"SHA256:{proof}"

    def _generate_compliance_recommendations(self,
                                           missing_events: set,
                                           integrity_verified: bool) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []

        if missing_events:
            recommendations.append("Ensure all required validation events are captured")
            recommendations.append("Implement comprehensive event tracking across all validation components")

        if not integrity_verified:
            recommendations.append("Investigate audit trail integrity issues")
            recommendations.append("Implement stronger cryptographic controls")

        if not recommendations:
            recommendations.append("Audit trail meets compliance requirements")
            recommendations.append("Continue monitoring validation processes")

        return recommendations

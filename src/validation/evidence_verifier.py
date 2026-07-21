"""
EvidenceVerifier - Direct Data Evidence Validation

Verifies evidence snippets against actual dataset records for truthfulness and accuracy.
"""

from typing import Any, Dict, List, Tuple

from validation.structured_insight_models import (
    EvidenceSnippet,
    EvidenceVerificationResult,
)


class EvidenceVerifier:
    """Verifies evidence snippets against actual dataset records"""

    def __init__(self):
        self.valid_record_id_fields = ['id', 'order_id', 'record_id', 'transaction_id']
        self.tolerance_for_numeric_values = 0.01  # 1% tolerance for floating point comparisons

    def verify_evidence(self, evidence_snippets: List[EvidenceSnippet],
                       dataset: Dict[str, Any]) -> EvidenceVerificationResult:
        """Verify evidence snippets against actual dataset records"""

        if not evidence_snippets:
            return EvidenceVerificationResult(
                quality_score=0.0,
                all_records_valid=False,
                all_values_accurate=False,
                invalid_references=[],
                value_mismatches=[],
                verification_details="No evidence snippets provided for verification"
            )

        verification_results = []
        invalid_references = []
        value_mismatches = []

        for evidence in evidence_snippets:
            record_found, value_accurate, details = self._verify_single_evidence(evidence, dataset)

            verification_results.append({
                'evidence': evidence,
                'record_found': record_found,
                'value_accurate': value_accurate,
                'details': details
            })

            if not record_found:
                invalid_references.append(
                    f"Record ID '{evidence.record_id}' not found in dataset"
                )

            if record_found and not value_accurate:
                value_mismatches.append(
                    f"Value mismatch for {evidence.record_id}.{evidence.field_name}: "
                    f"claimed '{evidence.data_value}' vs actual '{details}'"
                )

        # Calculate overall results
        all_records_valid = all(result['record_found'] for result in verification_results)
        all_values_accurate = all(result['value_accurate'] for result in verification_results if result['record_found'])
        quality_score = self._calculate_quality_score(verification_results)

        verification_details = self._generate_verification_details(
            verification_results, invalid_references, value_mismatches
        )

        return EvidenceVerificationResult(
            quality_score=quality_score,
            all_records_valid=all_records_valid,
            all_values_accurate=all_values_accurate,
            invalid_references=invalid_references,
            value_mismatches=value_mismatches,
            verification_details=verification_details
        )

    def _verify_single_evidence(self, evidence: EvidenceSnippet,
                               dataset: Dict[str, Any]) -> Tuple[bool, bool, str]:
        """Verify a single evidence snippet against the dataset"""

        # Find the record in the dataset
        record_found = False
        actual_value = None
        record_location = ""

        for table_name, records in dataset.items():
            if not isinstance(records, list):
                continue

            for record in records:
                if not isinstance(record, dict):
                    continue

                # Check multiple possible ID field names
                record_id_match = False
                for id_field in self.valid_record_id_fields:
                    if (id_field in record and
                        str(record[id_field]) == str(evidence.record_id)):
                        record_id_match = True
                        record_location = f"{table_name}.{id_field}"
                        break

                if record_id_match:
                    record_found = True
                    # Extract the actual field value
                    if evidence.field_name in record:
                        actual_value = str(record[evidence.field_name])
                    else:
                        actual_value = f"FIELD_NOT_FOUND: {evidence.field_name}"
                    break

            if record_found:
                break

        if not record_found:
            return False, False, f"Record ID '{evidence.record_id}' not found"

        # Compare claimed value with actual value
        value_accurate = self._compare_values(evidence.data_value, actual_value)

        return record_found, value_accurate, actual_value

    def _compare_values(self, claimed_value: str, actual_value: str) -> bool:
        """Compare claimed value with actual value, handling different data types"""

        # Direct string comparison first
        if claimed_value.strip() == actual_value.strip():
            return True

        # Handle numeric comparisons with tolerance
        try:
            claimed_numeric = float(claimed_value.replace('$', '').replace(',', ''))
            actual_numeric = float(actual_value.replace('$', '').replace(',', ''))

            # Check if within tolerance
            if abs(claimed_numeric - actual_numeric) <= self.tolerance_for_numeric_values:
                return True

            # Check if they're equal when rounded to 2 decimal places (common for currency)
            if round(claimed_numeric, 2) == round(actual_numeric, 2):
                return True

        except (ValueError, AttributeError):
            # Not numeric values, continue with string comparison
            pass

        # Handle case-insensitive comparison
        if claimed_value.lower().strip() == actual_value.lower().strip():
            return True

        # Handle partial matches for longer strings
        if len(claimed_value) > 10 and len(actual_value) > 10:
            if claimed_value.lower() in actual_value.lower() or actual_value.lower() in claimed_value.lower():
                return True

        return False

    def _calculate_quality_score(self, verification_results: List[Dict[str, Any]]) -> float:
        """Calculate overall evidence quality score"""
        if not verification_results:
            return 0.0

        # Weight different factors
        record_found_weight = 0.4
        value_accuracy_weight = 0.6

        records_found_ratio = sum(1 for r in verification_results if r['record_found']) / len(verification_results)

        # Only count value accuracy for records that were found
        found_records = [r for r in verification_results if r['record_found']]
        if found_records:
            values_accurate_ratio = sum(1 for r in found_records if r['value_accurate']) / len(found_records)
        else:
            values_accurate_ratio = 0.0

        quality_score = (
            records_found_ratio * record_found_weight +
            values_accurate_ratio * value_accuracy_weight
        )

        return min(quality_score, 1.0)

    def _generate_verification_details(self, verification_results: List[Dict[str, Any]],
                                     invalid_references: List[str],
                                     value_mismatches: List[str]) -> str:
        """Generate detailed verification analysis"""

        total_evidence = len(verification_results)
        records_found = sum(1 for r in verification_results if r['record_found'])
        values_accurate = sum(1 for r in verification_results if r['record_found'] and r['value_accurate'])

        details = [
            f"Evidence Verification Summary: {total_evidence} evidence snippets analyzed",
            f"Records Found: {records_found}/{total_evidence} ({records_found/total_evidence*100:.1f}%)",
            f"Values Accurate: {values_accurate}/{records_found} ({values_accurate/max(records_found,1)*100:.1f}%)"
        ]

        if invalid_references:
            details.append(f"Invalid References: {len(invalid_references)} found")
            for ref in invalid_references[:3]:  # Show first 3 examples
                details.append(f"  - {ref}")

        if value_mismatches:
            details.append(f"Value Mismatches: {len(value_mismatches)} found")
            for mismatch in value_mismatches[:3]:  # Show first 3 examples
                details.append(f"  - {mismatch}")

        if not invalid_references and not value_mismatches:
            details.append("All evidence verified successfully against dataset records")

        return " | ".join(details)

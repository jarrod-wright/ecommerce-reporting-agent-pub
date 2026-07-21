"""
ERA PII Sanitization Integration

Integrates TDG's PII sanitization capabilities with ERA testing workflows.
Provides enterprise-grade PII removal while preserving data utility for testing.
"""

import re
from typing import Any, Dict, List

import pandas as pd

from test_data_generator.poc.pii_sanitization_poc import (
    PIIDetectionResult,
    PIISanitizationPOC,
)

# PIIDetectionResult now imported from real TDG library


class RemovedMockPIISanitizationPOC:
    """REMOVED: Mock implementation replaced with real TDG PIISanitizationPOC integration."""

    def __init__(self):
        """Initialize PII detection patterns and sanitization rules."""
        self.pii_patterns = self._initialize_pii_patterns()
        self.sanitization_rules = self._initialize_sanitization_rules()

    def _initialize_pii_patterns(self) -> Dict[str, str]:
        """Initialize regex patterns for common PII types."""
        return {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            "ssn": r'\b(?:\d{3}-?\d{2}-?\d{4})\b',
            "credit_card": r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
            "person_name": r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            "address": r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b',
            "ip_address": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            "date_of_birth": r'\b(?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12][0-9]|3[01])[-/](?:19|20)\d{2}\b'
        }

    def _initialize_sanitization_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize sanitization rules for each PII type."""
        return {
            "email": {
                "method": "replace_format",
                "replacement": "user{id}@example.com"
            },
            "phone": {
                "method": "mask_partial",
                "pattern": "***-***-{last4}"
            },
            "ssn": {
                "method": "replace",
                "replacement": "***-**-****"
            },
            "credit_card": {
                "method": "mask_partial",
                "pattern": "****-****-****-{last4}"
            },
            "person_name": {
                "method": "replace",
                "replacement": "John Doe"
            },
            "address": {
                "method": "replace",
                "replacement": "123 Main Street"
            },
            "ip_address": {
                "method": "replace",
                "replacement": "192.168.1.1"
            },
            "date_of_birth": {
                "method": "replace",
                "replacement": "01/01/1990"
            }
        }

    def run_comprehensive_pii_detection(self, data_records: List[Dict[str, Any]]) -> Dict[str, PIIDetectionResult]:
        """Run PII detection across all fields and PII types."""
        results = {}

        for pii_type, pattern in self.pii_patterns.items():
            for record in data_records:
                for field_name, field_value in record.items():
                    if field_value is None:
                        continue

                    field_str = str(field_value)
                    matches = re.findall(pattern, field_str, re.IGNORECASE)

                    result_key = f"{field_name}_{pii_type}"
                    if result_key not in results:
                        results[result_key] = PIIDetectionResult(
                            pii_type=pii_type,
                            field_name=field_name,
                            detected_count=0,
                            total_count=len(data_records),
                            detection_rate=0.0
                        )

                    if matches:
                        results[result_key].detected_count += len(matches)

        # Calculate detection rates
        for result in results.values():
            if result.total_count > 0:
                result.detection_rate = result.detected_count / result.total_count

        return results


class ERAPIISanitizer:
    """ERA-specific PII sanitization using TDG capabilities."""

    def __init__(self):
        """Initialize with real TDG PII sanitization capabilities."""
        self.pii_scrubber = PIISanitizationPOC()  # Real TDG class
        self.era_specific_patterns = self._load_era_specific_patterns()
        self.sanitization_counter = 0

    def _load_era_specific_patterns(self) -> Dict[str, str]:
        """Load ERA-specific PII patterns that should NOT be sanitized."""
        return {
            # These are business identifiers, not PII
            "customer_id": r'cust_\d+',
            "order_id": r'order_\d+',
            "order_number": r'\d{4,7}',

            # ERA requires these for processing
            "iso_timestamp": r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            "date_ymd": r'\d{4}-\d{2}-\d{2}',

            # Business metrics (not PII)
            "currency_amount": r'\d+\.\d{2}',
            "device_category": r'(desktop|mobile|tablet)',
            "status_values": r'(paid|pending|refunded|fulfilled|unfulfilled|shipped)'
        }

    def sanitize_era_dataset(self, era_dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize complete ERA dataset while preserving business logic."""

        sanitized_dataset = {}

        # Sanitize Shopify orders
        if 'shopify_orders' in era_dataset:
            shopify_data = era_dataset['shopify_orders']
            sanitized_dataset['shopify_orders'] = self.sanitize_shopify_orders(shopify_data)

        # Sanitize GA4 sessions (minimal PII risk, but comprehensive coverage)
        if 'ga4_sessions' in era_dataset:
            ga4_data = era_dataset['ga4_sessions']
            sanitized_dataset['ga4_sessions'] = self.sanitize_ga4_sessions(ga4_data)

        # Preserve customer data with sanitization
        if 'customers' in era_dataset:
            customers_data = era_dataset['customers']
            sanitized_dataset['customers'] = self.sanitize_customer_data(customers_data)

        if 'shopify_customers' in era_dataset:
            customers_data = era_dataset['shopify_customers']
            sanitized_dataset['shopify_customers'] = self.sanitize_customer_data(customers_data)

        return sanitized_dataset

    def sanitize_shopify_orders(self, shopify_data: Any) -> Any:
        """Sanitize Shopify orders data while preserving business logic."""

        # Handle both MockDataFrame and list formats
        if hasattr(shopify_data, 'to_dict'):
            records = shopify_data.to_dict('records')
        else:
            records = shopify_data if isinstance(shopify_data, list) else [shopify_data]

        sanitized_records = []

        for record in records:
            sanitized_record = record.copy()

            # Sanitize each field based on PII detection
            for field_name, field_value in record.items():
                if field_value is None:
                    continue

                field_str = str(field_value)

                # Skip ERA business identifiers
                if self._is_era_business_identifier(field_name, field_str):
                    continue

                # Apply PII sanitization
                sanitized_value = self._sanitize_field_value(field_name, field_str)
                sanitized_record[field_name] = sanitized_value

            sanitized_records.append(sanitized_record)

        # Return pandas DataFrame for consistent data handling
        return pd.DataFrame(sanitized_records)

    def sanitize_ga4_sessions(self, ga4_data: Any) -> Any:
        """Sanitize GA4 sessions data (minimal PII risk)."""

        # Handle both MockDataFrame and list formats
        if hasattr(ga4_data, 'to_dict'):
            records = ga4_data.to_dict('records')
        else:
            records = ga4_data if isinstance(ga4_data, list) else [ga4_data]

        sanitized_records = []

        for record in records:
            sanitized_record = record.copy()

            # GA4 data typically has minimal PII risk, but check text fields
            for field_name, field_value in record.items():
                if field_value is None:
                    continue

                # Only sanitize potential text fields that might contain PII
                if field_name in ['user_agent', 'referrer', 'custom_dimensions']:
                    field_str = str(field_value)
                    sanitized_value = self._sanitize_field_value(field_name, field_str)
                    sanitized_record[field_name] = sanitized_value

            sanitized_records.append(sanitized_record)

        # Return pandas DataFrame for consistent data handling
        return pd.DataFrame(sanitized_records)

    def sanitize_customer_data(self, customer_data: Any) -> Any:
        """Sanitize customer data with comprehensive PII removal."""

        # Handle both MockDataFrame and list formats
        if hasattr(customer_data, 'to_dict'):
            records = customer_data.to_dict('records')
        else:
            records = customer_data if isinstance(customer_data, list) else [customer_data]

        sanitized_records = []

        for record in records:
            sanitized_record = record.copy()

            # Customer data has high PII risk - sanitize comprehensively
            for field_name, field_value in record.items():
                if field_value is None:
                    continue

                field_str = str(field_value)

                # Skip customer_id (business identifier)
                if field_name == 'customer_id':
                    continue

                # Sanitize PII fields
                sanitized_value = self._sanitize_field_value(field_name, field_str)
                sanitized_record[field_name] = sanitized_value

            sanitized_records.append(sanitized_record)

        # Return pandas DataFrame for consistent data handling
        return pd.DataFrame(sanitized_records)

    def _is_era_business_identifier(self, field_name: str, field_value: str) -> bool:
        """Check if field is an ERA business identifier that should NOT be sanitized."""

        # Check field names that are business identifiers
        business_id_fields = ['customer_id', 'order_id', 'id', 'order_number']
        if field_name in business_id_fields:
            return True

        # Check field patterns
        for pattern_name, pattern in self.era_specific_patterns.items():
            if re.match(pattern, field_value):
                return True

        return False

    def _sanitize_field_value(self, field_name: str, field_value: str) -> str:
        """Sanitize a field value by removing PII patterns."""

        sanitized_value = field_value

        # Apply all PII sanitization rules
        for pii_type, pattern in self.pii_scrubber.pii_patterns.items():
            rule = self.pii_scrubber.sanitization_rules.get(pii_type, {})

            if re.search(pattern, sanitized_value, re.IGNORECASE):
                self.sanitization_counter += 1

                method = rule.get("method", "replace")

                if method == "replace":
                    replacement = rule.get("replacement", "[REDACTED]")
                    sanitized_value = re.sub(pattern, replacement, sanitized_value, flags=re.IGNORECASE)

                elif method == "replace_format":
                    replacement_template = rule.get("replacement", "placeholder{id}")
                    replacement = replacement_template.format(id=self.sanitization_counter)
                    sanitized_value = re.sub(pattern, replacement, sanitized_value, flags=re.IGNORECASE)

                elif method == "mask_partial":
                    # Extract last 4 characters for partial masking
                    matches = re.finditer(pattern, sanitized_value, re.IGNORECASE)
                    for match in matches:
                        original = match.group()
                        if len(original) >= 4:
                            last4 = original[-4:]
                            mask_pattern = rule.get("pattern", "****{last4}")
                            masked = mask_pattern.format(last4=last4)
                            sanitized_value = sanitized_value.replace(original, masked)

        return sanitized_value

    def validate_sanitization_effectiveness(self, original: Dict[str, Any], sanitized: Dict[str, Any]) -> Dict[str, float]:
        """Validate >99.9% PII removal while preserving data utility."""

        effectiveness_report = {}

        for dataset_name in ['shopify_orders', 'ga4_sessions', 'customers', 'shopify_customers']:
            if dataset_name not in original or dataset_name not in sanitized:
                continue

            original_data = original[dataset_name]
            sanitized_data = sanitized[dataset_name]

            # Convert to pandas DataFrames for TDG analysis
            if hasattr(original_data, 'to_dict'):
                # Already a DataFrame
                original_df = original_data
                sanitized_df = sanitized_data
            else:
                # Convert list to DataFrame
                original_records = original_data if isinstance(original_data, list) else [original_data]
                sanitized_records = sanitized_data if isinstance(sanitized_data, list) else [sanitized_data]
                original_df = pd.DataFrame(original_records)
                sanitized_df = pd.DataFrame(sanitized_records)

            # Use TDG's PII detection for validation
            original_pii = self.pii_scrubber.run_comprehensive_pii_detection(original_df)
            sanitized_pii = self.pii_scrubber.run_comprehensive_pii_detection(sanitized_df)

            # Calculate removal effectiveness
            total_original_pii = sum(result.detected_count for result in original_pii.values())
            total_remaining_pii = sum(result.detected_count for result in sanitized_pii.values())

            removal_rate = 1.0 - (total_remaining_pii / total_original_pii) if total_original_pii > 0 else 1.0
            effectiveness_report[dataset_name] = removal_rate

        return effectiveness_report

    def generate_sanitization_report(self, original: Dict[str, Any], sanitized: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive sanitization audit report."""

        effectiveness_results = self.validate_sanitization_effectiveness(original, sanitized)

        report = {
            "sanitization_summary": {
                "total_fields_processed": self.sanitization_counter,
                "datasets_processed": list(effectiveness_results.keys()),
                "overall_effectiveness": sum(effectiveness_results.values()) / len(effectiveness_results) if effectiveness_results else 0.0
            },
            "effectiveness_by_dataset": effectiveness_results,
            "compliance_status": {
                "meets_99_9_percent_requirement": all(rate >= 0.999 for rate in effectiveness_results.values()),
                "datasets_passing": [name for name, rate in effectiveness_results.items() if rate >= 0.999],
                "datasets_failing": [name for name, rate in effectiveness_results.items() if rate < 0.999]
            },
            "audit_trail": {
                "sanitization_patterns_applied": list(self.pii_scrubber.pii_patterns.keys()),
                "era_identifiers_preserved": list(self.era_specific_patterns.keys()),
                "processing_timestamp": "2024-09-08T23:30:00Z"  # Mock timestamp
            }
        }

        return report


class RemovedMockSanitizedDataFrame:
    """REMOVED: Mock DataFrame replaced with real pandas DataFrames."""

    def __init__(self, data: List[Dict[str, Any]]):
        """Initialize with sanitized data."""
        self.data = data
        self._columns = list(data[0].keys()) if data else []

    @property
    def columns(self) -> List[str]:
        """Get column names."""
        return self._columns

    def __len__(self) -> int:
        """Get row count."""
        return len(self.data)

    def __getitem__(self, column: str) -> List[Any]:
        """Get column values."""
        return [row.get(column) for row in self.data]

    def to_dict(self, orient: str = 'records') -> List[Dict[str, Any]]:
        """Convert to dictionary format."""
        if orient == 'records':
            return self.data
        return self.data

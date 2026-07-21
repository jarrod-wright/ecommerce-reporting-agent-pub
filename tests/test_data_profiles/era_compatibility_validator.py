"""
ERA Compatibility Validator

Advanced validation for ERA ReportingAgentState compatibility and Polars processing.
Extends the basic profile validation with integration testing capabilities.
"""

import json
import re
from typing import Any, Dict, List, Optional


class MockReportingAgentState:
    """Mock ERA ReportingAgentState for compatibility testing."""

    def __init__(self, report_config: Dict[str, Any]):
        """Initialize with report configuration."""
        self.report_config = report_config
        self.raw_shopify_data: Optional[List[Dict[str, Any]]] = None
        self.raw_ga4_data: Optional[List[Dict[str, Any]]] = None
        self.processed_dataframe_json: Optional[str] = None
        self.generated_insights: Optional[Dict[str, Any]] = None
        self.visualization_filepaths: List[str] = []
        self.final_report_path: Optional[str] = None
        self.error_message: Optional[str] = None
        self.human_decision: Optional[str] = None


class MockPolarsProcessor:
    """Mock Polars processing for compatibility testing."""

    @staticmethod
    def process_data_node(state: MockReportingAgentState) -> MockReportingAgentState:
        """Mock process_data_node functionality."""

        if not state.raw_shopify_data or not state.raw_ga4_data:
            state.error_message = "Missing required data"
            return state

        try:
            # Simulate Polars processing
            shopify_data = state.raw_shopify_data
            ga4_data = state.raw_ga4_data

            # Validate data can be processed
            for order in shopify_data:
                # Test float conversion of total_price
                float(order['total_price'])

                # Validate date format
                if 'created_at' in order:
                    # Simple date validation
                    if not re.match(r'\d{4}-\d{2}-\d{2}', order['created_at']):
                        raise ValueError(f"Invalid date format: {order['created_at']}")

            for session in ga4_data:
                # Validate date format
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', session['date']):
                    raise ValueError(f"Invalid GA4 date format: {session['date']}")

                # Validate numeric fields
                if session.get('page_views', 0) <= 0:
                    raise ValueError("page_views must be positive")
                if session.get('duration', 0) <= 0:
                    raise ValueError("duration must be positive")

            # Create mock unified dataset
            unified_data = []

            # Group by date (simplified)
            date_groups = {}

            # Process Shopify data
            for order in shopify_data:
                date = order['created_at'][:10]  # Extract date part
                if date not in date_groups:
                    date_groups[date] = {'date': date, 'shopify_revenue': 0, 'ga4_sessions': 0, 'page_views': 0}
                date_groups[date]['shopify_revenue'] += float(order['total_price'])

            # Process GA4 data
            for session in ga4_data:
                date = session['date']
                if date not in date_groups:
                    date_groups[date] = {'date': date, 'shopify_revenue': 0, 'ga4_sessions': 0, 'page_views': 0}
                date_groups[date]['ga4_sessions'] += session.get('sessions', 1)
                date_groups[date]['page_views'] += session.get('page_views', 1)

            unified_data = list(date_groups.values())

            # Serialize to JSON (mock Polars to_json functionality)
            state.processed_dataframe_json = json.dumps(unified_data)

        except Exception as e:
            state.error_message = f"Processing error: {str(e)}"

        return state


class ERACompatibilityValidator:
    """Advanced ERA compatibility validation."""

    def __init__(self):
        """Initialize the compatibility validator."""
        self.polars_processor = MockPolarsProcessor()

    def test_era_state_compatibility(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Test compatibility with ERA ReportingAgentState."""

        results = {
            'test_name': 'era_state_compatibility',
            'passed': True,
            'errors': [],
            'validations': {}
        }

        try:
            # Create mock ERA state
            state = MockReportingAgentState({
                "date_range": "2024-01-01 to 2024-12-31"
            })

            # Test data assignment
            state.raw_shopify_data = dataset['shopify_orders'].to_dict('records')
            state.raw_ga4_data = dataset['ga4_sessions'].to_dict('records')

            results['validations']['data_assignment'] = '✓ Data successfully assigned to ERA state'

            # Test processing
            processed_state = self.polars_processor.process_data_node(state)

            if processed_state.error_message:
                results['passed'] = False
                results['errors'].append(f"Processing failed: {processed_state.error_message}")
            else:
                results['validations']['processing'] = '✓ Data processing completed successfully'

                # Validate processed output
                if processed_state.processed_dataframe_json:
                    unified_data = json.loads(processed_state.processed_dataframe_json)

                    if unified_data and len(unified_data) > 0:
                        results['validations']['unified_data'] = f'✓ Generated {len(unified_data)} unified records'

                        # Check required columns
                        sample_record = unified_data[0]
                        required_columns = ['date', 'shopify_revenue', 'ga4_sessions', 'page_views']
                        missing_columns = [col for col in required_columns if col not in sample_record]

                        if missing_columns:
                            results['passed'] = False
                            results['errors'].append(f"Missing unified data columns: {missing_columns}")
                        else:
                            results['validations']['unified_columns'] = '✓ All required unified columns present'
                    else:
                        results['passed'] = False
                        results['errors'].append("No unified data generated")
                else:
                    results['passed'] = False
                    results['errors'].append("No processed dataframe JSON generated")

        except Exception as e:
            results['passed'] = False
            results['errors'].append(f"ERA compatibility test error: {str(e)}")

        return results

    def test_performance_requirements(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Test performance requirements."""

        import time

        results = {
            'test_name': 'performance_requirements',
            'passed': True,
            'errors': [],
            'validations': {}
        }

        try:
            # Test processing time
            start_time = time.perf_counter()

            state = MockReportingAgentState({
                "date_range": "2024-01-01 to 2024-12-31"
            })

            state.raw_shopify_data = dataset['shopify_orders'].to_dict('records')
            state.raw_ga4_data = dataset['ga4_sessions'].to_dict('records')

            processed_state = self.polars_processor.process_data_node(state)

            processing_time = time.perf_counter() - start_time

            # Performance thresholds
            if processing_time < 30.0:  # 30 second threshold
                results['validations']['processing_speed'] = f'✓ Processing completed in {processing_time:.3f}s (<30s required)'
            else:
                results['passed'] = False
                results['errors'].append(f"Processing too slow: {processing_time:.3f}s (>30s)")

            # Memory estimation (rough)
            shopify_records = len(dataset['shopify_orders'])
            ga4_records = len(dataset['ga4_sessions'])
            total_records = shopify_records + ga4_records

            estimated_memory_mb = (total_records * 1000) / (1024 * 1024)  # Rough estimate

            if estimated_memory_mb < 100:  # 100MB threshold
                results['validations']['memory_usage'] = f'✓ Estimated memory usage: {estimated_memory_mb:.1f}MB (<100MB)'
            else:
                results['passed'] = False
                results['errors'].append(f"Estimated memory usage too high: {estimated_memory_mb:.1f}MB (>100MB)")

        except Exception as e:
            results['passed'] = False
            results['errors'].append(f"Performance test error: {str(e)}")

        return results

    def test_data_quality_metrics(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Test data quality metrics."""

        results = {
            'test_name': 'data_quality_metrics',
            'passed': True,
            'errors': [],
            'validations': {}
        }

        try:
            shopify_data = dataset['shopify_orders']
            ga4_data = dataset['ga4_sessions']

            # Test data completeness
            shopify_completeness = self._calculate_completeness(shopify_data.to_dict('records'))
            ga4_completeness = self._calculate_completeness(ga4_data.to_dict('records'))

            if shopify_completeness >= 0.8:  # 80% completeness threshold
                results['validations']['shopify_completeness'] = f'✓ Shopify data {shopify_completeness:.1%} complete'
            else:
                results['passed'] = False
                results['errors'].append(f"Shopify data only {shopify_completeness:.1%} complete (<80%)")

            if ga4_completeness >= 0.8:
                results['validations']['ga4_completeness'] = f'✓ GA4 data {ga4_completeness:.1%} complete'
            else:
                results['passed'] = False
                results['errors'].append(f"GA4 data only {ga4_completeness:.1%} complete (<80%)")

            # Test data consistency
            customer_ids_orders = set(shopify_data['customer_id'])
            customer_ids_customers = set(dataset['customers']['customer_id'])

            consistency_rate = len(customer_ids_orders & customer_ids_customers) / len(customer_ids_orders)

            if consistency_rate >= 0.95:  # 95% consistency threshold
                results['validations']['referential_consistency'] = f'✓ Referential integrity {consistency_rate:.1%}'
            else:
                results['passed'] = False
                results['errors'].append(f"Referential integrity only {consistency_rate:.1%} (<95%)")

        except Exception as e:
            results['passed'] = False
            results['errors'].append(f"Data quality test error: {str(e)}")

        return results

    def _calculate_completeness(self, data: List[Dict[str, Any]]) -> float:
        """Calculate data completeness rate."""
        if not data:
            return 0.0

        total_fields = len(data) * len(data[0])
        non_null_fields = 0

        for record in data:
            for value in record.values():
                if value is not None and value != '':
                    non_null_fields += 1

        return non_null_fields / total_fields if total_fields > 0 else 0.0

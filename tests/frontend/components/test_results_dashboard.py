from unittest.mock import MagicMock, patch

from agent.models.insights import ReportInsights
from streamlit_app.components.results_dashboard import render_results_dashboard


def test_results_dashboard_displays_contextual_upsell_message():
    """Test that render_results_dashboard displays contextual upsell messages based on data quality issues."""

    # Scenario 1: Data Quality Issue - should trigger upsell message
    with patch('streamlit_app.components.results_dashboard.st.info') as mock_info:
        # Create ReportInsights with data quality issue containing "inconsistent"
        report_with_issue = ReportInsights(
            summary="Sample summary with performance data",
            key_metrics={
                "total_revenue": 150000.00,
                "conversion_rate": 2.5,
                "average_order_value": 75.50,
                "total_orders": 1000
            },
            recommendations=[
                "Optimize checkout flow to reduce abandonment",
                "Implement personalized product recommendations"
            ],
            data_quality_notes="Data shows inconsistent tracking patterns across channels which may affect accuracy of the analysis."
        )

        # Mock other st components to avoid execution issues
        mock_column = MagicMock()
        with patch('streamlit_app.components.results_dashboard.st.header'), \
             patch('streamlit_app.components.results_dashboard.st.columns', return_value=[mock_column, mock_column, mock_column, mock_column]), \
             patch('streamlit_app.components.results_dashboard.st.metric'), \
             patch('streamlit_app.components.results_dashboard.st.write'), \
             patch('streamlit_app.components.results_dashboard.st.expander'), \
             patch('streamlit_app.components.results_dashboard.st.subheader'), \
             patch('streamlit_app.components.results_dashboard.st.dataframe'), \
             patch('streamlit_app.components.results_dashboard.st.plotly_chart'):

            render_results_dashboard(report_with_issue)

        # Assert that st.info was called with Data Readiness Assessment message
        assert mock_info.call_count >= 1
        info_calls = [call.args[0] for call in mock_info.call_args_list]
        assert any("Data Readiness Assessment" in call for call in info_calls), \
            f"Expected 'Data Readiness Assessment' message, but got: {info_calls}"

    # Scenario 2: No Data Quality Issue - should NOT trigger upsell message
    with patch('streamlit_app.components.results_dashboard.st.info') as mock_info:
        # Create ReportInsights with no data quality issues
        report_without_issue = ReportInsights(
            summary="Clean performance summary with reliable metrics",
            key_metrics={
                "total_revenue": 150000.00,
                "conversion_rate": 2.5,
                "average_order_value": 75.50,
                "total_orders": 1000
            },
            recommendations=[
                "Continue current optimization strategies",
                "Scale successful marketing campaigns"
            ],
            data_quality_notes="All data sources are properly configured and providing accurate tracking data."
        )

        # Mock other st components to avoid execution issues
        mock_column = MagicMock()
        with patch('streamlit_app.components.results_dashboard.st.header'), \
             patch('streamlit_app.components.results_dashboard.st.columns', return_value=[mock_column, mock_column, mock_column, mock_column]), \
             patch('streamlit_app.components.results_dashboard.st.metric'), \
             patch('streamlit_app.components.results_dashboard.st.write'), \
             patch('streamlit_app.components.results_dashboard.st.expander'), \
             patch('streamlit_app.components.results_dashboard.st.subheader'), \
             patch('streamlit_app.components.results_dashboard.st.dataframe'), \
             patch('streamlit_app.components.results_dashboard.st.plotly_chart'):

            render_results_dashboard(report_without_issue)

        # Assert that st.info was NOT called with Data Readiness Assessment message
        if mock_info.call_count > 0:
            info_calls = [call.args[0] for call in mock_info.call_args_list]
            assert not any("Data Readiness Assessment" in call for call in info_calls), \
                f"Did not expect 'Data Readiness Assessment' message, but found: {info_calls}"

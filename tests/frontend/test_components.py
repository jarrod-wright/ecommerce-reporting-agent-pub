"""Tests for streamlit_app components following the High Trust UI/UX Playbook."""

from unittest.mock import patch

from agent.models.insights import ReportInsights


def test_render_results_dashboard_displays_metrics_and_charts():
    """Test that render_results_dashboard properly displays metrics and visualizations."""

    # Create sample ReportInsights data following the model structure
    sample_insights = ReportInsights(
        summary="Strong performance with 15% revenue growth in Q2 2025",
        key_metrics={
            "total_revenue": 125000.50,
            "conversion_rate": 3.2,
            "average_order_value": 87.50,
            "total_orders": 1429,
            "revenue_growth": 15.2
        },
        recommendations=[
            "Focus on mobile optimization to improve conversion rates",
            "Implement retargeting campaigns for abandoned carts",
            "Expand inventory for top-performing product categories"
        ],
        data_quality_notes="Data complete for 90-day analysis period"
    )

    with patch('streamlit.metric') as mock_metric, \
         patch('streamlit.plotly_chart') as mock_plotly_chart, \
         patch('streamlit.header') as mock_header:

        # Import here to avoid circular imports during test discovery
        from streamlit_app.components import render_results_dashboard

        # Call the function that should exist
        render_results_dashboard(sample_insights)

        # Verify st.metric calls for key executive metrics
        expected_metric_calls = [
            ("Total Revenue", "$125,000.50", "+15.2%"),
            ("Conversion Rate", "3.2%", None),
            ("Average Order Value", "$87.50", None),
            ("Total Orders", "1,429", None)
        ]

        # Check that st.metric was called with expected values
        assert mock_metric.call_count == len(expected_metric_calls)

        # Verify specific metric calls
        for i, (label, value, delta) in enumerate(expected_metric_calls):
            call_args = mock_metric.call_args_list[i]
            assert call_args[1]['label'] == label
            assert call_args[1]['value'] == value
            if delta:
                assert call_args[1]['delta'] == delta

        # Verify that plotly charts are generated for visualizations
        # Should have at least one chart for the dashboard
        assert mock_plotly_chart.call_count >= 1

        # Verify proper section headers per High Trust UI/UX Playbook
        mock_header.assert_any_call("Executive Summary")
        mock_header.assert_any_call("Key Performance Indicators")

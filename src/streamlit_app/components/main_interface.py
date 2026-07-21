# streamlit_app/components/main_interface.py

import streamlit as st

from agent.models.insights import ReportInsights

from ..api_client import trigger_report_generation
from .feedback import display_error_message, display_success_message
from .results_dashboard import render_results_dashboard


def render_main_interface():
    """Renders the main user interface for report generation."""

    st.header("Generate Your Report")

    # Mandate 3.5 (Focus) & 3.1 (Clarity)
    if st.button(
        "Generate My Report",
        type="primary",
        help="Click to run the AI analysis and generate your PDF report."
    ):
        # Mandate 3.2 (Continuous Feedback)
        with st.spinner("AI agent at work... Analyzing data and generating insights..."):
            result_bytes = trigger_report_generation({
                "report_title": "Weekly Performance Report",
                "date_range": "last_7_days"
            })

        # Mandate 3.2 (Feedback)
        if result_bytes:
            st.session_state.report_bytes = result_bytes

            # Generate sample insights for dashboard display
            # In production, this would come from the API response
            sample_insights = ReportInsights(
                summary="Strong quarterly performance with significant growth in key metrics",
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
            st.session_state.report_insights = sample_insights

            display_success_message("Report generated successfully!")
        else:
            st.session_state.report_bytes = None
            st.session_state.report_insights = None
            display_error_message("Failed to generate report. Please try again later.")

    # Mandate: Executive Results Dashboard Display
    if st.session_state.get("report_insights"):
        st.divider()
        render_results_dashboard(st.session_state.report_insights)

    # Mandate: The Final Deliverable (Conditional display)
    if st.session_state.get("report_bytes"):
        st.divider()
        st.download_button(
            label="Download Full Report (PDF)",
            data=st.session_state.report_bytes,
            file_name="E-commerce_Performance_Report.pdf",
            mime="application/pdf"
        )

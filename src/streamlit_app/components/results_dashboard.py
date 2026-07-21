"""Results dashboard component implementing High Trust UI/UX Playbook design principles."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from agent.models.insights import ReportInsights


def render_results_dashboard(report_insights: ReportInsights):
    """
    Render the executive results dashboard following the High Trust UI/UX Playbook.
    
    Implements the prescribed Information Hierarchy:
    1. Executive Summary (Top) - st.metric components with key KPIs
    2. Key Insights & Visual Evidence (Middle) - Headers and plotly charts
    3. Detailed Data Appendix (Bottom) - Expandable dataframe section
    
    Args:
        report_insights: ReportInsights object containing all dashboard data
    """

    # Section 1: Executive Summary (Top) - "Bottom Line Up Front" (BLUF)
    st.header("Executive Summary")

    # Create metrics layout using columns for professional spacing
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        revenue = report_insights.key_metrics.get("total_revenue", 0)
        revenue_growth = report_insights.key_metrics.get("revenue_growth")
        delta_str = f"+{revenue_growth}%" if revenue_growth and revenue_growth > 0 else None
        st.metric(
            label="Total Revenue",
            value=f"${revenue:,.2f}",
            delta=delta_str,
            help="Total revenue generated during the analysis period"
        )

    with col2:
        conversion_rate = report_insights.key_metrics.get("conversion_rate", 0)
        st.metric(
            label="Conversion Rate",
            value=f"{conversion_rate}%",
            help="Percentage of visitors who completed a purchase"
        )

    with col3:
        aov = report_insights.key_metrics.get("average_order_value", 0)
        st.metric(
            label="Average Order Value",
            value=f"${aov:.2f}",
            help="Average value per completed order"
        )

    with col4:
        total_orders = report_insights.key_metrics.get("total_orders", 0)
        st.metric(
            label="Total Orders",
            value=f"{total_orders:,}",
            help="Total number of completed orders"
        )

    # Section 2: Key Insights & Visual Evidence (Middle)
    st.header("Key Performance Indicators")

    # Summary insights narrative
    st.write(report_insights.summary)

    # Generate sample visualization for revenue trends
    _render_revenue_trend_chart(report_insights.key_metrics)

    # Generate sample visualization for conversion funnel
    _render_conversion_funnel_chart(report_insights.key_metrics)

    # Section 3: Strategic Recommendations
    st.header("Strategic Recommendations")
    for i, recommendation in enumerate(report_insights.recommendations, 1):
        st.write(f"**{i}.** {recommendation}")

    # Section 3.5: Contextual Upsell Logic - Data Quality Assessment
    data_quality_keywords = ["inconsistent", "missing", "gaps"]
    if any(keyword in report_insights.data_quality_notes.lower() for keyword in data_quality_keywords):
        st.info(
            "💡 **Unlock Deeper Insights:** Our AI noticed potential data quality issues. "
            "A full 'Data Readiness Assessment' can help you build a rock-solid data foundation. "
            "[Learn More](#)"
        )

    # Section 4: Detailed Data Appendix (Bottom) - Progressive Disclosure
    with st.expander("📊 Detailed Data Analysis", expanded=False):
        st.subheader("Data Quality Assessment")
        st.info(report_insights.data_quality_notes)

        # Sample detailed data table
        sample_data = _generate_sample_dataframe(report_insights.key_metrics)
        st.dataframe(
            sample_data,
            use_container_width=True,
            hide_index=True
        )


def _render_revenue_trend_chart(key_metrics: dict):
    """Generate revenue trend visualization."""
    # Sample data for demonstration - in production this would come from actual data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='ME')
    revenue_values = [
        45000, 47000, 52000, 48000, 55000, 58000,
        62000, 59000, 65000, 68000, 72000, key_metrics.get("total_revenue", 75000) / 12
    ]

    fig = px.line(
        x=dates,
        y=revenue_values,
        title="Monthly Revenue Trend",
        labels={'x': 'Month', 'y': 'Revenue ($)'},
        color_discrete_sequence=['#2563EB']  # Brand Blue from UX Playbook
    )

    fig.update_layout(
        font_family="Inter",
        title_font_size=16,
        title_font_color="#1A202C",  # Slate 900
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)


def _render_conversion_funnel_chart(key_metrics: dict):
    """Generate conversion funnel visualization."""
    # Sample funnel data based on metrics
    total_visitors = key_metrics.get("total_orders", 1000) * 100 // key_metrics.get("conversion_rate", 3)
    add_to_cart = total_visitors * 0.25
    checkout_start = add_to_cart * 0.40
    completed_orders = key_metrics.get("total_orders", 1000)

    fig = go.Figure(go.Funnel(
        y=["Website Visitors", "Add to Cart", "Checkout Started", "Orders Completed"],
        x=[total_visitors, add_to_cart, checkout_start, completed_orders],
        marker={
            "color": ["#F8FAFC", "#CBD5E1", "#475569", "#2563EB"],  # UX Playbook colors
            "line": {"width": 2, "color": "#1A202C"}
        }
    ))

    fig.update_layout(
        title="E-commerce Conversion Funnel",
        font_family="Inter",
        title_font_size=16,
        title_font_color="#1A202C",
        paper_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)


def _generate_sample_dataframe(key_metrics: dict):
    """Generate sample detailed data for the appendix section."""
    return pd.DataFrame({
        'Metric': [
            'Total Revenue',
            'Conversion Rate',
            'Average Order Value',
            'Total Orders',
            'Revenue Growth'
        ],
        'Value': [
            f"${key_metrics.get('total_revenue', 0):,.2f}",
            f"{key_metrics.get('conversion_rate', 0)}%",
            f"${key_metrics.get('average_order_value', 0):.2f}",
            f"{key_metrics.get('total_orders', 0):,}",
            f"{key_metrics.get('revenue_growth', 0)}%"
        ],
        'Category': [
            'Financial',
            'Performance',
            'Financial',
            'Volume',
            'Growth'
        ]
    })

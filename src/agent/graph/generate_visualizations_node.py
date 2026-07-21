"""Generate visualizations node for the e-commerce performance reporting agent."""

import base64
import json
from typing import Any, Dict

import plotly.graph_objects as go
import polars as pl
import structlog

from agent.models.state import ReportingAgentState


def generate_visualizations_node(state: ReportingAgentState) -> Dict[str, Any]:
    """Generate visualizations from processed e-commerce performance data.

    This node takes the processed DataFrame containing unified Shopify revenue
    and GA4 analytics data, creates interactive visualizations using Plotly,
    and exports them as base64-encoded data URI strings following the HTML-first
    established pattern for in-memory chart storage.

    Args:
        state: The current agent state containing processed_dataframe_json with
               the unified DataFrame data ready for visualization

    Returns:
        Dictionary containing visualization_filepaths key with a list of data URI
        strings representing the generated charts as base64-encoded PNG images

    Raises:
        Exception: If chart generation, data processing, or image encoding fails
    """
    logger = structlog.get_logger()
    logger.info("Starting visualization generation from processed data")

    try:
        # Extract processed DataFrame JSON from state
        processed_data = state.processed_dataframe_json

        logger.info(
            "Preparing data for chart generation",
            data_available=processed_data is not None,
            report_title=state.report_config.get("report_title"),
        )

        # Deserialize JSON string back to Polars DataFrame
        df_data = json.loads(processed_data)
        df = pl.DataFrame(df_data)

        logger.info(
            "Successfully loaded DataFrame for visualization",
            rows=df.height,
            columns=list(df.columns),
        )

        # Create time-series line chart of revenue over date
        fig = go.Figure()

        # Add revenue line
        fig.add_trace(
            go.Scatter(
                x=df["date"].to_list(),
                y=df["shopify_revenue"].to_list(),
                mode="lines+markers",
                name="Shopify Revenue",
                line=dict(color="blue", width=2),
                marker=dict(size=6),
            )
        )

        # Update layout with title and labels
        fig.update_layout(
            title=f"{state.report_config.get('report_title', 'Performance Report')}"
            f" - Revenue Trend",
            xaxis_title="Date",
            yaxis_title="Revenue ($)",
            template="plotly_white",
            showlegend=True,
            width=800,
            height=500,
        )

        logger.info("Successfully created Plotly chart")

        # Export chart to in-memory PNG byte string using Kaleido engine
        png_bytes = fig.to_image(format="png", engine="kaleido")

        logger.info(
            "Successfully exported chart to PNG bytes",
            bytes_size=len(png_bytes),
        )

        # Encode byte string to base64
        encoded_string = base64.b64encode(png_bytes).decode("utf-8")

        # Create data URI string
        data_uri = f"data:image/png;base64,{encoded_string}"

        logger.info(
            "Successfully created data URI",
            uri_length=len(data_uri),
            has_base64_prefix=data_uri.startswith("data:image/png;base64,"),
        )

        # Return list containing the data URI string
        return {"visualization_filepaths": [data_uri]}

    except Exception as e:
        logger.error(
            "Failed to generate visualizations",
            error=str(e),
            data_available=state.processed_dataframe_json is not None,
            report_config=state.report_config,
        )
        raise e

"""Process data node for the e-commerce performance reporting agent."""

from typing import Any, Dict

import polars as pl
import structlog

from agent.models.state import ReportingAgentState


def process_data_node(state: ReportingAgentState) -> Dict[str, Any]:
    """Process and join Shopify and GA4 raw data into a unified DataFrame.

    This node takes the raw data from Shopify orders and GA4 sessions,
    performs data cleaning and type casting, then joins them into a single
    DataFrame that can be used for report generation.

    Args:
        state: The current agent state containing raw_shopify_data and raw_ga4_data

    Returns:
        Dictionary containing processed_dataframe_json key with the serialized
        unified DataFrame as a JSON string

    Raises:
        Exception: If data processing or DataFrame operations fail
    """
    logger = structlog.get_logger()
    logger.info("Starting data processing and joining")

    try:
        # Extract raw data from state
        raw_shopify_data = state.raw_shopify_data
        raw_ga4_data = state.raw_ga4_data

        logger.info(
            "Processing raw data",
            shopify_records=len(raw_shopify_data) if raw_shopify_data else 0,
            ga4_records=len(raw_ga4_data) if raw_ga4_data else 0,
        )

        # Create Shopify DataFrame with data cleaning and type casting
        shopify_df = pl.DataFrame(raw_shopify_data)

        # Clean and transform Shopify data
        shopify_df = shopify_df.with_columns(
            [
                # Extract date from created_at field
                pl.col("created_at").str.slice(0, 10).alias("date"),
                # Convert total_price to float
                pl.col("total_price").cast(pl.Float64).alias("total_price_float"),
            ]
        )

        # Group by date and sum revenue
        shopify_summary = shopify_df.group_by("date").agg(
            [pl.col("total_price_float").sum().alias("shopify_revenue")]
        )

        # Create GA4 DataFrame with data cleaning and type casting
        ga4_df = pl.DataFrame(raw_ga4_data)

        # Clean and transform GA4 data
        ga4_df = ga4_df.with_columns(
            [
                # Ensure date is string format
                pl.col("date").cast(pl.String),
                # Ensure page_views and duration are integers
                pl.col("page_views").cast(pl.Int64),
                pl.col("duration").cast(pl.Int64),
            ]
        )

        # Group by date and aggregate sessions and page views
        ga4_summary = ga4_df.group_by("date").agg(
            [
                pl.len().alias("ga4_sessions"),
                pl.col("page_views").sum().alias("page_views"),
            ]
        )

        # Join the two DataFrames on date
        unified_df = shopify_summary.join(ga4_summary, on="date", how="full")

        # Fill null values with 0 for missing data
        unified_df = unified_df.with_columns(
            [
                pl.col("shopify_revenue").fill_null(0.0),
                pl.col("ga4_sessions").fill_null(0),
                pl.col("page_views").fill_null(0),
            ]
        )

        # Sort by date for consistent ordering
        unified_df = unified_df.sort("date")

        logger.info(
            "Successfully processed and joined data",
            final_records=unified_df.height,
            columns=list(unified_df.columns),
        )

        # Serialize DataFrame to JSON string
        df_json = unified_df.to_pandas().to_json(orient="records")

        return {"processed_dataframe_json": df_json}

    except Exception as e:
        logger.error(
            "Failed to process data",
            error=str(e),
            shopify_data_available=state.raw_shopify_data is not None,
            ga4_data_available=state.raw_ga4_data is not None,
        )
        raise e

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReportingAgentState(BaseModel):
    """
    State model for the e-commerce performance reporting agent.

    This model tracks the complete workflow state from data collection
    through report generation, with optional fields for graph node updates.
    """

    report_config: Dict[str, Any]
    raw_shopify_data: Optional[List[Dict[str, Any]]] = None
    raw_ga4_data: Optional[List[Dict[str, Any]]] = None
    processed_dataframe_json: Optional[str] = None
    generated_insights: Optional[Dict[str, Any]] = None
    visualization_filepaths: List[str] = Field(default_factory=list)
    final_report_path: Optional[str] = None
    error_message: Optional[str] = None
    human_decision: Optional[str] = None

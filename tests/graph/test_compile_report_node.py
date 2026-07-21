"""Tests for compile_report_node function."""

from agent.graph.compile_report_node import compile_report_node
from agent.models.state import ReportingAgentState


def test_compile_report_node_success(mocker):
    # Create sample generated insights dictionary
    sample_insights = {
        "summary": "Revenue peaked on January 15th with $425.50 from 2 sessions and 13 page views.",
        "key_metrics": {
            "total_revenue": 800.99,
            "total_sessions": 4,
            "total_page_views": 24,
            "conversion_rate": 0.167,
        },
        "recommendations": [
            "Focus marketing efforts on high-performing days like January 15th",
            "Investigate why January 25th had revenue but no sessions - possible direct purchases",
        ],
        "data_quality_notes": "All data appears complete with no missing values",
    }

    # Create sample base64 data URI string for visualization
    sample_data_uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

    # Mock the weasyprint import and HTML class
    mock_html = mocker.MagicMock()
    mock_html.write_pdf.return_value = b"mock_pdf_bytes"

    # Mock the weasyprint module during import
    mock_weasyprint = mocker.MagicMock()
    mock_weasyprint.HTML.return_value = mock_html
    mocker.patch.dict("sys.modules", {"weasyprint": mock_weasyprint})

    # Create state with generated insights and visualization filepaths
    state = ReportingAgentState(
        report_config={
            "date_range": "2024-01-01 to 2024-01-31",
            "report_title": "Monthly Analytics Report",
        },
        generated_insights=sample_insights,
        visualization_filepaths=[sample_data_uri],
    )

    # Call the compile_report_node function
    result = compile_report_node(state)

    # Assert that the result contains final_report_path
    assert "final_report_path" in result

    # Assert that final_report_path is a string that looks like a valid PDF file path
    assert isinstance(result["final_report_path"], str)
    assert result["final_report_path"].endswith(".pdf")

    # Assert that the weasyprint HTML().write_pdf() mock was called
    mock_weasyprint.HTML.assert_called_once()
    mock_html.write_pdf.assert_called_once()

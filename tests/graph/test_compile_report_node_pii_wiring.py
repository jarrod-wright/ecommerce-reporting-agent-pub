"""The report path scrubs PII from generated insights before render.

Plan step 2 done-when: a test feeds synthetic PII and asserts it is absent
from the output. The insights payload is the data-derived path into the PDF;
this test captures the rendered HTML handed to WeasyPrint and checks the
synthetic PII never survives.
"""

import re

from agent.graph.compile_report_node import compile_report_node
from agent.models.state import ReportingAgentState


def test_report_render_scrubs_synthetic_pii_from_insights(mocker):
    synthetic_insights = {
        "summary": (
            "Owner Jane Doe (jane.doe@email.com, 555-123-4567) asked why the "
            "January cohort underperformed."
        ),
        "key_metrics": {"total_revenue": 800.99, "conversion_rate": 0.167},
        "recommendations": [
            "Email jane.doe@email.com the retention playbook",
            "Focus marketing spend on high-performing days",
        ],
        "data_quality_notes": "All data appears complete with no missing values",
    }

    mock_html = mocker.MagicMock()
    mock_html.write_pdf.return_value = b"mock_pdf_bytes"
    mock_weasyprint = mocker.MagicMock()
    mock_weasyprint.HTML.return_value = mock_html
    mocker.patch.dict("sys.modules", {"weasyprint": mock_weasyprint})

    state = ReportingAgentState(
        report_config={
            "date_range": "2024-01-01 to 2024-01-31",
            "report_title": "Monthly Analytics Report",
        },
        generated_insights=synthetic_insights,
        visualization_filepaths=[],
    )

    result = compile_report_node(state)
    assert "final_report_path" in result

    rendered = mock_weasyprint.HTML.call_args.kwargs["string"]

    assert "Jane Doe" not in rendered
    assert "jane.doe@email.com" not in rendered
    assert "555-123-4567" not in rendered
    # The scrubber replaces detected entities with type placeholders.
    assert "[PERSON]" in rendered
    assert "[EMAIL_ADDRESS]" in rendered
    # Non-PII analytical text survives the scrub untouched.
    assert "January cohort" in rendered
    # The numeric metrics are never mistaken for PII and never scrubbed away.
    assert "800.99" in rendered or "801" in rendered or "801.00" in rendered
    # No leftover raw e-mail-looking string remains in the render.
    assert not re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", rendered)

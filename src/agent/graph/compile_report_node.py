"""Compile report node for the e-commerce performance reporting agent."""

import tempfile
from typing import Any, Dict

import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape

from agent.models.state import ReportingAgentState

_RATE_HINTS = ("rate", "ratio", "percent", "pct", "share")


def _format_metric_value(value: Any, name: str = "") -> str:
    """Format a key-metric value for display.

    Numbers are rendered with thousands separators; a rate-type metric expressed as
    a 0..1 fraction (e.g. conversion_rate=0.031) is shown as a percentage (3.1%) —
    a faithful representation of the same value, never a fabricated figure. Anything
    non-numeric is passed through as a string.
    """
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        is_rate = any(hint in str(name).lower() for hint in _RATE_HINTS)
        if is_rate and 0 <= value <= 1:
            pct = value * 100
            return f"{int(pct)}%" if float(pct).is_integer() else f"{pct:.1f}%"
        if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
            return f"{int(value):,}"
        return f"{value:,.2f}"
    return str(value)


def compile_report_node(state: ReportingAgentState) -> Dict[str, Any]:
    """Compile final PDF report from generated insights and visualizations using HTML-first pattern.

    This node takes the generated insights and visualization data URIs from the agent state,
    renders them into an HTML template using Jinja2, and then converts the HTML to a PDF
    using WeasyPrint. The PDF is saved to a temporary file and the path is returned.

    Args:
        state: The current agent state containing generated_insights and visualization_filepaths

    Returns:
        Dictionary containing final_report_path key with the path to the generated PDF file

    Raises:
        Exception: If template rendering, PDF generation, or file operations fail
    """
    logger = structlog.get_logger()
    logger.info("Starting final report compilation")

    try:
        # Extract insights and visualizations from state
        generated_insights = state.generated_insights
        visualization_filepaths = state.visualization_filepaths

        logger.info(
            "Preparing data for report compilation",
            has_insights=generated_insights is not None,
            num_visualizations=len(visualization_filepaths)
            if visualization_filepaths
            else 0,
            report_title=state.report_config.get("report_title"),
        )

        # Set up Jinja2 environment to load templates from /app/templates directory
        import os
        # Find project root by looking for pyproject.toml
        current_dir = os.path.dirname(__file__)
        while current_dir != "/":
            if os.path.exists(os.path.join(current_dir, "pyproject.toml")):
                break
            current_dir = os.path.dirname(current_dir)
        template_dir = os.path.join(current_dir, "templates")
        # autoescape: report fields are LLM-produced (untrusted); escape on render.
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )
        env.filters["format_metric"] = _format_metric_value

        # Load the HTML template
        template = env.get_template("report_template.html")

        logger.info("Successfully loaded HTML template")

        # Render the template with insights and visualization data
        rendered_html = template.render(
            insights=generated_insights,
            visualizations=visualization_filepaths,
            report_config=state.report_config,
        )

        logger.info(
            "Successfully rendered HTML template",
            html_length=len(rendered_html),
        )

        # Import WeasyPrint here to allow mocking in tests
        import weasyprint

        # base_url lets the template resolve relative assets (e.g. bundled @font-face
        # fonts under templates/fonts/); trailing separator keeps the templates dir in scope.
        html_doc = weasyprint.HTML(
            string=rendered_html,
            base_url=os.path.join(template_dir, ""),
        )

        logger.info("Successfully created WeasyPrint HTML document")

        # Generate PDF as byte string in memory
        pdf_bytes = html_doc.write_pdf()

        logger.info(
            "Successfully generated PDF",
            pdf_size_bytes=len(pdf_bytes),
        )

        # Save PDF bytes to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(pdf_bytes)
            temp_pdf_path = temp_file.name

        logger.info(
            "Successfully saved PDF to temporary file",
            file_path=temp_pdf_path,
        )

        # Return dictionary with final report path
        return {"final_report_path": temp_pdf_path}

    except Exception as e:
        logger.error(
            "Failed to compile final report",
            error=str(e),
            has_insights=state.generated_insights is not None,
            has_visualizations=bool(state.visualization_filepaths),
            report_config=state.report_config,
        )
        raise e

#!/usr/bin/env python
"""Demo runner for the E-commerce Reporting Agent.

Runs the report-generation pipeline end-to-end on SYNTHETIC e-commerce data,
using free Google Gemini inference, and writes a viewable PDF to
``output/report.pdf``.

It drives the report nodes directly (process_data -> generate_insights ->
generate_visualizations -> compile_report) with synthetic data, so it needs
no Shopify/GA4 credentials. It exercises the *real* insight generation (LLM)
and *real* chart rendering (kaleido) -- this is a genuine run, not a mock.

Usage::

    cp .env.example .env          # then add your GOOGLE_API_KEY to .env
    poetry run python scripts/run_demo.py
"""

import random
import shutil
import sys
from datetime import date, timedelta
from pathlib import Path

# Ensure the src/ packages are importable when run as a script.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from agent.config import settings  # noqa: E402
from agent.graph.compile_report_node import compile_report_node  # noqa: E402
from agent.graph.generate_insights_node import generate_insights_node  # noqa: E402
from agent.graph.generate_visualizations_node import (  # noqa: E402
    generate_visualizations_node,
)
from agent.graph.process_data_node import process_data_node  # noqa: E402
from agent.models.state import ReportingAgentState  # noqa: E402


def build_synthetic_data(seed: int = 1337):
    """Generate ~a month of synthetic Shopify orders and GA4 sessions with an
    upward revenue trend, so the report has a real story to tell."""
    rng = random.Random(seed)
    start = date(2024, 1, 1)
    shopify_orders: list[dict] = []
    ga4_sessions: list[dict] = []

    for offset in range(31):
        day = (start + timedelta(days=offset)).isoformat()

        # Orders per day grow across the month; prices drift upward.
        for _ in range(6 + offset // 3 + rng.randint(0, 4)):
            price = round(rng.uniform(20, 400) * (1 + offset / 60), 2)
            shopify_orders.append(
                {"created_at": f"{day}T12:00:00", "total_price": price}
            )

        # Each GA4 row is one session; sessions also grow over time.
        for _ in range(40 + offset * 2 + rng.randint(0, 20)):
            ga4_sessions.append(
                {
                    "date": day,
                    "page_views": rng.randint(1, 15),
                    "duration": rng.randint(20, 900),
                }
            )

    return shopify_orders, ga4_sessions


def main() -> int:
    if not settings.GOOGLE_API_KEY:
        print(
            "ERROR: GOOGLE_API_KEY is not set.\n"
            "  Copy .env.example to .env and add your free Google AI Studio key,\n"
            "  or run:  export GOOGLE_API_KEY=your-key\n"
        )
        return 1

    print("1/4  Generating synthetic e-commerce data (31 days)...")
    shopify_orders, ga4_sessions = build_synthetic_data()
    print(f"     {len(shopify_orders)} orders, {len(ga4_sessions)} sessions")

    state = ReportingAgentState(
        report_config={
            "report_title": "January 2024 Performance Report (Demo)",
            "date_range": "2024-01-01 to 2024-01-31",
        },
        raw_shopify_data=shopify_orders,
        raw_ga4_data=ga4_sessions,
    )

    try:
        print("2/4  Processing and joining data...")
        state = state.model_copy(update=process_data_node(state))

        print(
            f"3/4  Generating insights via "
            f"{settings.PRIMARY_PROVIDER}/{settings.PRIMARY_LLM_MODEL} "
            f"and rendering chart..."
        )
        state = state.model_copy(update=generate_insights_node(state))
        state = state.model_copy(update=generate_visualizations_node(state))

        print("4/4  Compiling PDF report...")
        state = state.model_copy(update=compile_report_node(state))
    except Exception as exc:  # noqa: BLE001
        print(f"\nRun failed: {type(exc).__name__}: {exc}")
        print(
            "If this is an LLM/auth error, check GOOGLE_API_KEY and the model "
            "IDs in src/agent/config.py. If it's a kaleido/Chrome error, see "
            "the README note on the pinned kaleido 0.2.1."
        )
        return 1

    output_dir = REPO_ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    dest = output_dir / "report.pdf"
    shutil.copyfile(state.final_report_path, dest)

    print(f"\nDone -> {dest}")
    print("Open that PDF to review the generated report.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

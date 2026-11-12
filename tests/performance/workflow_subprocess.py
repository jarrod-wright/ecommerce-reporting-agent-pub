"""Subprocess entry point for the multi-scale memory measurement (BLD-1271).

Measurement method of record: the ERA workflow runs in a dedicated subprocess
that imports only what the workflow needs, then initializes the production PII
scrubber exactly as ``compile_report_node`` does. The budget number is the
subprocess's true peak RSS — suite-independent, and inclusive of the
``en_core_web_md`` model the deployed service carries.

Peak source: ``resource.getrusage(RUSAGE_SELF).ru_maxrss`` where available
(Linux CI, reported in KB); otherwise a psutil sampling thread (Windows dev).
"""

import json
import pickle
import sys
import threading
import time

METRICS_PREFIX = "ERA_SUBPROCESS_METRICS "


def _peak_rss_mb() -> float:
    """True peak RSS in MB for this process (Linux: kernel-reported peak)."""
    import resource

    # Linux: ru_maxrss is peak RSS in KB.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


class _RssSampler:
    """Sampling-thread fallback used when ``resource`` is unavailable."""

    def __init__(self, interval_s: float = 0.01):
        import psutil

        self._proc = psutil.Process()
        self._interval_s = interval_s
        self.peak_mb = self._proc.memory_info().rss / 1024 / 1024
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        while not self._stop.is_set():
            rss = self._proc.memory_info().rss / 1024 / 1024
            if rss > self.peak_mb:
                self.peak_mb = rss
            time.sleep(self._interval_s)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join(timeout=1.0)
        return False


def _run_workflow(dataset_path: str) -> dict:
    """Load the dataset, run the ERA workflow + scrubber init, report peaks."""
    from agent.graph.process_data_node import process_data_node
    from agent.models.state import ReportingAgentState
    from agent.utils.pii_scrubber import scrub_text_for_pii

    with open(dataset_path, "rb") as fh:
        era_dataset = pickle.load(fh)

    sampler_ctx = None
    try:
        import resource  # noqa: F401

        has_resource = True
    except ImportError:
        has_resource = False
    if not has_resource:
        sampler_ctx = _RssSampler()
        sampler_ctx.__enter__()

    baseline_mb = _point_rss_mb()

    era_state = ReportingAgentState(
        report_config={"date_range": "2024-01-01 to 2024-12-31"},
        raw_shopify_data=era_dataset["shopify_orders"].to_dict("records"),
        raw_ga4_data=era_dataset["ga4_sessions"].to_dict("records"),
    )

    workflow_start = time.perf_counter()
    processed = process_data_node(era_state)
    for key, value in processed.items():
        setattr(era_state, key, value)

    # Production scrubber init — the same lazy engine compile_report_node
    # builds on first report. Charges the NLP model to this measurement.
    scrub_text_for_pii("John Doe spent $1,240. Contact john.doe@example.com.")
    era_execution_time = time.perf_counter() - workflow_start

    if sampler_ctx is not None:
        sampler_ctx.__exit__()
        peak_mb = sampler_ctx.peak_mb
    else:
        peak_mb = _peak_rss_mb()

    return {
        "baseline_mb": round(baseline_mb, 1),
        "peak_mb": round(peak_mb, 1),
        "era_execution_time_s": round(era_execution_time, 2),
    }


def _point_rss_mb() -> float:
    import psutil

    return psutil.Process().memory_info().rss / 1024 / 1024


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python -m tests.performance.workflow_subprocess <dataset.pkl>",
              file=sys.stderr)
        return 2
    try:
        metrics = _run_workflow(sys.argv[1])
    except Exception as exc:  # noqa: BLE001 — report failure to the parent verbatim
        print(f"{METRICS_PREFIX}{json.dumps({'error': str(exc)})}")
        return 1
    print(f"{METRICS_PREFIX}{json.dumps(metrics)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

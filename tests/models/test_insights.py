"""Tests for ReportInsights model HTML sanitization and structured coercion."""

from agent.models.insights import ReportInsights


def test_report_insights_sanitizes_html_in_fields():
    """HTML/JS is sanitised in string fields and inside recommendation titles."""
    instance = ReportInsights(
        summary="Test summary <script>alert('XSS')</script>",
        key_metrics={"revenue": 10000, "conversion_rate": 0.025},
        recommendations=[
            "Optimize SEO <script>document.location='http://evil.com'</script>",
            "Improve UX <iframe src='javascript:alert(2)'></iframe> design",
        ],
        data_quality_notes="Quality check <img src=x onerror='alert(1)'> passed",
    )
    assert instance.summary == "Test summary [removed]alert('XSS')[removed]"
    assert instance.data_quality_notes == "Quality check [removed] passed"
    # recommendations are now objects; the bare strings become titles and are sanitised
    assert instance.recommendations[0].title == "Optimize SEO [removed]document.location='http://evil.com'[removed]"
    assert instance.recommendations[1].title == "Improve UX [removed] design"


# --- recommendations structured-coercion suite ---

def _mk_recs(recs):
    return ReportInsights(summary="s", key_metrics={"a": 1}, recommendations=recs, data_quality_notes="d")


def test_recommendations_structured_dicts_pass_through():
    i = _mk_recs([{"title": "Increase spend on peak days", "rationale": "Jan 15 drove 40% of revenue."}])
    assert i.recommendations[0].title == "Increase spend on peak days"
    assert i.recommendations[0].rationale == "Jan 15 drove 40% of revenue."


def test_recommendations_backward_compat_string():
    i = _mk_recs(["Focus on high-performing days"])
    assert i.recommendations[0].title == "Focus on high-performing days"
    assert i.recommendations[0].rationale == ""


def test_recommendations_single_string():
    i = _mk_recs("Do one thing")
    assert len(i.recommendations) == 1
    assert i.recommendations[0].title == "Do one thing"


def test_recommendations_dict_alias_keys():
    i = _mk_recs([{"recommendation": "Cut ad waste", "reason": "ROAS below 1 on Fridays"}])
    assert i.recommendations[0].title == "Cut ad waste"
    assert i.recommendations[0].rationale == "ROAS below 1 on Fridays"


def test_recommendations_unknown_dict_never_crashes():
    i = _mk_recs([{"foo": "bar"}])
    assert i.recommendations[0].title == "foo: bar"
    assert i.recommendations[0].rationale == ""


def test_recommendations_rationale_is_sanitised():
    i = _mk_recs([{"title": "ok", "rationale": "boom <script>alert(1)</script>"}])
    assert i.recommendations[0].rationale == "ok" or "[removed]" in i.recommendations[0].rationale
    assert "<script>" not in i.recommendations[0].rationale


def test_recommendations_none_becomes_empty():
    i = _mk_recs(None)
    assert i.recommendations == []


# --- key_metrics coercion suite (JSON-string bug fix regression guards) ---

_BASE = dict(summary="ok", recommendations=["r"], data_quality_notes="clean")


def _mk(km):
    return ReportInsights(key_metrics=km, **_BASE)


def test_coerce_key_metrics_parses_json_string_object():
    assert _mk('{"total_revenue": 12345.67, "average_order_value": 85.5}').key_metrics == {
        "total_revenue": 12345.67, "average_order_value": 85.5}


def test_coerce_key_metrics_parses_json_string_array():
    assert _mk('["alpha", "beta"]').key_metrics == {"metric_1": "alpha", "metric_2": "beta"}


def test_coerce_key_metrics_preserves_non_json_prose():
    assert _mk("Revenue was strong this quarter").key_metrics == {"details": "Revenue was strong this quarter"}


def test_coerce_key_metrics_dict_passthrough():
    assert _mk({"revenue": 10000, "conversion_rate": 0.025}).key_metrics == {"revenue": 10000, "conversion_rate": 0.025}


def test_coerce_key_metrics_list_enumerates():
    assert _mk(["x", "y"]).key_metrics == {"metric_1": "x", "metric_2": "y"}


def test_coerce_key_metrics_none_becomes_empty():
    assert _mk(None).key_metrics == {}


def test_coerce_key_metrics_json_scalar_string_preserved():
    assert _mk("42").key_metrics == {"details": "42"}


def test_sanitiser_preserves_words_starting_with_on():
    """BLUE regression: legitimate prose words (online, only, ongoing) must not be stripped."""
    i = ReportInsights(
        summary="Online sales grew while ongoing costs fell; only Fridays lagged.",
        key_metrics={"a": 1},
        recommendations=["Grow online only on peak days"],
        data_quality_notes="one anomaly noted",
    )
    assert i.summary == "Online sales grew while ongoing costs fell; only Fridays lagged."
    assert i.recommendations[0].title == "Grow online only on peak days"
    assert i.data_quality_notes == "one anomaly noted"


def test_sanitiser_still_neutralises_event_handler_attribute():
    """A real inline event handler on a non-listed tag is still neutralised (bleach backstop)."""
    i = ReportInsights(
        summary='hi <div onclick="steal()">x</div>',
        key_metrics={"a": 1},
        recommendations=["r"],
        data_quality_notes="d",
    )
    assert "onclick" not in i.summary
    assert "<div" not in i.summary

from datetime import datetime, timedelta

import pandas as pd

from report_automation.alerts import evaluate_alerts
from report_automation.reporting import build_daily_summary, event_breakdown


def _flights_frame(delays: list[float | None]) -> pd.DataFrame:
    base = datetime(2026, 9, 7, 8, 0, 0)
    rows = []
    for i, delay in enumerate(delays):
        sched = base + timedelta(hours=i)
        actual = sched + timedelta(minutes=delay) if delay else sched
        rows.append({"flight_id": i + 1, "flight_date": pd.Timestamp(sched.date()),
                     "scheduled_dep": sched, "actual_dep": actual})
    return pd.DataFrame(rows)


def test_delay_rate_flags_flights_over_15_minutes():
    flights = _flights_frame([0, 10, 20, 30])  # 2 of 4 delayed
    passengers = pd.DataFrame({"date": [pd.Timestamp("2026-09-07")], "passengers": [9000]})
    summary = build_daily_summary(flights, passengers)
    assert summary.loc[0, "delayed_flights"] == 2
    assert summary.loc[0, "delay_rate"] == 0.5


def test_build_daily_summary_merges_passengers():
    flights = _flights_frame([0, 0])
    passengers = pd.DataFrame({"date": [pd.Timestamp("2026-09-07")], "passengers": [9000]})
    summary = build_daily_summary(flights, passengers)
    assert list(summary.columns) == ["date", "flights", "delayed_flights",
                                     "avg_delay_min", "delay_rate", "passengers"]
    assert summary.loc[0, "passengers"] == 9000


def test_alert_rules_trigger_on_threshold_breach():
    summary = pd.DataFrame({
        "date": pd.to_datetime(["2026-09-07", "2026-09-08"]),
        "delay_rate": [0.10, 0.30],        # day 2 breaches
        "passengers": [5000, 9000],        # day 1 breaches
    })
    alerts = evaluate_alerts(summary, delay_rate_threshold=0.20,
                             min_passengers_expected=8000)
    rules = {(a.date.isoformat(), a.rule) for a in alerts}
    assert ("2026-09-07", "low_volume") in rules
    assert ("2026-09-08", "delay_rate") in rules
    assert len(alerts) == 2


def test_no_alerts_when_within_thresholds():
    summary = pd.DataFrame({
        "date": pd.to_datetime(["2026-09-07"]),
        "delay_rate": [0.05], "passengers": [9000],
    })
    assert evaluate_alerts(summary, delay_rate_threshold=0.20,
                           min_passengers_expected=8000) == []


def test_event_breakdown_counts_types():
    events = pd.DataFrame({
        "event_time": pd.to_datetime(["2026-09-07 08:00", "2026-09-07 09:00",
                                      "2026-09-08 08:00"]),
        "event_type": ["gate_change", "gate_change", "crew_delay"],
    })
    out = event_breakdown(events)
    assert out.set_index("date").loc[pd.Timestamp("2026-09-07"), "gate_change"] == 2
    assert out.set_index("date").loc[pd.Timestamp("2026-09-08"), "crew_delay"] == 1

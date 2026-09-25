"""Create the sample data sources in ./data so the tool runs out of the box.

In production these are the live ops DB, the ops API, and the existing
manual workbook — this generator simulates two weeks of operations.

Usage:
    python sample_data/generate_sample_data.py [--dest DIR]
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)
DEFAULT_DEST = Path(__file__).resolve().parent.parent / "data"


def generate(dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)

    # --- 1. SQL source: flights table in SQLite ---
    db = dest_dir / "flights.db"
    if db.exists():
        db.unlink()
    conn = sqlite3.connect(db)
    rows = []
    fid = 1000
    start = datetime(2026, 9, 7)  # Monday
    airlines = ["GreenAir", "NimbusJet", "Sahel Airways"]
    routes = [("LOS", "ABV"), ("LOS", "KAN"), ("LOS", "PHC"), ("ABV", "LOS")]
    for day in range(14):
        date = (start + timedelta(days=day)).date()
        for _ in range(random.randint(22, 30)):
            fid += 1
            orig, dest = random.choice(routes)
            sched = datetime.combine(date, datetime.min.time()) + timedelta(
                hours=random.randint(6, 20),
                minutes=random.choice([0, 15, 30, 45]),
            )
            delayed = random.random() < (0.28 if day in (5, 6) else 0.12)
            actual = sched + timedelta(minutes=random.randint(20, 95)) if delayed else sched
            rows.append((fid, str(date), random.choice(airlines), f"{orig}-{dest}",
                         sched.isoformat(), actual.isoformat(),
                         "DEPARTED" if not delayed else "DELAYED"))
    pd.DataFrame(rows, columns=[
        "flight_id", "flight_date", "airline", "route",
        "scheduled_dep", "actual_dep", "status"]).to_sql("flights", conn, index=False)
    conn.close()

    # --- 2. API source: ground-operations events (snapshot of REST payload) ---
    events = []
    for day in range(14):
        base = datetime.combine(start + timedelta(days=day), datetime.min.time())
        for _ in range(random.randint(12, 25)):
            events.append({
                "event_time": (base + timedelta(
                    hours=random.randint(5, 22),
                    minutes=random.randrange(60))).isoformat(),
                "event_type": random.choice(["baggage_delay", "gate_change",
                                             "fuel_truck_wait", "security_alert",
                                             "crew_delay", "equipment_ok"]),
            })
    (dest_dir / "ops_api_snapshot.json").write_text(
        json.dumps({"events": events}, indent=1), encoding="utf-8")

    # --- 3. Excel source: manually-maintained passenger workbook ---
    pax = [{
        "date": str(start + timedelta(days=day)),
        "passengers": max(3000, int(random.gauss(9800 if day not in (5, 6) else 7200, 900))),
        "cargo_tonnes": round(random.uniform(40, 120), 1),
    } for day in range(14)]
    with pd.ExcelWriter(dest_dir / "passenger_stats.xlsx", engine="openpyxl") as xw:
        pd.DataFrame(pax).to_excel(xw, sheet_name="daily_passengers", index=False)

    print("Sample data written to", dest_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST,
                        help="Output directory for the data files")
    args = parser.parse_args()
    generate(args.dest)


if __name__ == "__main__":
    main()

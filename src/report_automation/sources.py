"""Data access layer: one loader per source, each validating its input
and raising DataSourceError with actionable context on failure."""
from __future__ import annotations

import json
import logging
import sqlite3
import time
from pathlib import Path

import pandas as pd

from .exceptions import DataSourceError
from .settings import Settings

_FLIGHTS_QUERY = """
SELECT flight_id, flight_date, airline, route,
       scheduled_dep, actual_dep, status
FROM flights
"""


def load_sql_flights(db_path: Path) -> pd.DataFrame:
    """Flight schedule and status from the operations database."""
    if not db_path.exists():
        raise DataSourceError(f"Ops database not found: {db_path}")
    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(
                _FLIGHTS_QUERY, conn,
                parse_dates=["flight_date", "scheduled_dep", "actual_dep"],
            )
    except sqlite3.Error as exc:
        raise DataSourceError(f"Failed to read flights from {db_path}: {exc}") from exc
    if df.empty:
        raise DataSourceError(f"Flights table is empty: {db_path}")
    return df


def fetch_api_events(settings: Settings, logger: logging.Logger) -> pd.DataFrame:
    """Ground-operations events.

    Uses the live API when ``OPS_API_URL`` is configured, with bounded
    retries and exponential backoff; otherwise reads the on-disk
    snapshot (offline / air-gapped mode).
    """
    if settings.api_url:
        try:
            import requests  # lazy: only needed for API mode
        except ImportError as exc:  # pragma: no cover
            raise DataSourceError(
                "API mode requires the 'requests' package (pip install requests)"
            ) from exc

        for attempt in range(1, settings.api_retries + 1):
            try:
                response = requests.get(settings.api_url, timeout=settings.api_timeout_seconds)
                response.raise_for_status()
                payload = response.json()
                df = _events_frame(payload, source=settings.api_url)
                logger.info("Loaded %d events from API", len(df))
                return df
            except requests.RequestException as exc:
                logger.warning("API attempt %d/%d failed: %s", attempt, settings.api_retries, exc)
                if attempt < settings.api_retries:
                    time.sleep(2 ** (attempt - 1))
        logger.warning("API unreachable; falling back to snapshot %s", settings.api_snapshot)

    return _load_snapshot(settings.api_snapshot)


def _load_snapshot(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise DataSourceError(
            f"API snapshot not found: {path}. Configure OPS_API_URL or generate sample data."
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _events_frame(payload, source=str(path))


def _events_frame(payload: dict, source: str) -> pd.DataFrame:
    events = payload.get("events")
    if not events:
        raise DataSourceError(f"No events found in {source}")
    df = pd.DataFrame(events)
    df["event_time"] = pd.to_datetime(df["event_time"])
    return df


def load_excel_passengers(path: Path) -> pd.DataFrame:
    """Passenger volumes from the manually-maintained workbook."""
    if not path.exists():
        raise DataSourceError(f"Passenger workbook not found: {path}")
    df = pd.read_excel(path, sheet_name="daily_passengers", engine="openpyxl")
    missing = {"date", "passengers"} - set(df.columns)
    if missing:
        raise DataSourceError(f"Passenger workbook {path} missing columns: {sorted(missing)}")
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_all(settings: Settings, logger: logging.Logger) -> dict[str, pd.DataFrame]:
    """Load and validate every source. Raises DataSourceError on any failure."""
    sources = {
        "flights": load_sql_flights(settings.sqlite_db),
        "events": fetch_api_events(settings, logger),
        "passengers": load_excel_passengers(settings.excel_source),
    }
    logger.info(
        "Sources loaded: %s",
        ", ".join(f"{name}={len(frame)} rows" for name, frame in sources.items()),
    )
    return sources

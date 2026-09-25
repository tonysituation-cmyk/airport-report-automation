"""Application settings.

Every value can be overridden with an environment variable (see
``.env.example``). A local ``.env`` file is loaded when present.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:  # optional dependency — .env support degrades gracefully
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*args: object, **kwargs: object) -> bool:
        return False

PACKAGE_ROOT = Path(__file__).resolve().parent      # <repo>/src/report_automation
PROJECT_ROOT = PACKAGE_ROOT.parent.parent           # <repo>


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for one report cycle."""

    data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data")
    reports_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "reports")
    logs_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "logs")

    sqlite_db: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "flights.db")
    excel_source: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "passenger_stats.xlsx")
    api_snapshot: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "ops_api_snapshot.json")

    api_url: str | None = None            # live ops API; unset = snapshot mode
    api_timeout_seconds: float = 10.0
    api_retries: int = 3

    delay_rate_threshold: float = 0.20    # flag days above this delay share
    min_passengers_expected: int = 8000   # flag days below this volume

    smtp_host: str | None = None
    smtp_port: int = 465
    smtp_user: str | None = None
    smtp_password: str | None = None
    alert_email_to: str | None = None     # on-call address for alerts

    log_level: str = "INFO"
    output_file: Path | None = None

    def __post_init__(self) -> None:
        if self.output_file is None:
            object.__setattr__(self, "output_file", self.reports_dir / "weekly_operations_report.xlsx")


def _env_path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    return Path(value).expanduser() if value else default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value else default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


def _env_str(name: str, default: str | None = None) -> str | None:
    return os.getenv(name) or default


def load_settings(env_file: Path | None = None) -> Settings:
    """Build Settings from the environment, optionally loading a .env file."""
    env_file = env_file or (PROJECT_ROOT / ".env")
    if env_file.exists():
        load_dotenv(env_file)
    return Settings(
        data_dir=_env_path("OPS_DATA_DIR", PROJECT_ROOT / "data"),
        reports_dir=_env_path("OPS_REPORTS_DIR", PROJECT_ROOT / "reports"),
        logs_dir=_env_path("OPS_LOGS_DIR", PROJECT_ROOT / "logs"),
        sqlite_db=_env_path("OPS_SQLITE_DB", PROJECT_ROOT / "data" / "flights.db"),
        excel_source=_env_path("OPS_EXCEL_SOURCE", PROJECT_ROOT / "data" / "passenger_stats.xlsx"),
        api_snapshot=_env_path("OPS_API_SNAPSHOT", PROJECT_ROOT / "data" / "ops_api_snapshot.json"),
        api_url=_env_str("OPS_API_URL"),
        api_timeout_seconds=_env_float("OPS_API_TIMEOUT", 10.0),
        api_retries=_env_int("OPS_API_RETRIES", 3),
        delay_rate_threshold=_env_float("OPS_DELAY_RATE_THRESHOLD", 0.20),
        min_passengers_expected=_env_int("OPS_MIN_PASSENGERS", 8000),
        smtp_host=_env_str("OPS_SMTP_HOST"),
        smtp_port=_env_int("OPS_SMTP_PORT", 465),
        smtp_user=_env_str("OPS_SMTP_USER"),
        smtp_password=_env_str("OPS_SMTP_PASSWORD"),
        alert_email_to=_env_str("OPS_ALERT_EMAIL"),
        log_level=_env_str("OPS_LOG_LEVEL", "INFO") or "INFO",
    )

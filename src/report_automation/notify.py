"""Alert delivery: alerts.log always; email when SMTP is configured.

The email stub mirrors production behaviour — if OPS_SMTP_HOST is unset,
alerts are logged with the would-be email body instead of being sent.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from email.message import EmailMessage

from .alerts import Alert
from .exceptions import NotificationError
from .settings import Settings

ALERTS_LOG = "alerts.log"


def notify_alerts(
    logger: logging.Logger, alerts: list[Alert], settings: Settings
) -> None:
    """Deliver alerts: append to alerts.log, then email if configured."""
    if not alerts:
        return

    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    alerts_path = settings.logs_dir / ALERTS_LOG
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(alerts_path, "a", encoding="utf-8") as fh:
        for alert in alerts:
            fh.write(f"{stamp} | {alert.date} | {alert.rule} | {alert.message}" + chr(10))

    for alert in alerts:
        logger.warning("ALERT [%s] %s", alert.rule, alert.message)

    if settings.alert_email_to and settings.smtp_host:
        _send_email(logger, settings, alerts)
    else:
        logger.info(
            "Alert email not configured — %d alert(s) written to %s",
            len(alerts), alerts_path,
        )


def notify_failure(logger: logging.Logger, settings: Settings, error: BaseException) -> None:
    """Best-effort notification that the whole run failed."""
    message = f"Report automation run FAILED: {error!r}"
    logger.critical(message)
    try:
        fake = [Alert(date=datetime.now(timezone.utc).date(), rule="pipeline", message=message)]
        notify_alerts(logger, fake, settings)
    except NotificationError as exc:  # never mask the original error
        logger.error("Failed to deliver failure alert: %s", exc)


def _send_email(logger: logging.Logger, settings: Settings, alerts: list[Alert]) -> None:
    body = chr(10).join(a.message for a in alerts)
    message = EmailMessage()
    message["Subject"] = f"Operations report alerts ({len(alerts)})"
    message["From"] = settings.smtp_user or "ops-report@localhost"
    message["To"] = settings.alert_email_to or ""
    message.set_content(body)

    import smtplib
    try:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password or "")
            smtp.send_message(message)
        logger.info("Alert email sent to %s", settings.alert_email_to)
    except OSError as exc:
        raise NotificationError(f"SMTP delivery failed: {exc}") from exc

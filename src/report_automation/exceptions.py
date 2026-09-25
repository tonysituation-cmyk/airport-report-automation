"""Exception hierarchy for the reporting pipeline."""
from __future__ import annotations


class ReportAutomationError(Exception):
    """Base error for all pipeline failures."""


class DataSourceError(ReportAutomationError):
    """A data source is missing, unreadable, or failed validation."""


class NotificationError(ReportAutomationError):
    """An alert could not be delivered."""

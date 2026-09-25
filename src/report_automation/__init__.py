"""Weekly operations report automation.

Pulls from three operational data sources (SQL, API, Excel), aggregates
with Pandas, evaluates alerting thresholds, and renders a formatted,
charted Excel workbook with openpyxl.
"""
from __future__ import annotations

__version__ = "1.1.0"
__author__ = "Anthony Effedua"

from .pipeline import run  # noqa: F401  (convenience re-export)

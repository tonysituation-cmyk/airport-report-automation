# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-09-25

### Added
- Environment-based configuration (`.env` support) with typed `Settings`
- Structured `Alert` objects shared by workbook, log, and email outputs
- Retry with exponential backoff for the API source
- SMTP alert delivery (SSL) with graceful stub when unconfigured
- Container-friendly logging (`WatchedFileHandler`)
- `pyproject.toml` with console script (`ops-report`), ruff/mypy/pytest config
- pytest suite, Makefile, Dockerfile, GitHub Actions CI
- MIT license, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, issue/PR templates

### Changed
- Flat package layout -> `src/` layout
- Custom exception hierarchy (`ReportAutomationError`, `DataSourceError`, `NotificationError`)
- Date columns in reports render as `yyyy-mm-dd` with correct column widths

## [1.0.0] - 2026-09-25

- Initial release: multi-source ingestion (SQL/API/Excel), Pandas aggregation,
  threshold alerting, openpyxl report with charts, rotating logs

# Contributing

Thanks for your interest in improving this project!

## Getting started

1. Fork the repository and clone your fork
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
3. Install dev dependencies: `pip install -e .[dev]`
4. Generate sample data: `make sample-data`
5. Verify everything works: `make check`

## Workflow

- Branch from `main`: `git checkout -b feature/short-description`
- Keep changes focused; one feature or fix per pull request
- `make check` (ruff + mypy + pytest) must pass before opening a PR
- Write tests for new behaviour; keep type annotations complete

## Pull requests

- Fill in the PR template, including what/why and how you tested it
- Link related issues with `Closes #123`

## Reporting issues

Use the bug report or feature request templates. Include the output of
`ops-report --log-level DEBUG` for bugs.

By participating, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

# Security Policy

## Reporting a vulnerability

Please do **not** open a public issue for security vulnerabilities.
Instead, report them privately to the maintainer (see the email in the
README or git history).

Include: a description of the issue, steps to reproduce, affected versions,
and any suggested mitigation. You should receive an acknowledgement within
72 hours.

## Scope notes

- The bundled SMTP integration sends alert emails only; store SMTP
  credentials in environment variables or a secrets manager, never in code
  or committed `.env` files
- Sample data is synthetic; never commit real operational data to this
  repository
- Supported versions: the latest release only

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY sample_data ./sample_data
RUN python sample_data/generate_sample_data.py

# Default: run one report cycle against the bundled sample data.
CMD ["python", "-m", "report_automation"]

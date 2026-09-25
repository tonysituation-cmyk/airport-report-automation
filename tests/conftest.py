import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from report_automation.settings import Settings  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = REPO_ROOT / "sample_data" / "generate_sample_data.py"


@pytest.fixture()
def sandbox(tmp_path: Path) -> Settings:
    """A full isolated environment: sample data + settings pointed at tmp dirs."""
    data_dir = tmp_path / "data"
    subprocess.run([sys.executable, str(GENERATOR), "--dest", str(data_dir)],
                   check=True, capture_output=True)
    return Settings(
        data_dir=data_dir,
        reports_dir=tmp_path / "reports",
        logs_dir=tmp_path / "logs",
        sqlite_db=data_dir / "flights.db",
        excel_source=data_dir / "passenger_stats.xlsx",
        api_snapshot=data_dir / "ops_api_snapshot.json",
        api_url=None,  # offline/snapshot mode
        output_file=tmp_path / "reports" / "test_report.xlsx",
    )

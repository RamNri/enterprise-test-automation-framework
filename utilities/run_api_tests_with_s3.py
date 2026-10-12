
import logging
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from utilities.s3_report_uploader import upload_allure_results

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "artifacts" / "allure-results"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> int:
    bucket_name = os.getenv("S3_REPORTS_BUCKET")

    if not bucket_name:
        logger.error("S3_REPORTS_BUCKET environment variable is required.")
        return 1

    # Remove stale results so this run publishes only its own artifacts.
    if RESULTS_DIR.exists():
        shutil.rmtree(RESULTS_DIR)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + uuid.uuid4().hex[:8]
    )
    s3_prefix = f"allure-results/{run_id}"

    logger.info("Starting API test execution. Run ID: %s", run_id)

    test_command = [
        sys.executable,
        "-m",
        "pytest",
        "tests/api",
        "-q",
        f"--alluredir={RESULTS_DIR}",
    ]

    test_result = subprocess.run(test_command, cwd=PROJECT_ROOT)
    test_exit_code = test_result.returncode

    logger.info("Pytest finished with exit code %s.", test_exit_code)

    try:
        uploaded_count = upload_allure_results(
            results_dir=RESULTS_DIR,
            bucket_name=bucket_name,
            s3_prefix=s3_prefix,
        )
        logger.info(
            "Uploaded %s files to s3://%s/%s/",
            uploaded_count,
            bucket_name,
            s3_prefix,
        )
    except Exception:
        logger.exception("Could not publish the Allure results to S3.")
        # A failed upload must not be reported as a successful pipeline.
        return test_exit_code if test_exit_code != 0 else 1

    return test_exit_code


if __name__ == "__main__":
    sys.exit(main())

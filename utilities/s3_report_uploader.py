
import logging
import os
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

DEFAULT_RESULTS_DIR = Path("artifacts/allure-results")
DEFAULT_S3_PREFIX = "allure-results"


def upload_allure_results(
    results_dir: Path = DEFAULT_RESULTS_DIR,
    bucket_name: str | None = None,
    s3_prefix: str = DEFAULT_S3_PREFIX,
) -> int:
    """Upload Allure result files to S3 and return the file count."""

    bucket_name = bucket_name or os.getenv("S3_REPORTS_BUCKET")

    if not bucket_name:
        raise ValueError("S3_REPORTS_BUCKET environment variable is required.")

    results_dir = Path(results_dir)

    if not results_dir.is_dir():
        raise FileNotFoundError(
            f"Allure results directory does not exist: {results_dir}"
        )

    files = [path for path in results_dir.rglob("*") if path.is_file()]

    if not files:
        raise ValueError(f"No Allure result files found in {results_dir}")

    uploaded_count = 0

    try:
        s3_client = boto3.client("s3")

        for file_path in files:
            relative_path = file_path.relative_to(results_dir).as_posix()
            s3_key = f"{s3_prefix.rstrip('/')}/{relative_path}"

            logger.info(
                "Uploading %s to s3://%s/%s",
                file_path,
                bucket_name,
                s3_key,
            )

            s3_client.upload_file(
                str(file_path),
                bucket_name,
                s3_key,
            )
            uploaded_count += 1

    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to upload Allure results to S3.")
        raise RuntimeError("Allure result upload failed.") from exc

    logger.info("Successfully uploaded %d Allure result files.", uploaded_count)
    return uploaded_count

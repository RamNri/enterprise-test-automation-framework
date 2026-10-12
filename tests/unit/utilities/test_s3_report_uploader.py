
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from utilities.s3_report_uploader import upload_allure_results


BUCKET_NAME = "enterprise-test-reports-788208946296-us-east-1"


def test_upload_allure_results_uploads_files_with_correct_s3_keys(tmp_path):
    results_dir = tmp_path / "allure-results"
    results_dir.mkdir()

    (results_dir / "result.json").write_text('{"uuid": "test-123"}')
    (results_dir / "environment.properties").write_text("environment=local")

    with patch("utilities.s3_report_uploader.boto3.client") as mock_client:
        s3_client = MagicMock()
        mock_client.return_value = s3_client

        uploaded_count = upload_allure_results(
            results_dir=results_dir,
            bucket_name=BUCKET_NAME,
            s3_prefix="allure-results/test-run-123",
        )

    assert uploaded_count == 2
    assert mock_client.call_args.args == ("s3",)

    assert s3_client.upload_file.call_count == 2
    s3_client.upload_file.assert_any_call(
        str(results_dir / "result.json"),
        BUCKET_NAME,
        "allure-results/test-run-123/result.json",
    )
    s3_client.upload_file.assert_any_call(
        str(results_dir / "environment.properties"),
        BUCKET_NAME,
        "allure-results/test-run-123/environment.properties",
    )


def test_upload_allure_results_rejects_empty_directory(tmp_path):
    results_dir = tmp_path / "allure-results"
    results_dir.mkdir()

    with pytest.raises(ValueError, match="No Allure result files found"):
        upload_allure_results(
            results_dir=results_dir,
            bucket_name=BUCKET_NAME,
        )


def test_upload_allure_results_reports_s3_upload_failure(tmp_path):
    results_dir = tmp_path / "allure-results"
    results_dir.mkdir()
    result_file = results_dir / "result.json"
    result_file.write_text('{"uuid": "test-123"}')

    client_error = ClientError(
        {
            "Error": {
                "Code": "AccessDenied",
                "Message": "Access denied",
            }
        },
        "PutObject",
    )

    with patch("utilities.s3_report_uploader.boto3.client") as mock_client:
        s3_client = MagicMock()
        s3_client.upload_file.side_effect = client_error
        mock_client.return_value = s3_client

        with pytest.raises(RuntimeError, match="Allure result upload failed"):
            upload_allure_results(
                results_dir=results_dir,
                bucket_name=BUCKET_NAME,
            )

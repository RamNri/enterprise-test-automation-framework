import sys
from unittest.mock import Mock, patch
import importlib.util
from pathlib import Path
import pytest


ROOT_DIR = Path(__file__).resolve().parents[3]
CONFTEST_PATH = ROOT_DIR / "conftest.py"

spec = importlib.util.spec_from_file_location(
    "framework_conftest",
    CONFTEST_PATH,
)

conftest = importlib.util.module_from_spec(spec)
sys.modules["framework_conftest"] = conftest
spec.loader.exec_module(conftest)


class TestPytestConfiguration:

    @patch("framework_conftest.FrameworkConfigurator.configure")
    def test_pytest_configure_passes_cli_options_to_framework_configurator(
        self,
        configure,
    ):
        config = Mock()

        config.getoption.side_effect = {
            "--env": "qa",
            "--browser": "firefox",
            "--headless": True,
            "--execution-mode": "local",
        }.get

        conftest.pytest_configure(config)

        configure.assert_called_once_with(
          environment="qa",
          browser="firefox",
          headless=True,
          execution_mode="local",
        )
    
    def test_pytest_addoption_registers_framework_cli_options(self):

        parser = Mock()

        conftest.pytest_addoption(parser)

        assert parser.addoption.call_count == 4

        parser.addoption.assert_any_call(
            "--browser",
            action="store",
            default="chrome",
            help="Browser to run tests on",
        )

        parser.addoption.assert_any_call(
            "--headless",
            action="store_true",
            default=False,
            help="Run browser in headless mode",
        )

        parser.addoption.assert_any_call(
            "--env",
            action="store",
            default="local",
            help="Environmnet to run the tests against",
        ) 

        parser.addoption.assert_any_call(
          "--execution-mode",
            action="store",
            default="local",
            choices=["local", "grid", "browserstack"],
            help="Execution mode: local, grid, or browserstack",
        )

    @patch("framework_conftest.ExecutionContext.start_test")
    @patch("framework_conftest.ExecutionContext.set_worker_id")
    def test_pytest_runtest_setup_initializes_execution_context(
        self,
        set_worker_id,
        start_test,
    ):
        item = Mock()

        item.config.workerinput = {}

        item.nodeid = (
            "tests/unit/config/test_example.py::"
            "TestExample::test_something"
        )

        conftest.pytest_runtest_setup(item)

        set_worker_id.assert_called_once_with("master")

        start_test.assert_called_once_with(
            item.nodeid
        )

    @patch("framework_conftest.ExecutionContext.start_test")
    @patch("framework_conftest.ExecutionContext.set_worker_id")
    def test_pytest_runtest_setup_uses_xdist_worker_id(
        self,
        set_worker_id,
        start_test,
    ):
        item = Mock()

        item.config.workerinput = {
            "workerid": "gw0"
        }

        item.nodeid = (
            "tests/unit/config/test_example.py::"
            "TestExample::test_something"
        )

        conftest.pytest_runtest_setup(item)

        set_worker_id.assert_called_once_with("gw0")

        start_test.assert_called_once_with(
            item.nodeid
        )

    @patch("framework_conftest.DriverFactory.quit")
    @patch("framework_conftest.DriverFactory.create")
    def test_driver_fixture_creates_and_quits_driver(
        self,
        create,
        quit_driver,
    ):
        fake_driver = Mock()
        create.return_value = fake_driver

        fixture = conftest.driver.__wrapped__()

        returned_driver = next(fixture)

        assert returned_driver is fake_driver

        create.assert_called_once_with()

        with pytest.raises(StopIteration):
            next(fixture)

        quit_driver.assert_called_once_with()

    @patch("framework_conftest.ExecutionContext.session_id")
    @patch("framework_conftest.ExecutionContext.browser")
    @patch("framework_conftest.ExecutionContext.seed")
    @patch("framework_conftest.ExecutionContext.test_name")
    @patch("framework_conftest.ExecutionContext.thread_id")
    @patch("framework_conftest.ExecutionContext.worker_id")
    @patch("framework_conftest.ExecutionContext.execution_id")
    def test_pytest_runtest_makereport_attaches_execution_metadata(
        self,
        execution_id,
        worker_id,
        thread_id,
        test_name,
        seed,
        browser,
        session_id,
    ):
        execution_id.return_value = "exec-123"
        worker_id.return_value = "gw0"
        thread_id.return_value = 12345
        test_name.return_value = "test_login"
        seed.return_value = 98765
        browser.return_value = "chrome"
        session_id.return_value = "session-abc"

        item = Mock()

        call = Mock()
        call.when = "call"

        report = Mock()

        outcome = Mock()
        outcome.get_result.return_value = report

        hook = conftest.pytest_runtest_makereport(
            item,
            call,
        )

        next(hook)

        try:
            hook.send(outcome)
        except StopIteration:
            pass

        assert report.execution_id == "exec-123"
        assert report.worker_id == "gw0"
        assert report.thread_id == 12345
        assert report.test_name == "test_login"
        assert report.seed == 98765
        assert report.browser == "chrome"
        assert report.session_id == "session-abc"

    @patch("framework_conftest.FailureArtifactManager.attach_screenshot")
    @patch("framework_conftest.FailureArtifactManager.capture_screenshot")
    @patch("framework_conftest.ExecutionContext.duration")
    def test_pytest_runtest_makereport_does_not_capture_screenshot_for_passed_test(
        self,
        duration,
        capture_screenshot,
        attach_screenshot,
    ):
        duration.return_value = 1.25

        item = Mock()
        call = Mock()

        report = Mock()
        report.when = "call"
        report.passed = True
        report.failed = False

        outcome = Mock()
        outcome.get_result.return_value = report

        hook = conftest.pytest_runtest_makereport(item, call)

        next(hook)

        try:
            hook.send(outcome)
        except StopIteration:
            pass

        capture_screenshot.assert_not_called()
        attach_screenshot.assert_not_called()

    @patch("framework_conftest.FailureArtifactManager.attach_screenshot")
    @patch("framework_conftest.FailureArtifactManager.capture_screenshot")
    @patch("framework_conftest.logger.error")
    @patch("framework_conftest.FailureSanitizer.sanitize")
    @patch("framework_conftest.ExecutionContext.duration")
    def test_pytest_runtest_makereport_sanitizes_failure_before_logging(
        self,
        duration,
        sanitize,
        logger_error,
        capture_screenshot,
        attach_screenshot,
    ):
        duration.return_value = 1.25

        item = Mock()
        call = Mock()

        report = Mock()
        report.when = "call"
        report.passed = False
        report.failed = True
        report.longrepr = "password=secret123"

        sanitize.return_value = "password=***"

        outcome = Mock()
        outcome.get_result.return_value = report

        hook = conftest.pytest_runtest_makereport(item, call)

        next(hook)

        try:
            hook.send(outcome)
        except StopIteration:
            pass

        sanitize.assert_called_once_with("password=secret123")

        logger_error.assert_called_once_with(
            "TEST FAILED | message=%s",
            "password=***",
        )

    @patch("framework_conftest.FailureArtifactManager.attach_screenshot")
    @patch("framework_conftest.FailureArtifactManager.capture_screenshot")
    @patch("framework_conftest.FailureSanitizer.sanitize")
    @patch("framework_conftest.ExecutionContext.duration")
    def test_pytest_runtest_makereport_captures_screenshot_on_failure(
        self,
        duration,
        sanitize,
        capture_screenshot,
        attach_screenshot,
    ):
        duration.return_value = 1.25
        sanitize.return_value = "sanitized failure"

        fake_driver = Mock()

        item = Mock()
        item.name = "test_login"

        item.funcargs = {
            "driver": fake_driver
        }

        call = Mock()

        report = Mock()
        report.when = "call"
        report.passed = False
        report.failed = True
        report.longrepr = "original failure"

        outcome = Mock()
        outcome.get_result.return_value = report

        fake_filepath = Mock()
        capture_screenshot.return_value = fake_filepath

        hook = conftest.pytest_runtest_makereport(item, call)

        next(hook)

        try:
            hook.send(outcome)
        except StopIteration:
            pass

        capture_screenshot.assert_called_once_with(
            fake_driver,
            "test_login",
        )

    @patch("framework_conftest.FailureArtifactManager.attach_screenshot")
    @patch("framework_conftest.FailureArtifactManager.capture_screenshot")
    @patch("framework_conftest.FailureSanitizer.sanitize")
    @patch("framework_conftest.ExecutionContext.duration")
    def test_pytest_runtest_makereport_attaches_captured_screenshot_to_report(
        self,
        duration,
        sanitize,
        capture_screenshot,
        attach_screenshot,
    ):
        duration.return_value = 1.25
        sanitize.return_value = "sanitized failure"

        fake_driver = Mock()
        fake_filepath = Mock()

        item = Mock()
        item.name = "test_login"
        item.funcargs = {
            "driver": fake_driver
        }

        call = Mock()

        report = Mock()
        report.when = "call"
        report.passed = False
        report.failed = True
        report.longrepr = "original failure"

        outcome = Mock()
        outcome.get_result.return_value = report

        capture_screenshot.return_value = fake_filepath

        hook = conftest.pytest_runtest_makereport(item, call)

        next(hook)

        try:
            hook.send(outcome)
        except StopIteration:
            pass

        attach_screenshot.assert_called_once_with(
            report,
            fake_filepath,
        )

    @patch("framework_conftest.FailureArtifactManager.attach_screenshot")
    @patch("framework_conftest.FailureArtifactManager.capture_screenshot")
    @patch("framework_conftest.FailureSanitizer.sanitize")
    @patch("framework_conftest.ExecutionContext.duration")
    def test_pytest_runtest_makereport_skips_screenshot_when_driver_is_missing(
        self,
        duration,
        sanitize,
        capture_screenshot,
        attach_screenshot,
    ):
        duration.return_value = 1.25
        sanitize.return_value = "sanitized failure"

        item = Mock()
        item.name = "test_api_failure"
        item.funcargs = {}

        call = Mock()

        report = Mock()
        report.when = "call"
        report.passed = False
        report.failed = True
        report.longrepr = "original failure"

        outcome = Mock()
        outcome.get_result.return_value = report

        hook = conftest.pytest_runtest_makereport(item, call)

        next(hook)

        try:
            hook.send(outcome)
        except StopIteration:
            pass

        capture_screenshot.assert_not_called()
        attach_screenshot.assert_not_called()

    def test_pytest_html_results_table_header_adds_execution_metadata_columns(
    self,):
      cells = [
          "<th>Test</th>",
          "<th>Status</th>",
      ]

      conftest.pytest_html_results_table_header(cells)

      assert cells == [
          "<th>Test</th>",
          "<th>Status</th>",
          "<th>Execution ID</th>",
          "<th>Worker</th>",
          "<th>Thread</th>",
          "<th>Browser</th>",
          "<th>Session ID</th>",
      ]
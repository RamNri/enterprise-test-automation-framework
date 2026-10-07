
# Architect: Nripesh Kumar Srivastawa
# Role Profile: QA Automation Architect & AI Quality Specialist
# Credentials: AWS Certified Solutions Architect – Associate (SAA-C03)
# Core Expertise: Python, Advanced Pytest Concurrency, LLM/RAG Quality Engineering
# Enterprise Track Record: 13+ Years Experience (Ex-VMware MTS Q3, Ex-Amazon QAT)
# 
# 📬 FOR RECRUITMENT & COLLABORATION INQUIRIES:
# 📧 Direct Email: nripeshsrivastawa@gmail.com
# 🌐 GitHub: https://github.com/RamNri
# 
# *Status: Open for Senior QA Automation & AI/ML Testing opportunities.*

import pytest
import logging

from core.driver.driver_factory import DriverFactory
from core.logger import configure_logging

from core.execution.execution_context import ExecutionContext
from framework_logging.failure_sanitizer import FailureSanitizer
from framework_logging.failure_artifact_manager import (FailureArtifactManager,)
from config.framework_configurator import FrameworkConfigurator

logger = logging.getLogger("test.lifecycle")

configure_logging()


def pytest_addoption(parser):

    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to run tests on",
    )

    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode",
    )

    parser.addoption(
        "--execution-mode",
        action="store",
        default="local",
        choices=["local", "grid", "browserstack"],
        help="Execution mode: local, grid, or browserstack",
    )

    parser.addoption(
        "--env",
        action="store",
        default="local",
        help="Environmnet to run the tests against"

    )

def pytest_configure(config):
    environment = config.getoption("--env")
    browser = config.getoption("--browser")
    headless = config.getoption("--headless")
    execution_mode = config.getoption("--execution-mode")

    FrameworkConfigurator.configure(environment=environment, browser=browser, headless=headless, execution_mode=execution_mode)


@pytest.fixture
def driver():

    driver = DriverFactory.create()

    yield driver

    DriverFactory.quit()

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    worker_id = getattr(item.config, "workerinput", {},).get("workerid", "master",)
    ExecutionContext.set_worker_id(worker_id)
    ExecutionContext.start_test(item.nodeid)
    logger.info("TEST START")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):

    outcome = yield

    report = outcome.get_result()
    report.execution_id = ExecutionContext.execution_id()
    report.worker_id = ExecutionContext.worker_id()
    report.thread_id = ExecutionContext.thread_id()
    report.test_name = ExecutionContext.test_name()
    report.seed = ExecutionContext.seed()
    report.browser = ExecutionContext.browser()
    report.session_id = ExecutionContext.session_id()

    if report.when != "call":
        return
    status = "PASSED" if report.passed else "FAILED"
    logger.info(
        "TEST END | Status = %s | duration=%.3f sec", status, ExecutionContext.duration(),
    )

    if not report.failed:
        return

    failure_text = FailureSanitizer.sanitize(str(report.longrepr))
    logger.error("TEST FAILED | message=%s", failure_text,)

    driver = item.funcargs.get("driver")

    if driver is None:
        return

    filepath = FailureArtifactManager.capture_screenshot(driver, item.name,)

    FailureArtifactManager.attach_screenshot(report, filepath,)


def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>Execution ID</th>")
    cells.insert(3, "<th>Worker</th>")
    cells.insert(4, "<th>Thread</th>")
    cells.insert(5, "<th>Browser</th>")
    cells.insert(6, "<th>Session ID</th>")

def pytest_html_results_table_row(report, cells):
    cells.insert(
        2,
        f"<td>{getattr(report, 'execution_id', '-')}</td>",
    )

    cells.insert(
        3,
        f"<td>{getattr(report, 'worker_id', '-')}</td>",
    )
    cells.insert(
    4,
    f"<td>{getattr(report, 'thread_id', '-')}</td>",
    )
    cells.insert(
        5,
        f"<td>{getattr(report, 'browser', '-')}</td>",
        )
    cells.insert(
        6,
        f"<td>{getattr(report, 'session_id', '-')}</td>",
    )

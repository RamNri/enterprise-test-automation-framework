import logging

from selenium import webdriver

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from config import settings

from core.driver.browser import Browser
from core.driver.driver_options import DriverOptions
from core.execution.execution_context import ExecutionContext

from config.browserstack_config import BrowserStackConfig

logger = logging.getLogger(__name__)


# ============================================================
# Browser creator functions
# ============================================================

def _create_chrome(options):

    return webdriver.Chrome(
        service=ChromeService(
            ChromeDriverManager().install()
        ),
        options=options,
    )


def _create_firefox(options):

    return webdriver.Firefox(
        service=FirefoxService(
            GeckoDriverManager().install()
        ),
        options=options,
    )


def _create_edge(options):

    return webdriver.Edge(
        service=EdgeService(
            EdgeChromiumDriverManager().install()
        ),
        options=options,
    )


# ============================================================
# Driver Factory
# ============================================================

class DriverFactory:


    _CREATORS = {
        Browser.CHROME: _create_chrome,
        Browser.FIREFOX: _create_firefox,
        Browser.EDGE: _create_edge,
    }

    @staticmethod
    def create():

        # Read browser configuration
        browser = Browser(settings.BROWSER)

        # Create browser options
        options = DriverOptions.create(browser, settings.HEADLESS)

        if settings.EXECUTION_MODE == "grid":
            driver = webdriver.Remote(command_executor=settings.GRID_URL, options=options)

        elif settings.EXECUTION_MODE == "browserstack":
            capabilities = BrowserStackConfig.capabilities()

            for key, value in capabilities.items():
                options.set_capability(key, value)
      
            driver = webdriver.Remote(command_executor=BrowserStackConfig.hub_url(), options=options)
        
        else:

            # Find correct browser creator
            creator = DriverFactory._CREATORS[browser]

            # Create the browser driver
            driver = creator(options)

        try:
            # Publish execution context
            ExecutionContext.set_driver(driver)
            ExecutionContext.set_browser(browser.value)
            ExecutionContext.set_session_id(driver.session_id)

        except Exception:
            try:
                driver.quit()
            except Exception:
                logger.exception(
                    "Failed to clean up browser after driver creation"
                )

            finally:
                DriverFactory._clear_execution_context()

            raise

        logger.info("Browser created : %s", browser.value,)

        logger.info("Session Id : %s", driver.session_id,)

        return driver

    @staticmethod
    def current():

        return ExecutionContext.driver()

    @staticmethod
    def quit():

        driver = ExecutionContext.driver()

        if driver is None:
            return

        logger.info(
            "Closing browser session %s",
            driver.session_id,
        )
        try:
            driver.quit()

        finally:
            DriverFactory._clear_execution_context()

    @staticmethod
    def _clear_execution_context():

        try:
            ExecutionContext.set_driver(None)
        except Exception:
            pass

        try:
            ExecutionContext.set_browser(None)
        except Exception:
            pass

        try:
            ExecutionContext.set_session_id(None)
        except Exception:
            pass
import os
from config import settings

class BrowserStackConfig:

  @staticmethod
  def username():
    return os.getenv("BROWSERSTACK_USERNAME")

  @staticmethod
  def access_key():
    return os.getenv("BROWSERSTACK_ACCESS_KEY")

  @staticmethod
  def hub_url():
    return "https://hub.browserstack.com/wd/hub"

  @staticmethod
  def capabilities():
    return {
      "browserName": settings.BROWSER,
      "browserVersion": settings.BROWSERSTACK_BROWSER_VERSION,
      "bstack:options":{
        "userName": BrowserStackConfig.username(),
        "accessKey": BrowserStackConfig.access_key(),
        "os": settings.BROWSERSTACK_OS,
        "osVersion": settings.BROWSERSTACK_OS_VERSION,
        "projectName": settings.BROWSERSTACK_PROJECT_NAME,
        "buildName": settings.BROWSERSTACK_BUILD_NAME,
      },
    }
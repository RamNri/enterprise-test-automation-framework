ENVIRONMENT = "local"
BASE_URL = None
API_BASE_URL=None

#=========================================
#UI Settings
#=========================================
USERNAME = "standard_user"
PASSWORD = "secret_sauce"
TIMEOUT = 10
BROWSER = "chrome"
HEADLESS = False

EXECUTION_MODE = "local"
GRID_URL = "http://selenium-hub:4444"

#==========================================
#API Settings
#==========================================

REQUEST_TIMEOUT = 30
API_USERNAME = "admin"
API_PASSWORD = "password123"
MAX_API_RESPONSE_TIME = 5

#===========================================
#Retry settings
#===========================================
MAX_RETRIES = 3
RETRY_DELAY = 1  #SECONDS
RETRY_BACKOFF = 2  #EXPONENTIAL MULTIPLIER

RETRY_STATUS_CODES = {
  500,  #Internal server error
  502,  #Bad Gateway
  503,  #Service Unavailable
  504   #Gateway timeout
}

BROWSERSTACK_OS = "windows"
BROWSERSTACK_OS_VERSION = "11"
BROWSERSTACK_BROWSER_VERSION = "latest"
BROWSERSTACK_PROJECT_NAME = "Enterprise Test Automation Framework"
BROWSERSTACK_BUILD_NAME = "Local Build"

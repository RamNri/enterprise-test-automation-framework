import allure
import logging
from selenium.webdriver.common.by import By
from pages.inventory_page import InventoryPage
from pages.base_page import BasePage
from config.settings import BASE_URL

logger = logging.getLogger(__name__)


class LoginPage(BasePage):

    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, '[data-test="error"]')

    def __init__(self, driver):
        super().__init__(driver)

    @allure.step("Open login page")
    def open(self):
        logger.info("Opening %s", BASE_URL)
        self.driver.get(BASE_URL)
        return self
    
    def enter_username(self, username):
        self.type(self.USERNAME, username)

    def enter_password(self, password):
        self.type(self.PASSWORD, password)
    
    def click_login(self):
        self.find(self.LOGIN_BUTTON).click()
    
    def login(self, username, password):
        logger.info("Attempting login with user '%s'", username)
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        return self

    def get_error_message(self):
        return self.get_text(self.ERROR_MESSAGE)
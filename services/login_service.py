import allure
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from config import settings
from api.clients.auth_client import AuthClient


class LoginService:
  def __init__(self, driver):
    self.login_page = LoginPage(driver)

  def login(self, username, password):
     with allure.step("Login"):
      self.login_page.open().login(username, password,)
     return InventoryPage(self.login_page.driver)
    
  def login_as_standard_user(self):
    return self.login(settings.USERNAME, settings.PASSWORD)
  
  def login_via_api(self, username, password):
    token = AuthClient().login(username,password)
    return token

  def login_and_get_error(self, username, password,):
    self.login_page.open().login(username, password,)
    return self.login_page.get_error_message()
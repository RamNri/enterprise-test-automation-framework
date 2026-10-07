import allure
import pytest
from test_data.login_data import (
  VALID_LOGIN_USERS,
  INVALID_LOGIN_USERS,
)
from services.login_service import LoginService

@pytest.mark.parametrize(
    "username,password",
    VALID_LOGIN_USERS,
     ids=[

        "Standard User",

        "Problem User",

        "Performance User",
    ],
)

def test_successful_login(driver, username, password):
  allure.dynamic.parameter("password", "********")
  inventory = ( 
    LoginService(driver).login(username, password)
  )
  assert inventory.is_loaded()  

@pytest.mark.parametrize( "username,password", INVALID_LOGIN_USERS,
  ids=[
    "Locked user",
  ],
)
def test_locked_user_cannot_login(driver, username, password,):
  error_message = LoginService(driver).login_and_get_error(username, password,)
  assert error_message == ("Epic sadface: Sorry, this user has been locked out.")
  

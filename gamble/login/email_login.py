import time
from typing import Callable
from logging import getLogger

from selenium.webdriver import Chrome

from service.f import FPwd
from service.utils import configure_logger

from gamble.login.base import BaseLogin
from gamble.login.handlers import FormHandler


class LoginEmail(BaseLogin):
    EMAIL_FIELD = '//input[contains(@placeholder, "Email") or contains(@placeholder, "email")]'
    PWD_FIELD = '//input[contains(@placeholder, "Password") or contains(@placeholder, "password")]'
    SUBMIT_BTN = '//button[contains(text(), "Log in") or contains(text(), "log in")]'

    def __init__(self, chrome: Chrome, page_url: str, email: str, password: str, email_xpath: str = '',
                 password_xpath: str = '', submit_xpath: str = '', error_msg_xpath: str = '',
                 open_page_func: Callable = None):
        super().__init__(browser=chrome)
        self.form_handler = FormHandler(browser=chrome)
        self.page_url = page_url
        self._email = email
        self._password = FPwd(addr=password).get_addr()
        self.email_field = self.EMAIL_FIELD if not email_xpath else email_xpath
        self.password_field = self.PWD_FIELD if not password_xpath else password_xpath
        self.submit_btn = self.SUBMIT_BTN if not submit_xpath else submit_xpath
        self.error_msg_xpath = error_msg_xpath
        self.open_page_func = open_page_func
        self.logger = getLogger(self.__class__.__name__)
        configure_logger(self.logger)

        self.filling_script = ((self.email_field, self._email), (self.password_field, self._password))
        self.clicks_script = ((self.SUBMIT_BTN, 0.2),)

    def login(self):
        if not self.open_page_func:
            self.browser.get(self.page_url)
        else:
            self.open_page_func(self.page_url)

        for field_xpath, field_value in self.filling_script:
            self.form_handler.fill_input_by_xpath(input_xpath=field_xpath, text=field_value)
        time.sleep(3)

        for btn_xpath, wait_time in self.clicks_script:
            self.form_handler.button_click(btn_xpath)
            time.sleep(0.5)

        time.sleep(3)
        error_element = self.form_handler.get_element(self.error_msg_xpath)
        if error_element is not None:
            raise ValueError('Found Error Message on login: ' + error_element.text)

        return True

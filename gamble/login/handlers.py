from typing import Union, List
from logging import getLogger

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, \
    ElementClickInterceptedException
from selenium.webdriver.remote.webelement import WebElement

from service.utils import configure_logger


class FormHandler:
    def __init__(self, browser: Chrome):
        self.browser = browser
        self.logger = getLogger(self.__class__.__name__)
        configure_logger(self.logger)

    def button_click(self, xpath: str):
        try:
            button = self.browser.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            self.logger.error(f'The button with xpath="{xpath}" doesn\'t exists')
        else:
            try:
                button.click()
            except (ElementClickInterceptedException, ElementNotInteractableException):
                self.browser.execute_script("arguments[0].click();", button)
            self.logger.info(f'The button with xpath="{xpath}" successfully clicked')

    def get_element(self, xpath: str, _all: bool = False) -> Union[WebElement, List[WebElement], None]:
        try:
            element = self.browser.find_elements(By.XPATH, xpath) if _all else self.browser.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            element = None
        return element

    def fill_input_by_xpath(self, input_xpath: str, text: str) -> None:
        try:
            element = self.browser.find_element(By.XPATH, input_xpath)
        except NoSuchElementException:
            self.logger.error(f'The input field with xpath="{input_xpath}" doesn\'t exist')
        else:
            # element.clear()
            element.send_keys(text)
            self.logger.info(f'In the input field with xpath="{input_xpath}" successfully recorded custom value')

    def fill_input_by_id(self, input_id: str, text: str) -> None:
        try:
            element = self.browser.find_element(By.ID, input_id)
        except NoSuchElementException:
            element = self.get_element(f'//input[@id="{input_id}"]')
            if element is None:
                msg = f'No found input with id {input_id}'
                raise NoSuchElementException(msg=msg)
        try:
            element.clear()
            element.send_keys(text)
        except ElementNotInteractableException:
            self.logger.error(f'The input field with id="{input_id}" doesn\'t interactable')
        else:
            self.logger.info(f'In the input field with id="{input_id}" successfully recorded custom value')

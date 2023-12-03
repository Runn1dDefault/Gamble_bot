from typing import Any
from logging import getLogger

from selenium.webdriver import Chrome
from service.utils import configure_logger


class BaseLogin:
    def __init__(self, browser: Chrome, **kwargs):
        self.browser = browser
        self.logger = getLogger(self.__class__.__name__)
        configure_logger(self.logger)

    def login(self) -> Any:
        pass

import re
import time
from logging import getLogger

from selenium.common.exceptions import WebDriverException

from service.csv_saver import save_row

from gamble.login.base import BaseLogin
from gamble.handlers import GambleBrowserHandler
from service.utils import configure_logger


class GambleBase(GambleBrowserHandler):
    GAMBLE_SITE: str
    GAMBLE_URL: str
    MAKE_LOGIN: bool = True
    LOGIN_CLS: BaseLogin = BaseLogin
    LOGIN_PAGE: str = ''

    def __init__(self, link: str = None, *args, **kwargs):
        if link is not None:
            self.GAMBLE_SITE = link

        assert self.GAMBLE_SITE and self.GAMBLE_URL

        super().__init__(*args, **kwargs)
        self.logger = getLogger(self.__class__.__name__)
        configure_logger(self.logger)
        self.logger_preposition = f'{self.GAMBLE_SITE}: '
        self.login_kwargs = dict()

    def init_login_kwargs(self):
        pass

    def init_login_cls(self, **kwargs):
        self.init_login_kwargs()
        self.login_kwargs.update(kwargs)
        return self.LOGIN_CLS(**self.login_kwargs)

    def take_a_screen(self):
        pass

    def start_game(self):
        pass

    def check_spin_button(self):
        pass

    def check_bet_max(self):
        pass

    def extract_data_images(self):
        pass

    def extract_txt_from_data_images(self) -> dict:
        pass

    def extract_data(self):
        pass

    def extract_amounts(self, *args, **kwargs) -> dict:
        pass

    def checking_messages(self) -> None:
        pass

    def get_page(self, url: str) -> bool:
        try:
            page_opened = super().get_page(url)
        except WebDriverException as e:
            self.logger.error(
                f'{self.logger_preposition}When you open the page {url} in Chrome exception occurred: {e}'
            )
            page_opened = False
        else:
            self.logger.info(
                f'{self.logger_preposition}The page {url} successfully loaded in Chrome'
            )
        return page_opened

    @staticmethod
    def search_with_regex(pattern: str, s: str) -> str:
        match = re.search(pattern, s)
        balance = match[0] if match else ''
        return balance
    
    def click_start_game(self):
        start_xpath = '//*[@id="click_to_play_game"]'
        start = self.browser.find_element_by_xpath(start_xpath)
        start.click()
        time.sleep(30)
        self.logger.info('CLICK TO Start GAME')

    def read_data(self):
        self.extract_data()
        result = self.extract_amounts()
        self.logger.debug(result)
        save_row(data=result)
        return result

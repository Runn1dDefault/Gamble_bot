import re
import time
import datetime
from typing import Dict, Union, Optional

from exceptions import PageException


from gamble.games.templates import GambleByCoordinates
from gamble.mixins.pimped_mixins import PimpedCoordinatesMixin, PimpedRecognitionMixin
from gamble.login import LoginEmail
from service.utils import validate_str_digit


class PimpedGame(PimpedRecognitionMixin, PimpedCoordinatesMixin, GambleByCoordinates):
    GAMBLE_SITE = "https://www.dunder.com/"
    GAMBLE_URL = "https://www.dunder.com/en/game/pimped-png"
    LOGIN_PAGE = 'https://www.dunder.com/en/login'
    LOGIN_CLS = LoginEmail
    CANVAS_XPATH = '//iframe[@data-id="gameplay-iframe"]'
    SCREEN_ELEMENT = CANVAS_XPATH
    ACCEPT_COOKIES_BTN = '//div[contains(@class, "cookie")]/button'
    MAKE_LOGIN = True
    INIT_SIZE = (1920, 1080)

    def init_login_kwargs(self):
        self.login_kwargs = {'chrome': self.browser, 'page_url': self.LOGIN_PAGE,
                             'open_page_func': self.get_page,
                             'error_msg_xpath': '//span[@data-testid="loginFormErrorMessage"]'}

    def start_game(self):

        self._checking_errors_on_page()

        self.logger.info('Start waiting to loading...')
        self.__waiting_continue()
        self.logger.info('End waiting to loading')
        self.click_continue()

        self.initialize_coordinates()
        self.click_amount_coins_add(n=self.click_coin_add_qty)
        self.click_speed_button()

    def __waiting_continue(self) -> None:
        continue_btn_text = ''

        self.logger.info('Before while loop')

        while 'continue' not in continue_btn_text.lower():
            self.take_a_screen()
            self.checking_messages()

            continue_btn_text = self.checking_continue_btn()
            time.sleep(2)

    def click_amount_coins_add(self, n: int):
        for _ in range(abs(n) or 3):
            self.click_coin_value_add()

    def checking_messages(self) -> None:
        self.coordinates.msg_cancel_btn = self.coordinates.calc_coordinates_button(kx=0.415, ky=0.6)
        self.click_by_coordinates(*self.coordinates.msg_cancel_btn.values())

    def _checking_errors_on_page(self) -> None:
        if self._check_unavailable() is True or self._check_403() is True:
            raise PageException('Error on page unavailable or 403 in game!')

    def _check_unavailable(self) -> bool:
        unavailable = self.find_element_or_none('//p[@data-testid="gameIsNotAvailableError"]')

        if unavailable:
            log_msg = 'Found error message: %s' % unavailable.text
            self.logger.info(log_msg)
            return True

        return False

    def _check_403(self) -> Optional[bool]:
        outer_iframe = self.find_element_or_none(self.CANVAS_XPATH)

        if not outer_iframe:
            log_msg = 'Not found error 403 OUTER iframe'
            self.logger.debug(log_msg)
            return

        self.browser.switch_to.frame(outer_iframe)
        inner_iframe = self.find_element_or_none('gameFrame', is_id=True)

        if not inner_iframe:
            log_msg = 'Not found error 403 INNER iframe'
            self.logger.debug(log_msg)
            self.browser.switch_to.default_content()
            return

        self.browser.switch_to.frame(inner_iframe)
        title_el = self.find_element_or_none('//h1')

        if not title_el:
            log_msg = 'Not found h1 element in INNER iframe for checking 403 error'
            self.logger.debug(log_msg)
            self.browser.switch_to.default_content()
            return

        found = True if '403' in title_el.text else False
        self.browser.switch_to.default_content()
        return found

    def get_page(self, url: str) -> bool:
        opened = super().get_page(url)

        location_err_el = self.find_element_or_none('//p[@class="c-maintenance__text"]')

        if location_err_el:
            raise PageException(location_err_el.text.lower())

        return opened

    def extract_amounts(self) -> Dict[str, Union[str, float]]:
        balance_text = self._check_balance()
        balance_search = re.findall(r'\d+\W+\d+', balance_text)
        balance = abs(float(validate_str_digit(balance_search[0]))) if balance_search else 0.0

        win_text = self._check_win_amount()
        win_search = re.findall(r'\d+\.\d+', win_text)
        win = abs(float(validate_str_digit(win_search[0]))) if win_search else 0.0

        bet_text = self._check_bet_amount()
        bet_search = re.findall(r'\d+\.\d+', bet_text)
        bet = abs(float(validate_str_digit(bet_search[0]))) if bet_search else 0.0

        return {
            'Datetime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Balance': balance,
            'Bet': bet,
            'Win': win
        }

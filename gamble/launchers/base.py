import time
from random import randint
from logging import getLogger
from typing import Dict, Any, Union, Iterable

from requests import HTTPError

from api import APIClient
from service.utils import get_registration_data, wait_sometimes, configure_logger

from gamble.games.templates import GambleByCoordinates


class BaseGambleLauncher:
    SPIN_CHECK: Iterable[str] = ('spin', 'spi', 'sp', 'pin', 'in')
    GAMBLE_CHECK = ('ga', 'gam', 'ble', 'amb')
    WIN_TEXT = 'win'
    GAMBLE_LIMIT_TEXT = 'gamble limit'
    WAIT_BTN_APPEARS: int = 5
    GAMBLE_SITES: Dict[str, Any] = None
    DICT_COLOR = {1: "Red", 2: "Black"}
    DICT_CART_SUITS = {1: 'Hearts', 2: 'Diamonds', 3: 'Clubs', 4: 'Spades'}
    running = False
    game: GambleByCoordinates = None
    wait_time: Union[float, int] = 0

    def __init__(self, site_name: str, ext_value: Union[float, int], min_balance_value: Union[float, int] = None,
                 min_gamble_amount: Union[int, float] = None, api_client: APIClient = None):
        assert self.GAMBLE_SITES

        self.logger = getLogger(self.__class__.__name__)
        configure_logger(self.logger)
        self.site_name = site_name
        self.game_cls = self.GAMBLE_SITES.get(self.site_name)
        self.api_client = api_client

        self.ext_value = ext_value
        self.min_balance_value = min_balance_value
        self.min_gamble_amount = min_gamble_amount
        self.logger.info('Initialize...\nExt Value: {}\nMin Balance: {}\nMin Gamble: {}\n'.format(
            self.ext_value, self.min_balance_value, self.min_gamble_amount
        ))

    def run_game_process(self):
        self.running = True

    # WARNING: wait_sometimes only for dev tests
    @wait_sometimes
    def init_game(self, coin_clicks_amount: int = 3, game_link: str = None, use_proxy: bool = False):
        self.game = self.GAMBLE_SITES.get(self.site_name, GambleByCoordinates)(
            link=game_link,
            use_proxy=use_proxy,
            click_coin_add_qty=coin_clicks_amount
        )

    def stop_game_process(self, reason: str):
        self.running = False
        self.game.browser.quit()
        self.save_game_log(reason)

    def refresh_page(self):
        self.save_game_log('Browser will be refreshed')
        self.game.browser.refresh()

    def save_game_log(self, msg: str) -> None:
        if not self.api_client:
            return

        try:
            self.api_client.save_logs(site_name=self.site_name, message=msg)
            self.logger.debug(f'[{self.site_name}] {msg}')
        except HTTPError as e:
            self.logger.error(e)

    def init_registration(self) -> Dict[str, Any]:
        for _ in range(3):
            try:
                return get_registration_data(self.site_name, self.api_client.get_registrations())
            except HTTPError as e:
                self.save_game_log(f'Error in launched game: {e}')
                self.api_client._token = None
                time.sleep(1)
                continue

    def make_login(self):
        if self.game.MAKE_LOGIN:
            registration_data = self.init_registration()

            if registration_data is None:
                return

            self.game.init_login_cls(email=registration_data['profile']['user']['email'],
                                     password=registration_data['profile']['user']['addr']).login() #its password from django admin

    def make_gamble_logic(self, win_amount, balance):
        time.sleep(1)
        # if win_amount < 300:
        #     self.select_random_suit()
        # elif win_amount >= 300:
        self.gamble_random_case(win_amount, balance)

    def select_random_color(self):
        rand_number = randint(1, 2)

        if rand_number == 1:
            self.game.click_red_button()
        else:
            self.game.click_black_button()

        self.save_game_log(f'{self.DICT_COLOR[rand_number]} color was chosen')

    def select_random_suit(self):
        rand_number = randint(1, 4)

        if rand_number == 1:
            self.game.click_hearts_button()
        elif rand_number == 2:
            self.game.click_diamonds_button()
        elif rand_number == 3:
            self.game.click_clubs_button()
        else:
            self.game.click_spades_button()

        self.save_game_log(f'{self.DICT_CART_SUITS[rand_number]} was chosen')

    def gamble_random_case(self, win_amount, balance):
        # win x2 > target == color
        # win x4 > target == suit
        self.logger.info(f"{win_amount}, {self.ext_value}, {win_amount * 2 + balance}")
        if win_amount * 2 + balance >= self.ext_value:
            self.select_random_color()
        else:
            self.select_random_suit()
        # if win_amount * 2 < self.ext_value and win_amount * 4 <= self.ext_value:
        #     self.logger.info("win_amount * 2 < self.ext_value and win_amount * 4 <= self.ext_value")
        #     self.select_random_suit()
        # elif win_amount * 2 < self.ext_value and win_amount * 4 > self.ext_value:
                #     self.logger.info("win_amount * 2 > self.ext_value and win_amount * 4 > self.ext_value")
                #     self.select_random_suit()
        # elif win_amount * 2 >= self.ext_value and self.ext_value < win_amount * 4:
        #     self.logger.info("win_amount * 2 >= self.ext_value and self.ext_value < win_amount * 4")
        #     self.select_random_color()

        # else:
        #     self.logger.info("else")
        #     self.select_random_suit()

    def wait(self):
        time.sleep(self.wait_time)

    def spin_btn_available(self) -> bool:
        btn_text = self.game.check_spin_button().lower()

        if all(check_word not in btn_text for check_word in self.SPIN_CHECK):
            return False
        return True

    def gamble_btn_available(self) -> bool:
        btn_text = self.game.check_bet_max().lower()

        if all(check_word not in btn_text for check_word in self.GAMBLE_CHECK):
            return False
        return True

    def _take_screen(self):
        self.game.take_a_screen()
        self.game.checking_messages()

    def _waiting_for_gamble_button(self) -> bool:
        self.logger.debug('START WAITING FOR GAMBLE BUTTON...')

        start_time = time.monotonic()

        while self.gamble_btn_available() is False:
            self._take_screen()

            if time.monotonic() - start_time > self.WAIT_BTN_APPEARS:
                return False

            self.wait()

        self.logger.debug('OVER WAITING FOR GAMBLE BUTTON!')
        return True

    def _waiting_for_spin_button(self) -> bool:
        self.logger.debug('START WAITING FOR GAMBLE BUTTON...')

        start_time = time.monotonic()

        while self.spin_btn_available() is False and self.gamble_btn_available():
            self._take_screen()

            if time.monotonic() - start_time > self.WAIT_BTN_APPEARS:
                return False

            self.wait()

        self.logger.debug('OVER WAITING FOR GAMBLE BUTTON!')
        return True

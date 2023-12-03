import time
from typing import Dict

from gamble.games.base import GambleBase
from gamble.handlers import ScreenshotHandler, GambleCanvasCoordinates


class GambleByCoordinates(GambleBase):
    CANVAS_XPATH: str
    SCREEN_ELEMENT: str = None

    def __init__(self, click_coin_add_qty: int = 3, *args, **kwargs):
        assert self.CANVAS_XPATH

        super().__init__(*args, **kwargs)
        self.coordinates = GambleCanvasCoordinates(self.CANVAS_XPATH, browser=self.browser)
        self.screens = ScreenshotHandler(element_xpath=self.SCREEN_ELEMENT if self.SCREEN_ELEMENT else None,
                                         dir_name=self.__class__.__name__.lower(), browser=self.browser)
        self.click_coin_add_qty = click_coin_add_qty

    def initialize_coordinates(self) -> None:
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')

    def click_continue(self):
        self.logger.debug('CLICK CONTINUE')
        self.click_by_coordinates(*self.coordinates.continue_button.values())
        time.sleep(5)
        self.logger.debug('CONTINUE DONE')

    def click_coin_value_add(self, *args, **kwargs):
        self.logger.debug('CLICK COIN ADD')
        self.click_by_coordinates(*self.coordinates.coin_value_add.values())

    def click_spin_button_stupid(self):
        self.logger.debug('CLICK SPIN STUPID')
        self.click_by_coordinates(*self.coordinates.spin.values())
        time.sleep(5)
        self.take_a_screen()
        self.read_data()
        time.sleep(1)

    def save_data(self):
        return self.read_data()

    def click_spin_button(self):
        self.logger.debug('CLICK SPIN')
        self.click_by_coordinates(*self.coordinates.spin.values())

    def click_gamble_button(self):
        self.logger.debug('CLICK GAMBLE')
        self.click_by_coordinates(*self.coordinates.gamble_button.values())

    def click_cash_out_button(self):
        self.logger.debug('CLICK CASH OUT')
        self.click_by_coordinates(*self.coordinates.cash_out_button.values())

    def click_red_button(self):
        self.logger.debug('CLICK RED BUTTON')
        self.click_by_coordinates(*self.coordinates.red_button.values())

    def click_black_button(self):
        self.click_by_coordinates(*self.coordinates.black_button.values())

    def click_hearts_button(self):
        self.logger.debug('CLICK HEARTS BUTTON')
        self.click_by_coordinates(*self.coordinates.hearts_button.values())

    def click_diamonds_button(self):
        self.logger.debug('CLICK DIAMONDS BUTTON')
        self.click_by_coordinates(*self.coordinates.diamonds_button.values())

    def click_clubs_button(self):
        self.logger.debug('CLICK CLUBS BUTTON')
        self.click_by_coordinates(*self.coordinates.clubs_button.values())

    def click_spades_button(self):
        self.logger.debug('CLICK SPADES BUTTON')
        self.click_by_coordinates(*self.coordinates.spades_button.values())

    def click_speed_button(self):
        self.logger.debug('CLICK SPEED BUTTON')
        self.click_by_coordinates(*self.coordinates.speed.values())

    def take_a_screen(self) -> None:
        self.screens.save_screenshot()

    def checking_msg_cancel_btn(self) -> str:
        pass

    def check_bet_max(self) -> str:
        pass

    def check_spin_button(self) -> str:
        pass

    def check_win_coins(self) -> str:
        pass

    def extract_amounts(self, *args, **kwargs) -> Dict[str, float]:
        pass

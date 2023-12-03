import multiprocessing as mp
from time import monotonic
from typing import List

from recogniser import ImageTxtRecogniserCv2

from gamble.types import MultiplyCrop
from service.utils import value_in_list


class PimpedCoordinatesMixin:
    WINDOW_FULL_SIZE = True

    def initialize_coordinates(self) -> None:
        super().initialize_coordinates()
        self.coordinates.balance = self.coordinates.calc_coordinates_image(kx1=0.337, ky1=0.971, kx2=0.425, ky2=0.999)
        self.logger.debug(f'Balance image has properties: {self.coordinates.balance}')
        self.coordinates.bet = self.coordinates.calc_coordinates_image(kx1=0.474, ky1=0.971, kx2=0.532, ky2=0.999)
        self.logger.debug(f'Bet image has properties: {self.coordinates.bet}')
        self.coordinates.win = self.coordinates.calc_coordinates_image(kx1=0.626, ky1=0.971, kx2=0.688, ky2=0.999)
        self.logger.debug(f'Win image has properties: {self.coordinates.bet}')

    def click_continue(self):
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.continue_button = self.coordinates.calc_coordinates_button(kx=0.5, ky=0.8)
        self.logger.debug(f'Continue button has properties: {self.coordinates.continue_button}')
        super().click_continue()

    def click_coin_value_add(self):
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.coin_value_add = self.coordinates.calc_coordinates_button(kx=0.085, ky=0.916)
        self.logger.debug(f'Coins value add button has properties: {self.coordinates.coin_value_add}')
        super().click_coin_value_add()

    def click_spin_button(self):
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.spin = self.coordinates.calc_coordinates_button(kx=0.79, ky=0.916)
        self.logger.debug(f'Spin button has properties: {self.coordinates.spin}')
        super().click_spin_button()

    def click_gamble_button(self):
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.gamble_button = self.coordinates.calc_coordinates_button(kx=0.645, ky=0.911)
        self.logger.debug(f'Gamble button has properties: {self.coordinates.gamble_button}')
        super().click_gamble_button()

    def click_cash_out_button(self):
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.cash_out_button = self.coordinates.calc_coordinates_button(kx=0.835, ky=0.911)
        self.logger.debug(f'Cash out button has properties: {self.coordinates.cash_out_button}')
        super().click_cash_out_button()

    def click_red_button(self):
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.red_button = self.coordinates.calc_coordinates_button(kx=0.35, ky=0.45)
        self.logger.debug(f'Red button has properties: {self.coordinates.red_button}')
        super().click_red_button()

    def click_black_button(self):
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.black_button = self.coordinates.calc_coordinates_button(kx=0.35, ky=0.55)
        self.logger.debug(f'Black button has properties: {self.coordinates.black_button}')
        super().click_black_button()

    def click_hearts_button(self):
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.hearts_button = self.coordinates.calc_coordinates_button(kx=0.65, ky=0.45)
        self.logger.debug(f'Hearts button has properties: {self.coordinates.hearts_button}')
        super().click_hearts_button()

    def click_diamonds_button(self):
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.diamonds_button = self.coordinates.calc_coordinates_button(kx=0.7, ky=0.45)
        self.logger.debug(f'Diamonds button has properties: {self.coordinates.diamonds_button}')
        super().click_diamonds_button()

    def click_clubs_button(self):
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.clubs_button = self.coordinates.calc_coordinates_button(kx=0.65, ky=0.55)
        self.logger.debug(f'Clubs button has properties: {self.coordinates.clubs_button}')
        super().click_clubs_button()

    def click_spades_button(self):
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.spades_button = self.coordinates.calc_coordinates_button(kx=0.7, ky=0.55)
        self.logger.debug(f'Spades button has properties: {self.coordinates.spades_button}')
        super().click_spades_button()

    def click_speed_button(self):
        self.coordinates.init_canvas()
        self.logger.debug(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.speed = self.coordinates.calc_coordinates_button(kx=0.09, ky=0.98)
        self.logger.debug(f'Speed button has properties: {self.coordinates.speed}')
        super().click_speed_button()


def adaptive_recognizing(filepath: str, adaptive_pity: int, data: list, expected_values: List[str]):
    recognizer = ImageTxtRecogniserCv2()
    recognized_value = recognizer.recognize_by_adaptive_threshold(filepath=filepath, adaptive_pity=adaptive_pity)

    if value_in_list(value=recognized_value, check_list=expected_values):
        data.append(recognized_value)


class PimpedRecognitionMixin:
    RECOGNISING_LIMIT = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recognizer = ImageTxtRecogniserCv2()

    def checking_continue_btn(self):
        filepath = self.screens.save_crop(
            new_filename='continue_button.png',
            multiply_to=MultiplyCrop(0.4, 0.77, 0.6, 0.84)
        )
        return self.recognizer.recognize_by_adaptive_threshold(filepath=filepath, adaptive_pity=3)

    def checking_msg_cancel_btn(self):
        # no used
        filepath = self.screens.save_crop(
            new_filename='msg_cancel.png',
            multiply_to=MultiplyCrop(0.39, 0.585, 0.475, 0.62)
        )
        simple = self.recognizer.recognize_original(filepath=filepath)
        if 'can' in simple:
            return simple
        return self.recognizer.recognize_by_adaptive_threshold(filepath=filepath, adaptive_pity=7)

    def check_spin_button(self):
        """
        MultiplyCrop(0.76, 0.9, 0.826, 0.94)
        MultiplyCrop(0.74, 0.9, 0.84, 0.95)
        MultiplyCrop(0.74, 0.89, 0.84, 0.95)
        MultiplyCrop(0.74, 0.885, 0.848, 0.95)
        MultiplyCrop(0.735, 0.89, 0.845, 0.95)
        """
        filepath = self.screens.save_crop(
            new_filename='spin.png',
            multiply_to=MultiplyCrop(0.76, 0.9, 0.826, 0.94)
        )
        simple = self.recognizer.recognize_original(filepath=filepath)
        
        if 'sp' in simple.lower() or 'st' in simple.lower():
            return simple

        return self.recognizer.recognize_by_adaptive_threshold(
            filepath=filepath, 
            adaptive_pity=23
        ) 

    def check_bet_max(self):
        """
        MultiplyCrop(0.615, 0.92, 0.69, 0.942)
        MultiplyCrop(0.597, 0.91, 0.708, 0.955)
        MultiplyCrop(0.6, 0.91, 0.7, 0.95)
        MultiplyCrop(0.57, 0.91, 0.7, 0.95)
        MultiplyCrop(0.6, 0.905, 0.705, 0.951)
        """
        filepath = self.screens.save_crop(
            new_filename='bet_max.png',
            multiply_to=MultiplyCrop(0.615, 0.92, 0.69, 0.942)
        )
        simple = self.recognizer.recognize_original(filepath=filepath).lower()
        if 'ga' in simple or 'bet' in simple:
            return simple

        return self.recognizer.recognize_by_adaptive_threshold(
            filepath=filepath, 
            adaptive_pity=23
        )

    def check_win_coins(self) -> str:
        filename = 'coins.png'
        self.screens.save_crop(
            new_filename=filename,
            multiply_to=MultiplyCrop(0.25, 0.83, 0.65, 0.877),
            resize_x=1400, resize_y=100
        )
        return self.screens.get_text_from_png(filename)

    def extract_data(self) -> str:
        filepath = self.screens.save_crop(
            new_filename='result.png',
            multiply_to=MultiplyCrop(0.18, 0.97, 0.668, 1),
            resize_x=1200, resize_y=100
        )
        return self.recognizer.recognize_original(filepath)

    def _check_balance(self) -> str:
        filepath = self.screens.save_crop(
            new_filename='balance.png',
            multiply_to=MultiplyCrop(0.15,  0.97, 0.36, 1)
        )
        return self.recognizer.recognize_original(filepath)
    
    def _check_win_amount(self):
        filepath = self.screens.save_crop(
            new_filename='win_amount.png',
            multiply_to=MultiplyCrop(0.55, 0.97, 0.669, 1)
        )
        return self.recognizer.recognize_original(filepath)

    def _check_bet_amount(self):
        filepath = self.screens.save_crop(
            new_filename='bet_amount.png',
            multiply_to=MultiplyCrop(0.35, 0.97, 0.55, 1)
        )
        return self.recognizer.recognize_original(filepath)

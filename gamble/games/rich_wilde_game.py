import re
import time
import datetime
from typing import Dict

from recogniser import ImageTxtRecogniserCv2
from gamble.types import MultiplyCrop
from gamble.games.templates import GambleByCoordinates


class RichWildeGame(GambleByCoordinates):
    GAMBLE_SITE = "https://www.betamo.com/"
    GAMBLE_URL = "https://www.betamo.com/game/book-of-dead"
    CANVAS_XPATH = '//*[@id="game-block-0"]'

    # Take into account that the resolution of print screen
    # does not correspond to the resolution of the browser in Selenium
    # 1592, 1037 for 1280, 960
    BALANCE_LTRB = (570, 885, 695, 905)
    BET_LTRB = (765, 885, 840, 905)
    WIN_LTRB = (960, 885, 1045, 905)
    INIT_SIZE = (1920, 1080)
    recognizer = ImageTxtRecogniserCv2()

    def initialize_coordinates(self) -> None:
        super().initialize_coordinates()
        self.logger.info(f'Canvas has properties: {self.coordinates.canvas}')
        self.coordinates.continue_button = self.coordinates.calc_coordinates_button(kx=0.5, ky=0.8)
        self.logger.info(f'Continue button has properties: {self.coordinates.continue_button}')
        self.coordinates.coin_value_add = self.coordinates.calc_coordinates_button(kx=0.196, ky=0.916)
        self.logger.info(f'Coins value add button has properties: {self.coordinates.coin_value_add}')
        self.coordinates.amount_coins_add = self.coordinates.calc_coordinates_button(kx=0.391, ky=0.916)
        self.logger.info(f'Amount coins add button has properties: {self.coordinates.amount_coins_add}')
        self.coordinates.spin = self.coordinates.calc_coordinates_button(kx=0.713, ky=0.916)
        self.logger.info(f'Spin button has properties: {self.coordinates.spin}')
        self.coordinates.balance = self.coordinates.calc_coordinates_image(kx1=0.337, ky1=0.971, kx2=0.425, ky2=0.999)
        self.logger.info(f'Balance image has properties: {self.coordinates.balance}')
        self.coordinates.bet = self.coordinates.calc_coordinates_image(kx1=0.474, ky1=0.971, kx2=0.532, ky2=0.999)
        self.logger.info(f'Bet image has properties: {self.coordinates.bet}')
        self.coordinates.win = self.coordinates.calc_coordinates_image(kx1=0.626, ky1=0.971, kx2=0.688, ky2=0.999)
        self.logger.info(f'Win image has properties: {self.coordinates.bet}')

        self.coordinates.gamble_button = self.coordinates.calc_coordinates_button(kx=0.591, ky=0.911)
        self.logger.info(f'Gamble button has properties: {self.coordinates.gamble_button}')
        self.coordinates.cash_out_button = self.coordinates.calc_coordinates_button(kx=0.835, ky=0.911)
        self.logger.info(f'Cash out button has properties: {self.coordinates.cash_out_button}')
        self.coordinates.red_button = self.coordinates.calc_coordinates_button(kx=0.35, ky=0.45)
        self.logger.info(f'Red button has properties: {self.coordinates.red_button}')
        self.coordinates.black_button = self.coordinates.calc_coordinates_button(kx=0.35, ky=0.55)
        self.logger.info(f'Black button has properties: {self.coordinates.black_button}')
        self.coordinates.hearts_button = self.coordinates.calc_coordinates_button(kx=0.65, ky=0.45)
        self.logger.info(f'Hearts button has properties: {self.coordinates.hearts_button}')
        self.coordinates.diamonds_button = self.coordinates.calc_coordinates_button(kx=0.7, ky=0.45)
        self.logger.info(f'Diamonds button has properties: {self.coordinates.diamonds_button}')
        self.coordinates.clubs_button = self.coordinates.calc_coordinates_button(kx=0.65, ky=0.55)
        self.logger.info(f'Clubs button has properties: {self.coordinates.clubs_button}')
        self.coordinates.spades_button = self.coordinates.calc_coordinates_button(kx=0.7, ky=0.55)
        self.logger.info(f'Spades button has properties: {self.coordinates.spades_button}')
        self.coordinates.speed = self.coordinates.calc_coordinates_button(kx=0.065, ky=0.98)
        self.logger.info(f'Speed button has properties: {self.coordinates.speed}')

    def start_game(self):
        # self.get_page(self.GAMBLE_URL)
        # self.click_start_game()
        time.sleep(30)
        self.initialize_coordinates()
        self.click_continue()
        # n = 2 for first site
        self.click_coin_value_add(n=self.click_coin_add_qty)
        # self.click_amount_coins_add(n=2)
        time.sleep(2)
        self.take_a_screen()
        # self.extract_data_images()
        self.click_speed_button()

    def click_amount_coins_add(self, n: int):
        for _ in range(n):
            self.click_by_coordinates(*self.coordinates.amount_coins_add.values())

    def click_coin_value_add(self, n: int):
        for _ in range(n):
            self.click_by_coordinates(*self.coordinates.coin_value_add.values())

    def extract_data_images(self):
        self.screens.save_crop(*self.coordinates.balance.values(), new_filename='balance.png')
        self.screens.save_crop(*self.coordinates.bet.values(), new_filename='bet.png')
        self.screens.save_crop(*self.coordinates.win.values(), new_filename='win.png')

    def check_bet_max(self):
        new_filename = 'bet_max.png'
        file_path = self.screens.save_crop(
            new_filename=new_filename,
            multiply_to=MultiplyCrop(0.595, 0.72, 0.64, 0.77),
        )
        bet_max_text = self.recognizer.recognize_by_adaptive_threshold(filepath=file_path, adaptive_pity=7)
        print(bet_max_text)
        return bet_max_text

    def check_prev_cards(self):
        new_filename = 'prev_cards.png'
        self.screens.save_crop(
            new_filename=new_filename,
            multiply_to=MultiplyCrop(0.44, 0.55, 0.56, 0.58),
            resize_x=5000, resize_y=400
        )
        prev_cards_text = self.screens.get_text_from_png(new_filename)
        return prev_cards_text.strip()

    def check_win_coins(self):
        new_filename = 'coins.png'
        self.screens.save_crop(
            new_filename=new_filename,
            multiply_to=MultiplyCrop(0.47, 0.68, 0.62, 0.71),
            resize_x=1400, resize_y=100
        )
        return self.screens.get_text_from_png(new_filename)

    def check_gamble_coins(self) -> int:
        res = self.check_win_coins()
        coins = 0
        if 'WIN: ' in res.strip():
            try:
                coins = res.split('WIN: ')[1].split(' ')[0]
                coins = int(coins)
            except Exception as e:
                self.logger.error(e)
                coins = 0
        return coins

    def check_coins(self) -> int:
        self.take_a_screen()
        new_filename = 'coins.png'
        self.screens.save_crop(
            new_filename=new_filename,
            multiply_to=MultiplyCrop(0.47, 0.68, 0.62, 0.71),
            resize_x=2200, resize_y=100
        )
        coins_text = self.screens.get_text_from_png(new_filename)
        coins = 0
        if 'Won ' in coins_text.strip():
            try:
                coins = coins_text.split('Won ')[1].split(' ')[0]
                coins = int(coins)
            except Exception as e:
                self.logger.error(e)
                coins = 0
        return coins

    def check_spin_button(self):
        new_filename = 'spin.png'
        self.screens.save_crop(
            new_filename=new_filename,
            multiply_to=MultiplyCrop(0.66, 0.71, 0.7, 0.76),
            resize_x=500, resize_y=400
        )
        spin_text = self.screens.get_text_from_png(new_filename)
        return re.findall(r"\w+", spin_text.strip())[0]

    def extract_data(self) -> str:
        new_filename = 'result.png'
        self.screens.save_crop(new_filename=new_filename, multiply_to=MultiplyCrop(0.4, 0.77, 0.7, 0.8),
                               resize_x=1400, resize_y=100)
        return self.screens.get_text_from_png('result.png')

    def extract_txt_from_data_images(self) -> Dict[str, str]:
        balance = self.screens.get_text_from_png('balance.png')
        balance = self.search_with_regex(pattern=r'(\d+\.)\d+', s=balance)

        bet = self.screens.get_text_from_png('bet.png')
        bet = self.search_with_regex(pattern=r'(\d+\.)\d+', s=bet)

        win = self.screens.get_text_from_png('win.png')
        win = self.search_with_regex(pattern=r'(\d+\.)\d+', s=win)
        return {
            'Datetime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Balance': balance,
            'Bet': bet,
            'Win': win
        }

    @staticmethod
    def float_format(value):
        if value and len(value) > 1:
            first, second = value[0], value[1]
            if first == '0' and second != '.':
                new_value = first + '.' + value[1:]
            else:
                new_value = value
            return float(new_value)
        return 0.0

    def extract_amounts(self) -> dict:
        res = self.extract_data()
        search_amounts = re.findall(r'(\d+(?:\.\d+)?)', res)
        if not search_amounts:
            self.logger.critical('not found data')
            amounts = [0.0 for _ in range(3)]
        else:
            amounts = [self.float_format(amount) for amount in search_amounts if amount]

        if len(amounts) == 2:
            amounts.append(0.0)

        balance, bet, win = amounts

        return {
            'Datetime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Balance': balance,
            'Bet': bet,
            'Win': win
        }

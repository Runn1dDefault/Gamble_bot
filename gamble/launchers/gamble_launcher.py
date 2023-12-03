import time
from typing import Dict, Any
from decimal import Decimal

from selenium.common.exceptions import NoSuchWindowException

from gamble.games import RichWildeGame, PimpedGame
from gamble.launchers.base import BaseGambleLauncher


class GambleLauncher(BaseGambleLauncher):
    GAMBLE_SITES = {'www.betamo.com': RichWildeGame, 'dunder': PimpedGame}
    wait_time = 0

    _last_result: Dict[str, Any] = None

    def run_game_process(self):
        assert self.game

        super().run_game_process()
        self.make_login()
        self.game.get_page(self.game.GAMBLE_URL)
        self.game.start_game()

        try:
            self.run_game_logic()
        except NoSuchWindowException as e:
            self.stop_game_process('Game stopped by user!')
            self.logger.critical(e)
        except Exception as e:
            self.stop_game_process(str(e))
            self.logger.critical(e)

    def run_game_logic(self):
        self.save_game_log('Start game...')
        stop_reason = 'Game stopped by user!'

        while self.running:
            self.wait()
            self._take_screen()

            # extract BALANCE AND WIN AMOUNT
            game_points = self.game.extract_amounts()
            balance, win_amount = game_points['Balance'], game_points['Win']

            # checking BALANCE
            balance_reason = self._check_balance(balance, win_amount)
            if balance_reason:
                stop_reason = balance_reason
                break

            self._last_result = game_points

            # WIN CASE
            if self.gamble_btn_available():
                if self._win_case_gambled(win_amount, balance) is False:
                    self.__make_spin()

            # LOSE CASE
            else:
                self._lose_case(balance)
                # BONUS CASE
                if self._bonus_case_happened() is False:
                    self.__make_spin()

        self.stop_game_process(reason=stop_reason)
        self.logger.error(stop_reason)

    def __make_spin(self) -> None:
        if not self.spin_btn_available():
            return

        self.game.click_spin_button()
        while not self.spin_btn_available():
            self._take_screen()

    def _bonus_case_happened(self) -> bool:
        win_coins = self.game.check_win_coins().lower()

        if self.WIN_TEXT in win_coins and self.GAMBLE_LIMIT_TEXT not in win_coins:
            self.save_game_log('***BONUS ROUND HAPPENED***')
            self._waiting_for_gamble_button()
            return True
        return False

    def _lose_case(self, balance: float):
        if self._last_result and self._last_result['Balance'] > balance:
            msg = f"LOSE CASE: {self._lose_amount_from_last_result()}"
            self.save_game_log(msg)
            self.logger.debug(msg)

    def _win_case_gambled(self, win_amount: float, balance) -> bool:
        msg = f'Collected WIN CASE: {win_amount} eur'
        self.save_game_log(msg)
        self.logger.debug(msg)

        win_condition = self.ext_value > win_amount >= self.min_gamble_amount

        if win_condition and self._waiting_for_gamble_button():
            self.game.click_gamble_button()

            msg = f'Current win amount is WIN CASE: {win_amount} eur. Will be gambled.'
            self.save_game_log(msg)
            self.logger.debug(msg)

            self.make_gamble_logic(win_amount, balance)
            time.sleep(3)  # important!
            return True

        if win_amount >= self.ext_value:
            self._take_screen()

            if self.gamble_btn_available():
                self.game.click_cash_out_button()

        return False

    def _lose_amount_from_last_result(self) -> Decimal:
        lose_amount = self._last_result['Bet']
        decimal_amount = Decimal(lose_amount)
        format_float = ''.join(['0' for _ in range(len(str(lose_amount).split('.')[0]))]) + '.00'
        return decimal_amount.quantize(Decimal(format_float))

    def _check_balance(self, balance: float, win_amount: float) -> str:
        if balance < self.min_balance_value:
            return f'Your balance is {balance}, should be min {self.min_balance_value} eur'

        if self._balance_reached(balance=balance, win_amount=win_amount):
            return f'Your balance({balance}) reached {self.ext_value} eur. Browser will be closed.'
        return ''

    def _balance_reached(self, balance: float, win_amount: float) -> bool:
        if balance + win_amount >= self.ext_value:

            if win_amount > 0:
                self.game.click_cash_out_button()
            return True

        return False

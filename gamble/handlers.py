import os
import time
from typing import Optional, Union, Tuple
from logging import getLogger
from sys import platform

from PIL import Image

import undetected_chromedriver as uc
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome, ChromeOptions, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from config import BROWSER_NAME, PROXY_ADDRESS, DOWNLOAD_DIR_BROWSER, SCREENS_DIR, WINDOW_SIZE, CHROME_PLUGIN, \
    USE_URBAN, URBAN_PLUGIN
from recogniser.recognisers import TxtRecogniser
from service.utils import get_chromedriver_path, on_set_resolution, configure_logger

from gamble.types import MultiplyCrop


logger = getLogger(__name__)
configure_logger(logger)


class GambleBrowserHandler:
    ACCEPT_COOKIES_BTN: str = ""
    INIT_SIZE: Optional[Tuple[int, int]] = None
    WINDOW_FULL_SIZE: bool = False

    def __init__(self, use_proxy: bool = False, *args, **kwargs):
        self.use_proxy = use_proxy
        self.browser = self.create_web_driver(proxy=self.get_proxy)
        self._window_init_size()

    def create_web_driver(self, proxy: str = "") -> Chrome:
        browser = self._create_local_machine_web_driver(proxy=proxy)
        return browser

    @property
    def get_proxy(self):
        return PROXY_ADDRESS if self.use_proxy else ''

    def _window_init_size(self):
        if self.INIT_SIZE and (platform == "win64" or platform == "win32"):
            on_set_resolution(*self.INIT_SIZE)

        if not self.WINDOW_FULL_SIZE:
            self.browser.set_window_size(*WINDOW_SIZE)

    def _create_local_machine_web_driver(self, proxy: str = '') -> Chrome:
        if BROWSER_NAME == "chrome":
            chrome_options = self._chrome_options(proxy=proxy)
            # chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

            if self.WINDOW_FULL_SIZE:
                chrome_options.add_argument("--start-maximized")
            # service = Service(ChromeDriverManager().install())
            driver_path = get_chromedriver_path()
            driver = uc.Chrome(options=chrome_options, use_subprocess=True)
            return driver

    @staticmethod
    def _chrome_options(proxy: str = "") -> Optional[ChromeOptions]:
        # Chrome options
        chrome_prefs = {
            "download.default_directory": DOWNLOAD_DIR_BROWSER,
            "download.directory_upgrade": "true",
            "download.prompt_for_download": "false",
            "disable-popup-blocking": "true",
        }
        chrome_options = uc.ChromeOptions()
        # chrome_options.add_experimental_option("prefs", chrome_prefs)
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument("--disable-infobars")
        # chrome_options.add_argument("--incognito")

        if USE_URBAN:
            chrome_options.add_extension(URBAN_PLUGIN)

        elif proxy:
            # chrome_options.add_extension("./Proxy-Auto-Auth_v2.0.crx")
            # chrome_options.add_extension(CHROME_PLUGIN)
            chrome_options.add_argument(f'--proxy-server={proxy}')

        if BROWSER_NAME == "chrome":
            return chrome_options

    def get_page(self, url: str) -> bool:
        self.browser.get(url)
        time.sleep(10)
        self.accept_cookies()
        return True

    def accept_cookies(self) -> None:
        check_xpath = (By.XPATH, self.ACCEPT_COOKIES_BTN) if self.ACCEPT_COOKIES_BTN else (By.ID, "ok_cookie_button")
        cookie_button = WebDriverWait(self.browser, 10).until(
            ec.element_to_be_clickable(check_xpath)
        )
        cookie_button.click()
        logger.info('CLICK ACCEPT COOKIES')

    def alert_message(self, msg: str):
        self.browser.execute_script(f'alert("{msg}");')
        logger.error(msg)

    def click_by_coordinates(self, x: int, y: int):
        ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=y).click().perform()
        ActionChains(self.browser).move_by_offset(xoffset=-x, yoffset=-y).perform()

    def find_element_or_none(self, search_by: str, is_id: bool = False) -> Optional[WebElement]:
        try:
            return self.browser.find_element(by=By.ID if is_id else By.XPATH, value=search_by)
        except NoSuchElementException:
            pass


class ScreenshotHandler:
    MAIN_SCREEN_FILENAME: str = 'screenshot.png'
    txt_recogniser = TxtRecogniser()

    def __init__(self, dir_name: str, browser: Chrome, element_xpath: str = None):
        self.directory_name = dir_name
        self.browser = browser
        self.element_xpath = element_xpath

    @property
    def _make_screenshots_dir(self) -> str:
        path = os.path.join(SCREENS_DIR, self.directory_name)

        if not os.path.exists(path):
            os.mkdir(path)

        return path

    @property
    def main_screen_path(self):
        return os.path.join(self._make_screenshots_dir, self.MAIN_SCREEN_FILENAME)

    def save_screenshot(self, filename: str = '') -> None:
        if filename == '':
            filename = self.MAIN_SCREEN_FILENAME

        fullname = os.path.join(self._make_screenshots_dir, filename)
        if self.element_xpath:
            element = WebDriverWait(self.browser, 10).until(
                ec.presence_of_element_located((By.XPATH, self.element_xpath)),
            )
            if element is not None:
                element.screenshot(fullname)
            else:
                logger.error('Element xpath not found {}'.format(self.element_xpath))

        else:
            self.browser.save_screenshot(fullname)

        logger.info(f'SAVED SCREENSHOT TO FILE {self.directory_name}/{filename}')

    def save_crop(self, new_filename: str, multiply_to: MultiplyCrop, resize_x: Optional[int] = None,
                  resize_y: Optional[int] = None) -> Union[str, os.PathLike]:
        new_file_path = os.path.join(self._make_screenshots_dir, new_filename)
        original = Image.open(self.main_screen_path)

        # cropping original img and saving to new image
        width, height = original.size
        cropped_image = original.crop((multiply_to.MULTIPLY_TO_LEFT * width, multiply_to.MULTIPLY_TO_UP * height,
                                       multiply_to.MULTIPLY_TO_RIGHT * width, multiply_to.MULTIPLY_TO_DOWN * height))
        cropped_image.save(new_file_path)

        original = Image.open(new_file_path)

        if resize_x is not None and resize_y is not None:
            original = original.resize((resize_x, resize_y), Image.ANTIALIAS)

        original.save(new_file_path)
        return new_file_path

    def get_text_from_png(self, filename: str) -> str:
        png_path = self.get_file_path(filename)
        result = self.txt_recogniser.image_to_txt_recognise(png_path)
        return result.replace('♀', '')

    def get_file_path(self, filename: str):
        png_path = os.path.join(self._make_screenshots_dir, filename)

        if not os.path.exists(png_path):
            raise FileExistsError(f'Not found png file with path {png_path}')

        return png_path


class GambleCanvasCoordinates:
    def __init__(self, canvas_xpath: str, browser: Chrome):
        self.browser = browser
        self.canvas_xpath = canvas_xpath
        self.canvas = {'x': 0, 'y': 0, 'height': 0, 'width': 0}
        self.continue_button = {'x': 0, 'y': 0}
        self.coin_value_add = {'x': 0, 'y': 0}
        self.amount_coins_add = {'x': 0, 'y': 0}
        self.spin = {'x': 0, 'y': 0}
        self.gamble_button = {'x': 0, 'y': 0}
        self.cash_out_button = {'x': 0, 'y': 0}
        self.red_button = {'x': 0, 'y': 0}
        self.black_button = {'x': 0, 'y': 0}
        self.hearts_button = {'x': 0, 'y': 0}
        self.diamonds_button = {'x': 0, 'y': 0}
        self.clubs_button = {'x': 0, 'y': 0}
        self.spades_button = {'x': 0, 'y': 0}
        self.balance = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}
        self.bet = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}
        self.win = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}
        self.speed = {'x': 0, 'y': 0}
        self.msg_cancel_btn = {'x': 0, 'y': 0}

    def init_canvas(self) -> None:
        try:
            self.canvas['x'] = self.browser.find_element(by=By.XPATH, value=self.canvas_xpath).location['x']
            self.canvas['y'] = self.browser.find_element(by=By.XPATH, value=self.canvas_xpath).location['y']
        except NoSuchElementException:
            self.canvas['x'] = 0
            self.canvas['y'] = 0

        self.canvas['height'] = self.browser.find_element(by=By.XPATH, value=self.canvas_xpath).size['height']
        self.canvas['width'] = self.browser.find_element(by=By.XPATH, value=self.canvas_xpath).size['width']

    def calc_coordinates_button(self, kx: float, ky: float) -> dict:
        return {'x': self.canvas['x'] + int(kx * self.canvas['width']),
                'y': self.canvas['y'] + int(ky * self.canvas['height'])}

    def calc_coordinates_image(self, kx1: float, ky1: float, kx2: float, ky2: float) -> dict:
        # Scaling coefficient print screen relative to the screen resolution
        scale_print_screen = 1.291
        return {
            'x1': self.canvas['x'] + int(kx1 * self.canvas['width'] * scale_print_screen),
            'y1': self.canvas['y'] + int(ky1 * self.canvas['height'] * scale_print_screen),
            'x2': self.canvas['x'] + int(kx2 * self.canvas['width'] * scale_print_screen),
            'y2': self.canvas['y'] + int(ky2 * self.canvas['height'] * scale_print_screen),
        }

    def print_properties_of_elem(self, xpath: str):
        el = self.browser.find_element(by=By.XPATH, value=xpath)
        logger.debug(el.location)
        logger.debug(el.size)

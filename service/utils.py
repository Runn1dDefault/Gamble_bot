import logging
import os
import re
import time
from sys import platform as _platform
from typing import Any, Dict, List

from config import LOG_LEVEL, LOG_FORMAT, LOG_FILENAME, BASE_DIR, CONSOLE_LOG


def validate_str_digit(value: str) -> str:
    digit = re.sub(r'\W+', '.', value.strip())
    symbols_count = digit.count('.')
    return digit.replace('.', '', symbols_count - 1)


def wait_sometimes(func):
    def wait(*args, **kwargs):
        result = func(*args, **kwargs)
        time.sleep(15)
        return result
    return wait


def configure_logger(logger: logging.Logger):
    logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(LOG_FORMAT)

    file = logging.FileHandler(LOG_FILENAME)
    file.setFormatter(formatter)
    logger.addHandler(file)

    if CONSOLE_LOG:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)


def rebuild_site_dict_structure(site_list):
    sites_data = dict()

    for site in site_list:
        site_data = dict(
            address=site['address']
        )

        if not site.get('country_option'):
            site_data['min_balance'] = 0.0
            site_data['min_check'] = 0.0
            site_data['target_balance'] = 0.0
            site_data['link_game'] = None
        else:
            country = site['country_option'][0]
            site_data['min_balance'] = float(country['min_balance'])
            site_data['min_check'] = float(country['min_check'])
            site_data['target_balance'] = float(country['target_balance'])
            site_data['link_game'] = country.get('link_game')
            site_data['coin_clicks'] = country.get('coin_clicks', 3)

        sites_data[site['name']] = site_data
    return sites_data


def on_set_resolution(width: int, height: int):
    import pywintypes
    import win32api
    import win32con

    # adapted from Peter Wood: https://stackoverflow.com/a/54262365
    devmode = pywintypes.DEVMODEType()
    devmode.PelsWidth = width
    devmode.PelsHeight = height

    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

    win32api.ChangeDisplaySettings(devmode, 0)


def get_registration_data(betsite_name: str, registrations: List[Dict[str, Any]]) -> Dict[str, Any]:
    for registration in registrations:
        betsite = registration.get('betsite')
        if betsite and betsite.get('name') == betsite_name:
            return registration


def get_site_names(site_list: list):
    site_names = []
    for site in site_list:
        site_names.append(site['name'])
    return site_names


def create_folder_for_file(full_path: str):
    folder = os.path.dirname(full_path)
    access_rights = 0o755
    try:
        if not os.path.exists(folder):
            os.makedirs(folder, access_rights)
    except OSError:
        pass
        # self._logger.error("Create directory %s failed" % folder)
    else:
        pass
        # self._logger.info(f"Directory {folder} successfully created")


def get_chromedriver_path() -> str:
    if _platform == "win64" or _platform == "win32":
        driver_path = os.path.join(BASE_DIR, 'driver', 'chromedriver.exe')
    elif _platform == "linux" or _platform == "linux2":
        driver_path = os.path.join(BASE_DIR, 'driver', 'chromedriver')
    elif _platform == "darwin":
        driver_path = os.path.join(BASE_DIR, 'driver', 'chromedriver')
    else:
        driver_path = ''
    return driver_path


def value_in_list(value: str, check_list: List[str]) -> bool:
    for expected_value in check_list:
        if value and expected_value.lower() in value.lower():
            return True
    return False

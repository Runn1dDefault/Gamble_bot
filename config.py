import os
import logging
import sys
from pathlib import Path
from sys import platform as _platform
from urllib.parse import urljoin


if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = Path(__file__).resolve().parent


TEMP_PATH = os.path.join(BASE_DIR, 'temp')
if not os.path.exists(TEMP_PATH):
    os.mkdir(TEMP_PATH)
    
SCREENS_DIR = os.path.join(TEMP_PATH, 'screens')
if not os.path.exists(SCREENS_DIR):
    os.mkdir(SCREENS_DIR)


if _platform == "linux" or _platform == "linux2":
    # linux
    TESSERACT_PATH = '/usr/bin/tesseract'

    if not os.path.exists(TESSERACT_PATH):
        TESSERACT_PATH = '/usr/span/tesseract'

    if not os.path.exists(TESSERACT_PATH):
        tesseract_url = 'https://tesseract-ocr.github.io/tessdoc/Installation.html'
        raise FileNotFoundError('Not found tesseract please see: {}'.format(tesseract_url))

    # info: for error like this "Error opening data file /usr/share/tesseract-oct/5/tessdata/eng.traineddata"
    # use command -> chmod u=rwx,g=rwx,o=rwx /usr/share/tesseract-oct/5/tessdata/eng.traineddata
elif _platform == "darwin":
    TESSERACT_PATH = os.path.join(BASE_DIR, 'tesseract', '5.0.1', 'bin', 'tesseract')
else:
    TESSERACT_PATH = os.path.join(BASE_DIR, 'tesseract', 'Tesseract-OCR', 'tesseract.exe')


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s: %(message)s'


if os.name == 'nt':
    LOG_FILENAME = 'log.out'
elif _platform == "linux" or _platform == "linux2" or _platform == "darwin":
    LOG_FILENAME = os.path.join(TEMP_PATH, 'log.out')
else:
    raise Exception(f'Unknown OS {os.name}')

PLUGINS_DIR = os.path.join(TEMP_PATH, 'plugins')
# logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, filename=LOG_FILENAME)

PYTESSERACT_CUSTOM_CONFIG = r'-l eng --psm 6'
# BROWSER CONFIG
BROWSER_NAME = 'chrome'
CHROMEDRIVER_DOWNLOADS_URL = 'https://chromedriver.chromium.org/downloads'
WINDOW_SIZE = (1350, 768)
PROXY_ADDRESS = 'http://5.189.151.227:24110'
CHROME_PLUGIN = os.path.join(PLUGINS_DIR, 'proxy_auth_plugin.zip')
URBAN_PLUGIN = os.path.join(PLUGINS_DIR, 'Urban_VPN.crx')
DOWNLOAD_DIR_BROWSER = os.path.abspath("files")

# API CONFIG
API_URL = 'http://185.151.31.66:8009/'
API_LOGS_URL = urljoin(API_URL, '/api/logs/')
API_ERROR_STATUSES = (204, 400, 404, 401, 412, 500, 512, 521, 503, 403)

CONSOLE_LOG = True
USE_URBAN = False
USE_PROXY = False
API_LOG_INCLUDE = True

ABBYY_APPID = '07f69397-f946-46a7-812d-353ec5ae30bf'
ABBYY_PWD = 'pCA1vpqef9dQh1vCAUZPsWXT'
# 'http': '154.3.106.153:51681', 'https' : '154.3.106.153:51681'
ABBYY_PROXY = {}

ICON_PATH = os.path.join(TEMP_PATH, 'icons/gambling.ico')

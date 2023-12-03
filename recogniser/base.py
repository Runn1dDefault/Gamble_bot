from pytesseract import pytesseract

from config import TESSERACT_PATH, PYTESSERACT_CUSTOM_CONFIG


class BaseTxtRecogniser:
    def __init__(self):
        pytesseract.tesseract_cmd = TESSERACT_PATH
        self.pytesseract_config = PYTESSERACT_CUSTOM_CONFIG

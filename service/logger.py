import logging

from config import LOG_LEVEL, LOG_FORMAT, LOG_FILENAME, CONSOLE_LOG


class Logger(logging.Logger):

    def __init__(self, name: str):
        super().__init__(name, level=LOG_LEVEL)
        
        formatter = logging.Formatter(LOG_FORMAT)

        if CONSOLE_LOG:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.addHandler(console_handler)
        else:
            file_handler = logging.FileHandler(LOG_FILENAME)
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)

from tkinter import Frame, Tk
from logging import getLogger

from service.utils import configure_logger


class BaseFrame(Frame):
    def __init__(self, master: Tk):
        super().__init__(master=master)
        self.root = master
        self.logger = getLogger(self.__class__.__name__)
        configure_logger(self.logger)

    def setup(self) -> None:
        pass

from typing import NamedTuple, Union


class MultiplyCrop(NamedTuple):
    MULTIPLY_TO_LEFT: Union[int, float]
    MULTIPLY_TO_UP: Union[int, float]
    MULTIPLY_TO_RIGHT: Union[int, float]
    MULTIPLY_TO_DOWN: Union[int, float]

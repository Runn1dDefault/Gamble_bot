import os
import csv
from typing import Union

from config import TEMP_PATH


def save_row(data: Union[dict, str]):
    filename = 'gamble_results.csv'
    filepath = os.path.join(TEMP_PATH, filename)

    file_exist = os.path.isfile(path=filepath)
    type_open = 'a' if file_exist else 'w'

    with open(filepath, type_open) as csvfile:
        fieldnames = ['Datetime', 'Balance', 'Bet', 'Win']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exist:
            writer.writeheader()

        writer.writerow(data)

from collections import OrderedDict
from typing import List, Tuple, Optional

import numpy

from service.utils import value_in_list

from recogniser.image_recognisers import ImageTxtRecogniserPillow, ImageTxtRecogniserCv2
from service.logger import Logger


class TxtRecogniser:
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self.pillow_recognizer = ImageTxtRecogniserPillow()
        self.cv2_recognizer = ImageTxtRecogniserCv2()

    @property
    def methods_by_filters(self) -> OrderedDict:
        return OrderedDict(
            cv2_adaptive_thresholding=self.cv2_adaptive_threshold,
            cv2_original=self.cv2_recognizer.recognize_original,
            cv2_thresholding=self.cv2_recognizer.recognize_by_threshold,
            pillow_original=self.pillow_recognizer.recognize_original
        )

    def image_to_txt_recognise(self, filepath: str) -> str:
        return self.pillow_recognizer.recognize_original(filepath=filepath)

    def cv2_adaptive_threshold(self, filepath: str, expected_values: List[str],
                               adaptive_pity: int = None) -> Tuple[str, int]:
        if adaptive_pity:
            adaptive_threshold_img = self.cv2_recognizer.recognize_by_adaptive_threshold(
                filepath=filepath, adaptive_pity=adaptive_pity
            )

            if value_in_list(adaptive_threshold_img, check_list=expected_values):
                return adaptive_threshold_img, adaptive_pity

        for value in numpy.arange(1, 20, 0.1):
            adaptive_value = round(value, 2)
            adaptive_threshold_result = self.cv2_recognizer.recognize_by_adaptive_threshold(
                filepath=filepath, adaptive_pity=adaptive_value
            )

            if value_in_list(adaptive_threshold_result, check_list=expected_values):
                return adaptive_threshold_result, adaptive_value

        return '', 0

    def recognise_with_all_methods(self, filepath: str, expected_values: List[str]) -> Tuple[Optional[str], str]:
        for filter_name, method in self.methods_by_filters.items():
            check_in = False
            method_kwargs = dict(filepath=filepath)

            if filter_name == 'cv2_adaptive_thresholding':
                method_kwargs['expected_values'] = expected_values
                result, pity_value = method(**method_kwargs)
                if pity_value == 0:
                    continue
            else:
                result = method(**method_kwargs)
                check_in = True

            if result and check_in:
                if value_in_list(result, check_list=expected_values):
                    return filter_name, result

            if result:
                return filter_name, result

        return None, ''


class TxtRecognizerByLast(TxtRecogniser):
    def __init__(self):
        super().__init__()
        self._recognize_key: Optional[str] = None
        self._saved_methods = dict()
        self._saved_adaptive_pities = dict()
        self._save_pillow_resizes = dict()

    def _save_adaptive_pity(self, pity_value: int) -> None:
        self._saved_adaptive_pities[self._recognize_key] = pity_value
        self.logger.debug('Save adaptive pity value {} with key {}'.format(pity_value, self._recognize_key))

    def _save_success_method(self, filter_name: str) -> None:
        method = self.methods_by_filters.get(filter_name)

        if method:
            self._saved_methods[self._recognize_key] = method
            self.logger.debug(
                'Save success method!\nFilter name: {}\nKey: {}'.format(filter_name or 'Pillow', self._recognize_key)
            )

    def resizes_by_last_success(self, filepath: str, resizes: List[Tuple[int, int]],
                                expected_values: List[str]):
        assert expected_values
        self._recognize_key = str(expected_values)

        saved_resizes = self._save_pillow_resizes.get(self._recognize_key)
        if saved_resizes:
            saved_resizes_generator = self.pillow_recognizer.recognize_by_resizes(filepath=filepath,
                                                                                  resizes=[saved_resizes])

            for result_txt, resize_x, resize_y in saved_resizes_generator:

                if value_in_list(result_txt, check_list=expected_values):
                    return result_txt

        resize_generator = self.pillow_recognizer.recognize_by_resizes(filepath=filepath, resizes=resizes)

        for result_txt, resize_x, resize_y in resize_generator:

            if value_in_list(result_txt, check_list=expected_values):
                self._save_pillow_resizes[self._recognize_key] = (resize_x, resize_y)
                return result_txt

    def cv2_adaptive_threshold(self, filepath: str, expected_values: List[str],
                               adaptive_pity: int = None) -> Tuple[str, int]:
        assert expected_values
        self._recognize_key = str(expected_values)

        adaptive_value = adaptive_pity if adaptive_pity else self._saved_adaptive_pities.get(self._recognize_key)

        result, pity = super().cv2_adaptive_threshold(filepath=filepath, expected_values=expected_values,
                                                      adaptive_pity=adaptive_value)

        if result and pity != adaptive_value:
            self._save_adaptive_pity(pity)

        return result, pity

    def recognise_with_all_methods(self, filepath: str, expected_values: List[str]) -> Tuple[Optional[str], str]:
        assert expected_values
        self._recognize_key = str(expected_values)

        filter_name, result = super().recognise_with_all_methods(filepath=filepath, expected_values=expected_values)

        if result:
            self._save_success_method(filter_name)

        return filter_name, result

    def recognize_by_last_method(self, filepath: str, expected_values: List[str]) -> str:
        assert expected_values
        self._recognize_key = str(expected_values)

        method = self._saved_methods.get(self._recognize_key)
        if method:
            method_name = method.__name__

            self.logger.debug('Trying recognize text from png with last success method {}...'.format(method_name))

            if method_name == 'cv2_adaptive_threshold':
                result, _ = method(filepath=filepath, expected_values=expected_values)
            else:
                result = method(filepath=filepath)

            if result:
                return result

        _, result = self.recognise_with_all_methods(filepath=filepath, expected_values=expected_values)
        return result


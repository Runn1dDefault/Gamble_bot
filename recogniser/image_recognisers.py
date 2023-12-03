import os
from typing import List, Dict, Tuple, Iterator

from PIL import Image
from pytesseract import image_to_string

from recogniser.base import BaseTxtRecogniser
from recogniser.image_handlers import ImageHandlerPillow, ImageHandlerCv2


class ImageTxtRecogniserPillow(BaseTxtRecogniser):
    pillow_handler_cls = ImageHandlerPillow

    def recognize_original(self, filepath: str) -> str:
        img = self.pillow_handler_cls(filepath=filepath).img
        txt = image_to_string(img, config=self.pytesseract_config)
        return txt

    def recognize_by_resizes(self, filepath: str, resizes: List[Tuple[int, int]]) -> Iterator[Tuple[str, int, int]]:
        assert resizes
        img = self.pillow_handler_cls(filepath=filepath).img

        for resize_x, resize_y in resizes:
            resized_img = img.resize((resize_x, resize_y), Image.ANTIALIAS)
            yield image_to_string(resized_img, config=self.pytesseract_config), resize_x, resize_y

    def to_txt_by_filters(self, filepath: str, red_rgba: List[int] = None, green_rgba: List[int] = None,
                          blue_rgba: List[int] = None) -> Dict[str, str]:

        checked_images_results = dict()
        original_img_handler = self.pillow_handler_cls(filepath=filepath)
        original_img = original_img_handler.img
        checked_images_results['original'] = original_img
        checked_images_results['put_alpha'] = original_img_handler.image_to_put_alpha(300)

        checked_images_results['original_blurred'] = original_img_handler.image_enhance(0.05)
        original_sharpened = original_img_handler.image_enhance(1.9)
        checked_images_results['original_sharpened'] = original_sharpened

        if red_rgba and green_rgba and blue_rgba:
            transparent_img = original_img_handler.transparent(red_rgba, green_rgba, blue_rgba,
                                                               include_background=False)
            checked_images_results['transparent'] = transparent_img

            transparent_img_handler = self.pillow_handler_cls(img=transparent_img)
            checked_images_results['transparent_put_alpha'] = transparent_img_handler.image_to_put_alpha(300)

            transparent_blurred = transparent_img_handler.image_enhance(0.05)
            transparent_sharpened = transparent_img_handler.image_enhance(1.9)
            checked_images_results['transparent_blurred'] = transparent_blurred
            checked_images_results['transparent_sharpened'] = transparent_sharpened

        sharpened_img_handler = self.pillow_handler_cls(img=original_sharpened)
        checked_images_results['sharpened_put_alpha'] = sharpened_img_handler.image_to_put_alpha(300)

        if red_rgba and green_rgba and blue_rgba:
            sharpened_transparent = sharpened_img_handler.transparent(red_rgba=red_rgba, green_rgba=green_rgba,
                                                                      blue_rgba=blue_rgba, include_background=False)
            checked_images_results['sharpened_transparent'] = sharpened_transparent

        sharpened_blurred = sharpened_img_handler.image_enhance(0.05)
        sharpened_double = sharpened_img_handler.image_enhance(1.9)

        checked_images_results['sharpened_blurred'] = sharpened_blurred
        checked_images_results['sharpened_double'] = sharpened_double

        results = dict()
        for checking_name, img in checked_images_results.items():
            txt = image_to_string(img, config=self.pytesseract_config)
            results[checking_name] = txt if txt else None
        return results

    def transparent_image_to_txt(self, filepath: str, red_rgba: List[int], green_rgba: List[int], blue_rgba: List[int],
                                 include_background: bool = True) -> str:
        img_handler = self.pillow_handler_cls(filepath=filepath)
        filename = os.path.basename(filepath)
        save_filepath = filepath.replace(filename, 'transparent_' + filename)
        img = img_handler.transparent(red_rgba, green_rgba, blue_rgba,
                                      save_filepath=save_filepath,
                                      include_background=include_background)
        return image_to_string(img, config=self.pytesseract_config)


class ImageTxtRecogniserCv2(BaseTxtRecogniser):
    cv2_handler_cls = ImageHandlerCv2

    def recognize_original(self, filepath: str) -> str:
        img = self.cv2_handler_cls(filepath=filepath).img
        txt = image_to_string(img, config=self.pytesseract_config)
        return txt

    def recognize_by_adaptive_threshold(self, filepath: str, adaptive_pity: int = 2):
        img_handler = self.cv2_handler_cls(filepath=filepath)
        img_handler.img = img_handler.get_grayscale()
        img_handler.img = img_handler.adaptive_thresholding(adaptive_pity)
        filename = os.path.basename(filepath)
        save_filepath = filepath.replace(filename, 'adaptive_threshold_' + filename)
        img_handler.save(save_filepath)
        return image_to_string(img_handler.img, config=self.pytesseract_config)

    def save_grayscale(self, filepath: str):
        img_handler = self.cv2_handler_cls(filepath=filepath)
        img_handler.img = img_handler.get_grayscale()
        img_handler.save(filepath=filepath)

    def recognize_by_threshold(self, filepath: str):
        img_handler = self.cv2_handler_cls(filepath=filepath)
        img_handler.img = img_handler.get_grayscale()
        img_handler.img = img_handler.thresholding()
        filename = os.path.basename(filepath)
        save_filepath = filepath.replace(filename, 'adaptive_threshold_' + filename)
        img_handler.save(save_filepath)
        return image_to_string(img_handler.img, config=self.pytesseract_config)

from typing import List, Union

import cv2
import numpy as np

try:
    from PIL import Image
except ImportError:
    import Image
from PIL import ImageEnhance


class ImageHandlerPillow:
    def __init__(self, img=None, filepath: str = None):
        assert img or filepath

        self.img = img if img else Image.open(filepath)

    def image_to_put_alpha(self, value: Union[int, float]):
        img_rgba = self.img.copy()
        img_rgba.putalpha(value)
        return img_rgba

    def transparent(self, red_rgba: List[int], green_rgba: List[int], blue_rgba: List[int],
                    include_background: bool = True, save_filepath: str = None):
        rgba = self.img.convert("RGBA")
        datas = rgba.getdata()
        new_data = []
        for item in datas:
            if item[0] in red_rgba and item[1] in green_rgba and item[2] in blue_rgba:
                new_data.append((255, 255, 255, 0))
            else:
                if include_background:
                    new_data.append(item)
                else:
                    new_data.append((0, 0, 0))
        if new_data:
            rgba.putdata(new_data)
        if save_filepath:
            rgba.save(save_filepath, "PNG")
        return rgba

    def image_enhance(self, enhance_value: Union[float, int]):
        enhancer = ImageEnhance.Sharpness(self.img)
        return enhancer.enhance(enhance_value)


class ImageHandlerCv2:
    def __init__(self, filepath: str):
        self.img = cv2.imread(filepath)
        self.original = self.img.copy()

    def get_grayscale(self):
        return cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

    def remove_noise(self):
        return cv2.medianBlur(self.img, 3)

    def thresholding(self):
        ret, th = cv2.threshold(self.img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return th

    def adaptive_thresholding(self, adaptive_pity: int):
        return cv2.adaptiveThreshold(self.img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, adaptive_pity)

    def dilate(self):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.dilate(self.img, kernel, iterations=1)

    def erode(self):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.erode(self.img, kernel, iterations=1)

    def opening(self):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(self.img, cv2.MORPH_OPEN, kernel)

    def canny(self):
        return cv2.Canny(self.img, 100, 200)

    def deskew(self):
        coords = np.column_stack(np.where(self.img > 0))
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        h, w = self.img.shape[:2]
        center = (w // 2, h // 2)
        return cv2.warpAffine(self.img, cv2.getRotationMatrix2D(center, angle, 1.0),
                              (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    def match_template(self, template):
        return cv2.matchTemplate(self.img, template, cv2.TM_CCOEFF_NORMED)

    def save(self, filepath: str):
        cv2.imwrite(filepath, self.img)

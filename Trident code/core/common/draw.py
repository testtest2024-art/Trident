import base64
import io
import os
import tempfile
from typing import List

from PIL import ImageDraw, ImageFont
from PIL.Image import Image

from core.model.step import ElementProxy


class DrawUtils:
    @staticmethod
    def crop_element_in_image(image: Image, x, y, width, height):
        """
        
        """
        crop_im = image.crop((x, y, width, height))

        return crop_im

    @staticmethod
    def draw_element_in_image(image: Image, x, y, width, height):
        """
        
        :params is_labeling:
        """
        draw = ImageDraw.Draw(image)

        draw.rectangle((x, y, x + width, y + height), outline="red", width=3)

        return image

    @staticmethod
    def label_element_in_image(image: Image, element_list: List[ElementProxy], scale=1):
        """
        
        :param scale: 
        """

        draw = ImageDraw.Draw(image)

        font = ImageFont.load_default(size=40)

        for index, element in enumerate(element_list):
            x = element.x
            y = element.y
            width = element.width
            height = element.height
            label_text = str(index + 1)

            # cropped_img = image.crop((x, y, x + width, y + height))
            #
            # 
            # buffer = io.BytesIO()
            # cropped_img.save(buffer, format='PNG')
            # img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            # if not element.text:
            #     element.img = img_base64

            # if x == 0 or y == 0:
            #     continue

            if element.clickable:
                draw.rectangle((x, y, x + width, y + height), outline="red", width=3)
                draw.rectangle((x, y - 50, (x + 60), y), fill="gray")
                # 
                draw.text(xy=(x + 5, y - 50), text=label_text, fill="white", font=font)
            if element.inputable:
                draw.rectangle((x, y, x + width, y + height), outline="yellow", width=3)
                draw.rectangle((x, y, (x + 50), (y + 50)), fill="gray")
                # 
                draw.text(xy=(x + 5, y + 5), text=label_text, fill="red", font=font)

        return image

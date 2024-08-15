import json
from typing import Dict, List


class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    def __repr__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)


class ElementProxy:
    def __init__(self, text, clickable, inputable, x, y, width, height, img: str = ""):
        self.text: str = text

        self.clickable: bool = clickable
        self.inputable: bool = inputable

        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height

        self.img: str = img

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    def __repr__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)


class Step:
    def __init__(self, operate: str, params: Dict, element: ElementProxy or Dict):
        self.operate: str = operate
        self.params: Dict = params
        self.element: ElementProxy = element
        # if isinstance(element, Dict):
        #     self.element: Element = Element(**element)
        # else:
        #     self.element: Element = element

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

import time
from uiautomator2.xpath import XPathSelector

from core.model.device import ElementOperate, check_element_exist
from core.model.step import Rect


class AndroidElement(ElementOperate):

    def __init__(self, element: XPathSelector, session, timeout: int = 3):
        self.element: XPathSelector = element
        self.session = session
        self.timeout = timeout

    def get_element_clickable_parent(self):
        element = self.element.elem
        while True:
            if element.attrib.get("clickable") == "true":
                return element
            # 
            if len(element.xpath("./parent::*")) == 0:
                return self.element.elem
            # 
            element = element.xpath("./parent::*")[0]

    @check_element_exist
    def click(self) -> None:
        self.element.click()

    def assert_exist(self) -> None:
        if not self.exist():
            raise AssertionError()

    def exist(self) -> bool:
        start_time = time.time()
        while time.time() - start_time <= self.timeout:
            if self.element.exists:
                return True

        return False

    @check_element_exist
    def get_rect(self):
        rect = self.element.get().rect
        return Rect(x=rect[0], y=rect[1], width=rect[2], height=rect[3])

    @check_element_exist
    def get_bounds_center(self):
        return list(self.element.get().center())

    @check_element_exist
    def screenshot(self):
        return self.element.screenshot()

    @check_element_exist
    def draw_in_screenshot(self) -> None:
        pass

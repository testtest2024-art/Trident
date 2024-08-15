import os

import adbutils
import requests
import subprocess
import re
from typing import List

from lxml import etree
from uiautomator2 import Device

from core.android.element import AndroidElement
from core.common.draw import DrawUtils
from typing import Optional
from uiautomator2 import ConnectError

from core.model.step import ElementProxy


class AndroidDevice(Device):
    def __init__(self, addr):
        """
        
        :param addr: "10.0.0.1:7912" or "http://10.0.0.1:7912"
        """
        super(AndroidDevice, self).__init__(addr)
        # try:
        #     self.dump_hierarchy()
        # except Exception as e:
        #     self._adb_device.uninstall("com.github.uiautomator")
        #     self.reset_uiautomator()
        self.screen_on()
        self.webview = None

    def send_keys(self, value: str):
        # 
        if value.encode("unicode_escape").decode() == r"\ue007":
            self.send_action("search")
            return

        super().send_keys(value)

    def find_element_by_xpath(self, xpath, timeout=3) -> AndroidElement:
        element = self.xpath(xpath)
        return AndroidElement(element, session=self, timeout=3)

    def find_element_by_text(self, text, timeout=3) -> AndroidElement:
        return self.find_element_by_xpath(
            f"//*[@text='{text}' or @content-desc='{text}' or @resource-id='{text}']",
            timeout=timeout,
        )

    def assert_exist_more(self, exist_value_list, exist_type):
        return True

    def go_to_schema(self, schema):
        self.shell(f"am start {schema}")

    def assert_exist(self):
        return True

    def back(self):
        self.press("back")

    def swipe_up(self, duration=0.1):
        w, h = self.window_size()
        self.swipe(w * 0.5, h * 0.6, w * 0.5, h * 0.3, duration=duration)

    def swipe_down(self, duration=0.1):
        w, h = self.window_size()
        self.swipe(w * 0.5, h * 0.3, w * 0.5, h * 0.6, duration=duration)

    def hierarchy_to_element(self) -> List[ElementProxy]:
        """
        Android Native
        :return:
        """

        def get_sub_text(element: etree._Element):
            text = ""
            for sub_element in element.getchildren():
                if sub_element.attrib.get("class") != "android.widget.Image":
                    text += sub_element.attrib.get("text") or sub_element.attrib.get(
                        "content-desc"
                    )
                    text += get_sub_text(sub_element)
            return text

        # print(self.device.shell('uiautomator dump --compressed /data/local/tmp/uidump.xml && echo success'))
        hierarchy = self.dump_hierarchy()  # 

        # 
        tree = etree.ElementTree(etree.fromstring(hierarchy.encode()))

        # 
        root = tree.getroot()

        virtual_element_list = []

        current_package = self.app_current().get("package")
        for element in root.iter():
            element: etree._Element

            if (
                not element.attrib.get("bounds")
                or element.attrib.get("package") != current_package
            ):
                continue

            # 
            pattern = r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]"
            matches = re.match(pattern, element.attrib.get("bounds", "[][]"))
            position = [int(num) for num in matches.groups()]

            if (
                element.attrib.get("clickable") == "true"
                or element.attrib.get("class") == "android.widget.EditText"
            ):
                # print(element.attrib)
                virtual_element_list.append(
                    ElementProxy(
                        text=element.attrib.get("text")
                        or element.attrib.get("content-desc")
                        or get_sub_text(element),
                        clickable=element.attrib.get("clickable") == "true",
                        inputable=element.attrib.get("class")
                        == "android.widget.EditText",
                        x=position[0],
                        y=position[1],
                        width=position[2] - position[0],
                        height=position[3] - position[1],
                    )
                )

        return virtual_element_list


def _fix_wifi_addr(addr: str) -> Optional[str]:
    if not addr:
        return None
    if re.match(r"^https?://", addr):  # eg: http://example.org
        return addr

    # make a request
    # eg: 10.0.0.1, 10.0.0.1:7912
    if ":" not in addr:
        addr += ":7912"  # make default port 7912
    try:
        r = requests.get("http://" + addr + "/version", timeout=2)
        r.raise_for_status()
        return "http://" + addr
    except:
        return None


def connect(addr=None) -> AndroidDevice:
    """
    Args:
        addr (str): uiautomator server address or serial number. default from env-var ANDROID_DEVICE_IP

    Returns:
        Device

    Raises:
        ConnectError

    Example:
        connect("10.0.0.1:7912")
        connect("10.0.0.1") # use default 7912 port
        connect("http://10.0.0.1")
        connect("http://10.0.0.1:7912")
        connect("cff1123ea")  # adb device serial number
    """
    if not addr or addr == "+":
        addr = os.getenv("ANDROID_DEVICE_IP") or os.getenv("ANDROID_SERIAL")
    wifi_addr = _fix_wifi_addr(addr)
    if wifi_addr:
        return connect_wifi(addr)
    return connect_usb(addr)


def connect_usb(serial: Optional[str] = None, init: bool = False) -> AndroidDevice:
    """
    Args:
        serial (str): android device serial

    Returns:
        Device

    Raises:
        ConnectError
    """
    if init:
        print("connect_usb, args init=True is deprecated since 2.8.0")

    if not serial:
        device = adbutils.adb.device()
        serial = device.serial
    return AndroidDevice(serial)


def connect_wifi(addr: str) -> AndroidDevice:
    """
    Args:
        addr (str) uiautomator server address.

    Returns:
        Device

    Raises:
        ConnectError

    Examples:
        connect_wifi("10.0.0.1")
    """
    _addr = _fix_wifi_addr(addr)
    if _addr is None:
        raise ConnectError("addr is invalid or atx-agent is not running", addr)
    del addr
    return AndroidDevice(_addr)


if __name__ == "__main__":
    device: AndroidDevice = connect()
    element_list = device.hierarchy_to_element()
    image = DrawUtils.label_element_in_image(device.screenshot(), element_list)
    image.show()
    image.save("screenshot.png")


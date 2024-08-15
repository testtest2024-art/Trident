from abc import ABC, abstractmethod

from core.model.exception import ElementDoesNotExistException
from core.model.keys import Keys


class DeviceOperate(ABC):
    @abstractmethod
    def click(self, x, y):
        """
        :param x: 
        :param y: 
        """

    @abstractmethod
    def send_keys(self, value: str or Keys):
        """
        :param value: 
        """

    @abstractmethod
    def find_element_by_text(self, text, timeout=3):
        """
        :param text: 
        :param timeout: 
        """

    @abstractmethod
    def find_element_by_xpath(self, xpath, timeout=3):
        """
        :param xpath: 
        :param timeout: 
        """

    @abstractmethod
    def back(self) -> None:
        """
        
        """

    @abstractmethod
    def go_to_schema(self, schema) -> None:
        """
        
        """

    @abstractmethod
    def swipe_up(self, duration=0.1) -> None:
        """
        
        """

    @abstractmethod
    def swipe_down(self, duration=0.1) -> None:
        """
        
        """

    @abstractmethod
    def start_record(self, file_path):
        """
        
        """

    @abstractmethod
    def stop_record(self):
        """
        
        """

    # @abstractmethod
    # def click_pop_up(self):
    #     res, message = AiTestLabRequestUtils.post_data(path='/detect/pop_up', file_path=file_path)
    #     if not res:
    #         return None
    #     return res[0]["coordinate"]
    #
    # @abstractmethod
    # def watcher(self):
    #     pass


def check_element_exist(func):
    def wrapper(self, *args, **kwargs):
        if self.exist():
            return func(self, *args, **kwargs)
        else:
            raise ElementDoesNotExistException("")

    return wrapper


class ElementOperate(ABC):

    @abstractmethod
    @check_element_exist
    def click(self) -> None:
        """
        
        """
        raise NotImplementedError

    @abstractmethod
    def assert_exist(self) -> None:
        """
        
        """
        raise NotImplementedError

    @abstractmethod
    def screenshot(self):
        """
        
        """

    @abstractmethod
    def draw_in_screenshot(self) -> None:
        """
        
        """
        raise NotImplementedError

    def exist(self):
        raise NotImplementedError

import logging
import os.path

import colorlog

from core.common.utils import get_local_time

class Logger:
    def __init__(self, name: str = "gpt-test", log_path: str = "logs"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        # 
        self.stream_format = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)-15s] %(filename)s(%(lineno)d) [%(levelname)s]%(reset)s - %(message)s',
        )

        # 
        self.file_format = logging.Formatter('%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')

        # 
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(self.stream_format)

        cur_time = get_local_time()

        # 
        self.file_handler = logging.FileHandler(os.path.join(log_path, cur_time + '.log'))  # 
        self.file_handler.setFormatter(self.file_format)

        # 
        self.logger.addHandler(self.stream_handler)
        self.logger.addHandler(self.file_handler)

# 
LOGGER = Logger().logger
LOGGER.info("This is an info message")
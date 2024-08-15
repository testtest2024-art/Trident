import os
from typing import List, Dict

from core.common import utils
from core.runner.runner import Runner

class TestJob:
    def __init__(self, config):
        self.name: str = ""
        self.workspace: str = "./workspace"
        self.devices: Dict[str, str] = {}
        self.case_dir: str = ""
        self.runner = Runner()
        self._parse_config(config)

    def run(self):
        self.runner.build_test_cases(self.case_dir, self.devices, self.workspace)
        self.runner.run_test_cases()

    def _check_fields(self):
        if not self.name and not isinstance(self.name, str):
            raise ValueError(f"testjob's name({self.name}) must be provided"
                             f" and be string type.")

        if not isinstance(self.workspace, str):
            raise ValueError(f"workspace({self.workspace}) must be string type.")

        if not self.devices and not isinstance(self.devices, dict):
            raise ValueError(f"device ids ({self.devices}) must be provided"
                             f" and be list type.")

        if not self.case_dir and not isinstance(self.case_dir, str):
            raise ValueError(f"case dir ({self.case_dir}) must be provided"
                             f" and be string type.")

    def _parse_config(self, config: dict):
        for k, v in config.items():
            if k in self.__dict__:
                self.__dict__[k] = v
        self._check_fields()
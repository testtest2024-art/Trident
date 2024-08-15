import json
import os
import threading
import time
from typing import Dict

from core.runner.testcase.testcase import TestCase
from core.common import utils


class Runner:
    def __init__(self):
        self.test_cases = []

    def build_test_cases(self, case_dir: str, devices: Dict[str, str], workspace: str):
        case_list = []
        for filename in os.listdir(case_dir):
            with open(os.path.join(case_dir, filename), encoding="utf-8") as fp:
                case_list.extend(json.load(fp))
        print(f"all cases num: {len(case_list)}")

        num_devices = len(devices)
        print(f"{num_devices}")
        cases_per_device = len(case_list) // num_devices
        print(f"{cases_per_device}")
        case_lists_per_device = [
            case_list[i * cases_per_device: (i + 1) * cases_per_device]
            for i in range(num_devices)
        ]

        for device, cases in zip(devices.items(), case_lists_per_device):
            self.test_cases.append(TestCase(device, cases, os.path.join(workspace, utils.get_local_time())))



    def run_test_cases(self):
        # 
        threads = []
        for test_case in self.test_cases:
            thread = threading.Thread(
                target=test_case.run,
            )
            threads.append(thread)
            thread.start()
            # 
            time.sleep(1)

        # 
        for thread in threads:
            thread.join()



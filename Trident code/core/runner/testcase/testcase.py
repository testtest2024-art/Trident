import os
import re
import time
import traceback
from typing import List, Dict, Tuple

from core.android.device import AndroidDevice, connect
from core.android.element import AndroidElement
from core.common.log import LOGGER
from core.gptdroid.main import get_llm_element
from core.gptdroid.record import Record
from core.gptdroid.utils import draw_error_case


class TestCase:
    def __init__(self, device: Tuple[str], cases: List[str] = [], workspace: str = ""):
        self.device = None
        self.device_id = device[0]
        self.device_type = device[1]
        self.cases = cases
        self.workspace = workspace
        self.status = "success"
        self.error_reason = None
        self.logger = LOGGER
        self.element_count = 0
        self.element_error_num = 0
        self.element_success_num = 0
        self.case_count = 0
        self.case_error_num = 0
        self.case_success_num = 0
        self.cur_step = 1
        self.record = None


    def run(self):
        self._init_workspace()
        try:
            self.device = self._init_device()
            self.logger.info(
                f"Case:\ndevice_id:{self.device_id}\ndevice_type:{self.device_type}\nworkspace:{self.workspace}")
            self.verify()
        except Exception as e:
            self.status = "fail"
            self.error_reason = e
            self.logger.info(traceback.format_exc())
        finally:
            pass

    def verify(self):
        self.logger.info(f"start: {self.case_count}case")
        # case
        for case_idx, case in enumerate(self.cases):
            self.case_count += 1
            assert isinstance(case, Dict)
            step_list: List[Dict] = case["step_list"]
            case_name = case.get("case_name", "")
            case_desc = case.get("desc", "")

            #  case recorder            self.record = Record(device=self.device, workspace=os.path.join(self.workspace, case_name))

            self.logger.info(
                f"===================={case_idx} {case['case_name']}===================="
            )
            self.logger.info(f" {case_desc}")
            #  case step
            for step_idx, step in enumerate(step_list):
                self.logger.info(f"========step {step_idx}========")
                # step 
                step_desc = ""
                operate = step["operate"]
                element_dict = step.get("element", {})
                params = step["params"]

                self.logger.info(
                    f": {operate}, : {params}, : {element_dict}"
                )
                # if
                if len(element_dict) != 0:
                    self.element_count += 1
                    element_desc = element_dict["desc"]
                    self.logger.info(f"===step {step_idx}: {operate} - {element_desc}===")

                    if operate == "click":
                        step_desc = f": {element_desc}"
                    if operate == "exist":
                        step_desc = f": {element_desc}"
                    if operate == "assert_exist":
                        step_desc += f": {element_desc}"
                    if operate == "send_keys":
                        step_desc += (
                            f": {element_desc}: {params.get('value')}"
                        )
                    #  element_dict  xpath  element
                    element: AndroidElement
                    print('element dict:')
                    print(element_dict)
                    element = self._find_element(element_dict)
                    try:
                        assert isinstance(element, AndroidElement), "element AndroidElement"
                        assert element is not None, " element"
                    except Exception as e:
                        self.logger.error("_find_element, element dict element")
                        break

                    # LLM
            
                    try:
                        x, y, width, height = get_llm_element(self.record, case_name, step_desc, self.workspace)
                    except:
                        self.logger.info(
                            f"error: {traceback.format_exc()}"
                        )
                        self.case_error_num += 1
                        break

                    element_parent = element.get_element_clickable_parent()
                    # x,y
                    pattern = r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]"
                    matches = re.match(pattern, element_parent.get("bounds", "[][]"))
                    position = [int(num) for num in matches.groups()]

                    origin_x, origin_y, origin_width, origin_height = position[0], position[1], position[2] - position[
                        0], position[3] - position[1]

                    self.logger.info(
                        f": {origin_x, origin_y, origin_width, origin_height}"
                    )

                    self.logger.info(f": {x, y, width, height}")

                    # 10 
                    threshold = 10
                    #  10%
                    percentage = 0.1
                    if (
                            # x  threshold  width 
                            abs(origin_x - x) <= min(threshold, origin_width * percentage)
                            # y  threshold  height 
                            and abs(origin_y - y) <= min(threshold, origin_height * percentage)
                            and abs(origin_width - width) <= min(threshold, origin_width * percentage)
                            and abs(origin_height - height) <= min(threshold, origin_height * percentage)
                    ) or (
                        # 
                        # llm  bounds  origin bounds 
                        x >= origin_x
                        and y >= origin_y
                        and (x + width) <= (origin_x + origin_width)
                        and (y + height) <= (origin_y + origin_height)
                    ):
                        self.logger.info("case")
                        self.element_success_num += 1
                    else:
                        self.logger.error("case")
                        # 
                        position2 = [x, y, x + width, y + height]
                        # 

                        draw_error_case(self.record.current_steps, position, position2, os.path.join(self.workspace, case_name))
                        self.logger.info(f"========step {step_idx}========")
                        # 
                        self.element_error_num += 1
                        self.case_error_num += 1
                        break

                    # 
                    if operate == "click":
                        self.logger.info("case")
                        self.device.click(x + width / 2, y + height / 2)
                    else:
                        self.logger.info("case")

                else:
                    #  params  self.device  operate 
                    self.logger.info(f"{operate}, {params}")
                    getattr(self.device, operate)(**params)

                self.logger.info(f"========step {step_idx}========")

                #  3 
                time.sleep(3)

            self.cur_step += self.record.current_steps
        # getattr(self.device, operate)(params)
        self.logger.info(
            f": {self.element_count}, : {self.element_success_num}, : {self.element_success_num / self.element_count}"
        )
        self.case_success_num = self.case_count - self.case_error_num
        self.logger.info(
            f": {self.case_count}, : {self.case_error_num}: {self.case_success_num / self.case_count}"
        )



    def _init_device(self):
        """
        
        """
        device: AndroidDevice = connect(self.device_id)
        # print(f"device: {self.device_id} connected")
        # device = self.device_id
        return device

    def _find_element(self, step_element: dict):
        element_text = None
        element_xpath = None
        attributes: dict = step_element.get("attributes", {})
        #  case  step_element.attributes 
        if attributes.__contains__(self.device_type):
            element_text = attributes[self.device_type].get("text")
            element_xpath = attributes[self.device_type].get("xpath")
        else:
            # 
            for key, value in attributes.items():
                element_text = value.get("text")
        #  text  xpath   AndroidElement
        if element_text:
            element = self.device.find_element_by_text(text=element_text)
            return element
        if element_xpath:
            element = self.device.find_element_by_xpath(xpath=element_xpath)
            return element

        return None

    def _init_workspace(self):
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
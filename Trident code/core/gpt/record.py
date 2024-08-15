import uiautomator2 as u2
from datetime import datetime
import os
import subprocess

from core.gptdroid.process_image import *


class Record:
    def __init__(self, device, workspace: str = "outputs"):
        self.device = device
        self.current_activity = "null"
        self.current_steps = 0
        self.last_action = ""

        self.workspace = workspace
        self.hierarchy_path = os.path.join(workspace, "hierarchy_files")
        self.screenshot_path = os.path.join(workspace, "screenshots")
        self.annotated_image_path = os.path.join(workspace, "annotated_images")
        self.components_path = os.path.join(workspace, "components")
        self.error_path = os.path.join(workspace, "error_cases")

        self.reset()

    def record(self):
        print("...")
        self.current_steps += 1
        # screenshot
        os.makedirs(self.screenshot_path, exist_ok=True)
        self.device.screenshot(f"{self.screenshot_path}/{self.current_steps}.jpg")
        # page hierarchy file
        self.save_page_hierarchy()
        # current activity
        self.current_activity = self.get_running_info()["activity"]
        self.process_current()

    def reset(self):
        self.current_activity = ""
        self.current_steps = 0

        # clear these dirs
        directories = [
            self.hierarchy_path,
            self.screenshot_path,
            self.annotated_image_path,
            self.components_path,
            self.error_path,
        ]

        for directory in directories:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)

        os.makedirs(self.screenshot_path, exist_ok=True)
        os.makedirs(self.hierarchy_path, exist_ok=True)
        os.makedirs(self.annotated_image_path, exist_ok=True)
        os.makedirs(self.components_path, exist_ok=True)
        os.makedirs(self.error_path, exist_ok=True)

    def save_page_hierarchy(self):
        os.makedirs(self.hierarchy_path, exist_ok=True)
        path = self.hierarchy_path + "/" + str(self.current_steps) + ".xml"
        with open(path, "w", encoding="utf-8") as hierarchy_file:
            page_source = self.device.dump_hierarchy(compressed=True, pretty=True)
            hierarchy_file.write(page_source)

    def subprocess_getoutput(self, stmt):
        result = subprocess.getoutput(stmt)
        return result

    def get_running_info(self):
        platform = os.name
        if platform == "nt":
            # 
            cmd = r"adb shell dumpsys activity activities | findstr mActivityComponent="
        elif platform == "posix":
            # 
            cmd = r"adb shell dumpsys activity activities | grep mActivityComponent="
        else:
            raise Exception("Unsupported platform")
        res = self.subprocess_getoutput(cmd)
        # print(res)
        real_res = res.split("\n")[0].strip()
        app_name = real_res.split("/")[0]
        activity_name = real_res.split("/")[1]
        return {"app": app_name, "activity": activity_name}

    def process_current(self):
        tree = ET.parse(os.path.join(self.hierarchy_path, f"{self.current_steps}.xml"))
        root = tree.getroot()
        enabled_components = extract_enabled_components(root)
        idx = 1
        for e in enabled_components:
            e.id = idx
            idx += 1
        # print(f"{len(enabled_components)}")
        # 
        image_path = os.path.join(self.screenshot_path, f"{self.current_steps}.jpg")
        image = cv2.imread(image_path)

        # Drawing the bounds on the image
        enabled_bounds = [e.bound for e in enabled_components]
        image_with_bounds = draw_bounds(image, enabled_bounds)

        # Save the image with drawn bounds
        output_path = os.path.join(self.annotated_image_path, f"{self.current_steps}.jpg")
        cv2.imwrite(output_path, image_with_bounds)

        dict_list = [component.to_dict() for component in enabled_components]
        json_str = json.dumps(dict_list, ensure_ascii=False)
        # print(json_str)
        component_path = os.path.join(self.components_path, f"{self.current_steps}.json")
        with open(component_path, "w", encoding="utf-8") as f:
            f.write(json_str)

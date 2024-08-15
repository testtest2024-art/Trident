import ast
import base64
import re
import time
from typing import List

import requests
from enum import Enum
import cv2
import os

from core.common.utils import is_local_file


def get_response_from_lm(images: List[str], prompt: str):
    """
    """
    api_key = "xxxxxxxxxxx"

    def encode_image(image_path: str):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    msg = [{"type": "text", "text": prompt}]
    for image in images:
        image_path = image
        base64_image = encode_image(image_path)
        msg_cur = {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
        }
        msg.append(msg_cur)

    headers = {"Content-Type": "application/json", "Authorization": f""}

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [{"role": "user", "content": msg}],
        "max_tokens": 3000,
    }

    response, outputs = send_request(headers, payload)

    if "choices" not in response.json():
        print(" response  choices，sleep API ")
        time.sleep(15)

    response, outputs = send_request(headers, payload)

    if "choices" not in response.json():
        print(" response choices，sleep API ")
        time.sleep(15)

    print("[prompt]")
    print(prompt)
    print("[output]")
    print(outputs)

    return outputs


def send_request(headers, payload):
    response = requests.post(
        "https://sparks.ke.com/demo/llm", headers=headers, json=payload
    )
    try:
        outputs = response.json()["choices"][0]["message"]["content"].strip()
    except:
        outputs = "ERROR"
        print(f": {response.text}")
    return response, outputs



class Option(Enum):
    ASK_FOR_KEYS = 1
    ASK_FOR_ID = 2


def getPrompt(
    test_target,
    last_action="",
    option=Option.ASK_FOR_KEYS,
    retrieve_info="",
):
    prompt1 = (
        "Below are instructions for an App exploration task. [Task Description]"
        "### [GUI information]: "
        "The App is {App name}. Its activities are {Activities}. The current page is {Activity name}."
        "### [Testing history]: "    
        "The tested functions and the visit number to each function are as follows: "
        "{Function mame} + {Visit number} "
        "### [Explore optimization]:"
        "According to the feedback from the testing process, "
        "{Possible bug path} "
        "{Exception path}"

        "### [Legend of image]: "
        "{Legend of current GUI screenshots}"
        "{Legend of recently tested screenshots}"

        "### [Query]: "
        "{Querying general action} (e.g., Which numbered widget? What actions are needed? What is the textual description of the widget? ([Widget number] + [Action][click / long-click / check / scroll] + [Widget text] ).)"  
        "{Querying text input} (e.g., Please give the widget number, generate the input text, and the action after input. ([Widget number]+[Input Content]) provided ([Widget number] + [Action[click]] + [Widget text]).) "
    )

    prompt2 = (
        "Below are instructions for the no-crash bug detection task. [Task Description]"
        "### [Bug examples]: "
        "The categories of bugs include {Bug category}. We provide the bug examples:"
        "(1){Bug description} + {Bug replay path}"
        "### [Function-driven COT]: "
        "Let's think step by step."
        "1. Function Identification: The tested function {Function name}"
        "2. Expected Path: Please predict the exploration steps for this fucntion based on above information."
        "3. Actual Path: The tested function sequence is as follows:"
       
        "### [Legend of image]: "
        "The image shows a test sequence arranged in order from left to right and from top to bottom. Each screenshot is labeled with a different colored bounding box indicating the action of the operation. Below the screenshot is the corresponding page description."

        "### [Query]: "
        "{Querying bug detection} (e.g., Please analyze each step in the test sequence in the image based on the description and examples of the bugs, predict whether the page that transits after each step meets your expectation, use this to determine whether there are any bugs, and point out the bug page.）"
        "{Querying possible bug path} (e.g., Is there any page or operation that could potentially trigger some bugs? Please provide the corresponding page and action widget.)"
        "{Querying exception path} (e.g., By analyzing the test path, if there are any pages or operations in the path that have abnormalities? Please provide the corresponding page and action widget.)"

    )

    if option == Option.ASK_FOR_KEYS:
        # print(prompt1)
        return prompt1
    else:
        # print(prompt2)
        return prompt2


def parse_output(s, option):
    if option == Option.ASK_FOR_KEYS:
        # 
        #  keywords
        keyword_pattern = re.compile(r"\[(.*?)\]")
        try:
            keywords = f"[{keyword_pattern.findall(s)[0]}]"
        except ValueError as e:
            raise ValueError('ASK FOR KEYS  keywords : ', s)
        keywords = ast.literal_eval(keywords)
        return keywords
    else:
        # 
        #  ID
        id_pattern = re.compile(r"ID：(.*?)，")
        action_pattern = re.compile(r"：(.*?)。")
        try:
            id = int(id_pattern.findall(s)[0])
        except ValueError as e:
            raise ValueError('ASK FOR ID  id : ', s)
            # -1 
            id = None
        try:
            action = action_pattern.findall(s)[0]
        except ValueError as e:
            raise ValueError('ASK FOR ID  action : ', s)
            action = None

        return id, action


def draw_2bounds(image, bounds1, bounds2):
    """
    bounds1
    bounds2
    """
    x1, y1, x2, y2 = bounds1
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Blue colorunds1
    x1, y1, x2, y2 = bounds2
    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Blue colorunds1
    return image


def draw_error_case(i, bounds1, bounds2, workspace):
    print('')
    image_path = os.path.join(workspace, f"screenshots/{i}.jpg")
    image = cv2.imread(image_path)
    image_with_bounds = draw_2bounds(image, bounds1, bounds2)
    # Save the image with drawn bounds
    output_path = os.path.join(workspace, f"error_cases/{i}.jpg")
    cv2.imwrite(output_path, image_with_bounds)
import json
import os.path
import time
from typing import List

from core.gptdroid.utils import get_response_from_lm, getPrompt, Option, parse_output
from core.gptdroid.record import Record

def get_llm_element(record, case: str, step_desc: str, workspace: str):
    workspace = os.path.join(workspace, case)
    # record = Record(device=device, workspace=workspace)
    record.record()

    cur_step = record.current_steps

    file_path = os.path.join(workspace, f"annotated_images/{cur_step}.jpg")

    max_retries = 3
    retries = 0
    success = False

    keywords = []
    # Stage 1
    while not success and retries < max_retries:
        try:
            keywords = run_stage1(step_desc, file_path, record.last_action)
            success = True
        except Exception as e:
            print(f": {e}")
            retries += 1
            time.sleep(1)  # 
    if not success:
        print("程序在stage1")

    # Stage 2
    component_info = os.path.join(workspace, f"components/{cur_step}.json")

    retrieve_list = []
    with open(component_info, "r") as f:
        data = json.load(f)
        for each_data in data:
            for keyword in keywords:
                if keyword in each_data['name']:
                    retrieve_list.append(each_data)
                    break

    max_retries = 3
    retries = 0
    success = False

    id, action = "", ""
    while not success and retries < max_retries:
        try:
            id, action = run_stage2(step_desc, file_path, record.last_action, retrieve_list)
            success = True
        except Exception as e:
            print(f": {e}")
            retries += 1
            time.sleep(1)
    if not success:
        print("stage2")

    if not success:
        print("error")

    # record.last_action = action

    click_item = {}
    with open(component_info, "r") as f:
        data = json.load(f)
        for each in data:
            if each["id"] == id:
                click_item = each
                break

    record.last_action = f"{str(click_item)}"
    print('', click_item)

    return (
        click_item["bound"][0],
        click_item["bound"][1],
        click_item["bound"][2] - click_item["bound"][0],
        click_item["bound"][3] - click_item["bound"][1],
    )

def run_stage1(test_target, file_path: str, last_action: str):
    output = get_response_from_lm(
        [file_path],
        getPrompt(
            test_target=test_target,
            last_action=last_action,
            option=Option.ASK_FOR_KEYS,
        ),
    )
    keywords = parse_output(output, Option.ASK_FOR_KEYS)
    print(f"keywords: {keywords}")

    keywords = [
        keyword.replace("“", "").replace("”", "").replace('"', "")
        for keyword in keywords
    ]
    print(f" keywords（python list）: {keywords}")
    return keywords


def run_stage2(test_target, file_path: str, last_action: str, retrieve_list: List[str]):
    output = get_response_from_lm(
        [file_path],
        getPrompt(
            test_target=test_target,
            last_action=last_action,
            option=Option.ASK_FOR_ID,
            retrieve_info=str(retrieve_list),
        ),
    )
    id, action = parse_output(output, Option.ASK_FOR_ID)
    return id, action
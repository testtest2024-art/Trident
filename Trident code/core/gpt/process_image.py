import json
from xml.etree import ElementTree as ET
import numpy as np
from matplotlib import pyplot as plt
import cv2
import re

from core.gptdroid.component import Component

"""
XML
"""

def extract_enabled_components(root):
    # 
    def find_leaves(parent):
        leaves = []
        for child in parent:
            if len(list(child)) == 0:  # 
                leaves.append(child)
            else:
                leaves.extend(find_leaves(child))  # 
        return leaves

    # 
    leaves = find_leaves(root)

    # 
    def filter_nodes(leaves):
        filtered = []
        for leaf in leaves:
            # 
            if leaf.get('package') == '':
                if leaf.get('class') == 'android.widget.ImageView' or leaf.get('text') or leaf.get('content-desc'):
                    filtered.append(leaf)
        return filtered

    # 
    filtered_leaves = filter_nodes(leaves)

    all_components = []

    for node in filtered_leaves:
        bound_str = node.attrib.get("bounds")
        coords = list(map(int, re.findall(r"\d+", bound_str)))
        text = node.attrib.get("text") if node.attrib.get("text") else ""
        resource_id = node.attrib.get("resource-id") if node.attrib.get("resource-id") else ""
        content_desc = node.attrib.get("content-desc") if node.attrib.get("content-desc") else ""
        component = Component(text=text, resource_id=resource_id, desc=content_desc, bound=coords)
        all_components.append(component)

    # 
    id2text = {
        "iv_detial_head_error": "",
        "iv_house_compare": "",
        "iv_detial_head_im": "",
        "iv_detial_head_share": "",
        "iv_search_change_city_down_icon": "",
        "tv_nav_center_search_text": ""
    }

    # 
    #  text  desc  desc  text
    for component in all_components:
        for key in id2text.keys():
            if key in component.resource_id:
                component.text = id2text[key]
                break
        if component.text == None and component.desc != None:
            component.text = component.desc


    for component in all_components:
        text = component.text
        resource_id = component.resource_id
        content_desc = component.desc
        name = f"tex{text}，resource_id{resource_id}，content_desc{content_desc}"
        component.name = name

    return all_components

# 
# Function to recursively extract bounds of enabled elements
def extract_enabled_components_deprecated(node):
    """
    """
    components = []

    #  system ui
    if node.attrib.get(
            "resource-id"
    ) == "true" and "com.android.systemui" in node.attrib.get("resource-id"):
        return

    if node.attrib.get(
            "package"
    ) == "true" and "systemui" in node.attrib.get("package"):
        return

    # package = node.attrib.get("package")
    # if package is not None and "systemui" in package:
    #     return

    def get_info_from_child(node, attrib):
        """
        
        len(node)  0  1
        """
        if node.attrib.get(attrib):
            return node.attrib.get(attrib)
        for child in node:
            info = get_info_from_child(child, attrib)
            if info:
                return info
        return ""

    # 
    # 
    if node.attrib.get("clickable") == "true" or node.attrib.get("text") is not None:
        # 
        bound_str = node.attrib.get("bounds")
        coords = list(map(int, re.findall(r"\d+", bound_str)))
        text = get_info_from_child(node, "text") or ""
        resource_id = get_info_from_child(node, "resource-id") or ""
        content_desc = get_info_from_child(node, "content-desc") or ""
        name = f"text{text}，resource_id{resource_id}，content_desc{content_desc}"
        component = Component(name=name, bound=coords)
        components.append(component)


    # Recursively check for any child nodes
    for child in node:
        components.extend(extract_enabled_components(child))

    return components


def sortBounds(bounds):
    """
    """
    sorted_data = sorted(bounds, key=lambda x: (x[1], x[0]))

    return sorted_data


# Function to draw rectangles on the image based on the bounds
import cv2


def draw_bounds(image, bounds_list):
    """
    """
    num = 0
    # last_y = -1
    for coords in bounds_list:
        num += 1
        # Extracting the coordinates from the bounds string
        # coords = list(map(int, re.findall(r'\d+', bound_str)))
        # Since coords are in the form [x1,y1,x2,y2], we unpack them
        x1, y1, x2, y2 = coords
        # Draw a rectangle on the image
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Blue color

        # if y1 != last_y:
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_color = (0, 0, 255)  # Red color
        background_color = (169, 169, 169)  # Gray color
        text = str(num)
        # (text_width, text_height) = cv2.getTextSize(text, font, font_scale, 2)[0]
        # box_coords = ((x1, y1+30), (x1 + text_width, y1 - text_height + 25))
        # cv2.rectangle(image, box_coords[0], box_coords[1], background_color, cv2.FILLED)
        cv2.putText(image, text, (x1, y1 + 30), font, font_scale, font_color, 2)
        # last_y = y1

    return image


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


def calculate_area(box):
    """
    """
    # 
    return (box[2] - box[0]) * (box[3] - box[1])


def is_fully_overlapped(box1, box2):
    """
    """
    #  box1  box2  box2  box1
    return (
            box1[0] <= box2[0]
            and box1[1] <= box2[1]
            and box1[2] >= box2[2]
            and box1[3] >= box2[3]
    ) or (
            box2[0] <= box1[0]
            and box2[1] <= box1[1]
            and box2[2] >= box1[2]
            and box2[3] >= box1[3]
    )


def calculate_overlap_area(box1, box2):
    """
    
    """
    overlap_width = max(0, min(box1[2], box2[2]) - max(box1[0], box2[0]))
    overlap_height = max(0, min(box1[3], box2[3]) - max(box1[1], box2[1]))
    return overlap_width * overlap_height


def is_large_overlap(box1, box2, threshold=0.3):
    """
    
    """
    overlap_area = calculate_overlap_area(box1, box2)
    area1 = calculate_area(box1)
    area2 = calculate_area(box2)

    # 
    return overlap_area > threshold * area1 or overlap_area > threshold * area2


def remove_larger_overlap(boxes):
    """
    """
    i = 0
    while i < len(boxes):
        removed = False
        for j in range(i + 1, len(boxes)):
            if is_fully_overlapped(boxes[i], boxes[j]):
                # if is_overlap(boxes[i], boxes[j]):
                # 
                if calculate_area(boxes[i]) > calculate_area(boxes[j]):
                    del boxes[i]
                else:
                    del boxes[j]
                removed = True
                break  # 
        if not removed:
            i += 1  # 
    return boxes


def shift_box(box, dx, dy):
    """
    
    """
    return [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]


def resolve_overlap(boxes):
    """
    
    """
    for i in range(len(boxes)):
        for j in range(len(boxes)):
            if (
                    i != j
                    and is_large_overlap(boxes[i], boxes[j])
                    and is_fully_overlapped(boxes[i], boxes[j]) == False
            ):
                # print('OOOKKKK')
                # print('box i', boxes[i])
                # print('box j', boxes[j])
                # 
                # 
                if boxes[i][0] < boxes[j][0] or boxes[i][1] < boxes[j][1]:
                    # boxes[j] 
                    shift_x = max(0, boxes[i][2] - boxes[j][0])
                    shift_y = max(0, boxes[i][3] - boxes[j][1])
                    # boxes[j] = shift_box(boxes[j], shift_x, shift_y)
                    boxes[j] = shift_box(boxes[j], 0, shift_y)
                else:
                    # boxes[i] 
                    shift_x = max(0, boxes[j][2] - boxes[i][0])
                    shift_y = max(0, boxes[j][3] - boxes[i][1])
                    # boxes[i] = shift_box(boxes[i], shift_x, shift_y)
                    boxes[i] = shift_box(boxes[i], 0, shift_y)
                # print('box i', boxes[i])
                # print('box j', boxes[j])
    return boxes


# def draw_error_case(i, bounds1, bounds2):
#     print('error')
#     image_path = f"./screenshots/{i}.jpg"
#     image = cv2.imread(image_path)
#
#     image_with_bounds = draw_2bounds(image, bounds1, bounds2)
#     # Save the image with drawn bounds
#     output_path = f"error_cases/{i}.jpg"
#     cv2.imwrite(output_path, image_with_bounds)

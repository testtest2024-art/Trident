import os
import subprocess

from core.gptdroid.process_image import *

def process_current(hierarchy_path, current_steps):
    tree = ET.parse(os.path.join(hierarchy_path, f"{current_steps}.xml"))
    root = tree.getroot()

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
            if leaf.get('package') == 'com.xxxx':
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
        name = f"text{text}，resource_id{resource_id}，content_desc{content_desc}"
        component = Component(name=name, bound=coords)
        all_components.append(component)


    idx = 1
    for e in all_components:
        e.id = idx
        idx += 1
        print(e)

if __name__ == '__main__':
    hierarchy_path = "./outputs/"
    current_steps = 1
    process_current(hierarchy_path, current_steps)
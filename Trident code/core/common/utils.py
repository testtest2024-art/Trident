import os
import sys
import time

import yaml

def is_local_file(url):
    """Check if the url is a file and already exists locally."""
    return os.path.isfile(url)

def get_local_time():
    """Get local time."""
    return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

def yaml2dict(url):
    """Convert yaml file to the dict."""
    if url.endswith('.yaml') or url.endswith('.yml'):
        with open(url, "rb") as file:
            raw_dict = yaml.load(file, Loader=yaml.SafeLoader)

        return raw_dict

    raise RuntimeError('config file must be the yaml format')
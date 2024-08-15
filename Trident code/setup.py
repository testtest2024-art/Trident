import sys
import os

from setuptools import setup, find_packages

assert sys.version_info >= (3, 6), "Sorry, Python < 3.6 is not supported."


class InstallPrepare:
    """
    Parsing dependencies
    """

    def __init__(self):
        self.project = os.path.join(os.path.dirname(__file__), "core")
        # self._requirements = os.path.join(self.project, "..", "requirements.txt")


    @property
    def version(self):
        default_version = "0.1.0"
        return default_version

_infos = InstallPrepare()

setup(
    name='tgpt',
    version=_infos.version,
    description="A package which use gpt4v to test Android cases",
    packages=find_packages(exclude=["tests", "*.tests",
                                    "*.tests.*", "tests.*"]),
    include_package_data=True,
    entry_points={
        "console_scripts": ["tgpt = core.cmd.main:main"]
    },
    python_requires=">=3.6",
    license="Apache License 2.0",
)
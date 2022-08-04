from yaml import safe_load, YAMLError
from typing import Dict
import os


class Parser():
    """Parser class. Exists solely to parse yaml files in the folder and create
    a check tree.

    Attributes:

    Methods:
        generate_tree -- generates a check tree.
    """

    yml_dict: Dict
    test_path: str = ""

    def __init__(self):
        self.test_path = get_test_path()

    def parse_yaml(self) -> Dict:
        if self.test_path == "":
            return {}
        with open(self.test_path, "r") as ymlfile:
            try:
                data = safe_load(ymlfile)
                return data
            except YAMLError as exc:
                print(exc)
                return {}

    def generate_tree(self) -> Dict:
        return {}


def get_test_path() -> str:
    """Parses working dir in search of a test configuration file.
    Returns its decoded path
    """
    cwd = os.getcwd()
    # Check if there is a configuration file in working dir
    if os.path.isfile(f"{cwd}/test.yml") is True:
        return os.fspath(f"{cwd}/test.yml")
    # Else check if it's in a "test" folder
    if os.path.isfile(f"{cwd}/tests/test.yml") is True:
        return os.fspath(f"{cwd}/tests/test.yml")
    return ""

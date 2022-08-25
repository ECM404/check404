from yaml import safe_load, YAMLError
from .check import Check
from typing import Dict
import os
import glob


class Parser():
    """Parser class. Exists solely to parse yaml files in the folder and create
    a check tree.

    Attributes:
        test_path -- Path to the config file
        yml_dict -- Dictionary created from reading the test config file

    Methods:
        generate_tree -- generates a check tree.
    """

    yml_dict: Dict
    test_path: str = ""
    check_tree: list

    def __init__(self):
        self.test_path = get_glob_path('**/*.yml')
        self.yml_dict = flatten_dict(read_yml(self.test_path))

    def generate_tree(self):
        """Generates a check tree using a list of lists.
        TODO - Real tree implementation
        """
        tree = []
        files = set()
        i = -1
        for name, conf in self.yml_dict.items():
            file = conf["file"]
            if file not in files:
                files.add(file)
                comp_check = Check(f"Compilation {file}", file=file, weight=1)
                tree.append([comp_check])
                i += 1
            tree[i].append(
                Check(name, **conf, parent=tree[i][0])
            )
        self.check_tree = tree


def flatten_dict(d: Dict) -> Dict:
    """Flatten dictionary with stdin/stdout with more than 1 entry. Returns
    the same dictionary if there is nothing to flatten
    Example:
        {"Ex1":{"stdin":[1,2], "stdout":[2,3]}} turns into:
        {"Ex1 (in:1, out:2)":{"stdin":"1", "stdout":"2"},
         "Ex1 (in:2, out:3)":{"stdin":"2", "stdout":"3"}}
    """
    new_d = d.copy()
    for key, value in d.items():
        if isinstance(value["stdin"], list):
            new_value = new_d.pop(key)
            for stdin, stdout in zip(value["stdin"], value["stdout"]):
                new_value["stdin"], new_value["stdout"] = stdin, stdout
                stdin_noret = stdin.replace("\n", " -> ")
                new_d[f"{key}(in:{stdin_noret})"] = new_value.copy()
    return new_d


def read_yml(path: str) -> Dict:
    """Safely reads yml file and returns a dictionary."""
    if path == "":
        return {}
    with open(path, "r") as ymlfile:
        try:
            data = safe_load(ymlfile)
            return data
        except YAMLError as exc:
            print(exc)
            return {}


def get_glob_path(pattern: str) -> str:
    """Parses working dir in search of a test configuration file.
    Returns its decoded path
    """
    found = glob.glob(pattern)[0]
    if isinstance(found, list):
        return found[0]
    return found

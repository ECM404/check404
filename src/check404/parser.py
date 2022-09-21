from yaml import safe_load, YAMLError
from .check import Check
from .tree import Tree, Node
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

    def __init__(self):
        self.test_path = get_glob_path('**/*.yml')
        self.yml_dict = flatten_dict(read_yml(self.test_path))

    def generate_tree(self) -> Tree:
        """Generates a check tree using a list of lists.
        TODO - Real tree implementation
        """
        root = Node()
        tree = Tree(root=root)
        files = separate_by_files(self.yml_dict)
        flist = list(files.keys())
        flist.sort()
        for file in flist:
            comp_check = Check(f"Compilando {file}", file=file, weight=1)
            froot = Node(check=comp_check, parent=root)
            tree.add_node(froot)
            nodes = list(files[file].keys())
            nodes.sort()
            for n in nodes:
                conf = files[file][n]
                temp_check = Check(n, **conf)
                tree.add_node(Node(check=temp_check, parent=froot))
        return tree


def separate_by_files(d: Dict) -> Dict:
    """Get the flattened dictionary and separate it by files."""
    unique_files = set([d[x]['file'] for x in d])
    out = {}
    for f in unique_files:
        temp_dict = {x: d[x] for x in d if f in d[x]['file']}
        out[f] = temp_dict
    return out


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
    found = glob.glob(pattern, recursive=True)
    if isinstance(found, list):
        return found[0]
    return found

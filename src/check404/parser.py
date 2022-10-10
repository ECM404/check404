from yaml import safe_load, YAMLError
from .check import Check
from .tree import Tree, Node
from typing import Dict
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
        """Generates a check tree and returns it.
        """
        root = Node()
        tree = Tree(root=root)
        unique_files = set(
            [self.yml_dict[check][0]["file"] for check in self.yml_dict]
        )
        for file in unique_files:
            comp_node = Node(check=Check(f"Compilando {file}",
                             file=file, weight=1), parent=root)
            tree.add_node(comp_node)
            for check_name, check_configs in self.yml_dict.items():
                for i, config in enumerate(check_configs):
                    name = check_name if i == 0 else ""
                    if not file == config["file"]:
                        continue
                    node = Node(check=Check(name, **config), parent=comp_node)
                    tree.add_node(node)
        return tree


def flatten_dict(d: Dict) -> Dict:
    """Flatten dictionary with stdin/stdout with more than 1 entry. Returns
    the same dictionary if there is nothing to flatten.
    Example:
        {"Ex1":{"stdin":[1,2], "stdout":[2,3]}}
        turns into:
        {"Ex1":[ {"stdin":"1", "stdout":"2"},
                 {2, out:3)":{"stdin":"2", "stdout":"3"} ]}
    """
    for key, value in d.items():
        input_key = "input" if "input" in value else "stdin"
        # If the input is not a group, there's nothing to do...
        if not isinstance(value[input_key], list):
            d[value] = [d[value]]
            continue
        output_key = ("varout" if "varout" in value else
                      "output" if "output" in value else "stdout")
        new_value = []
        for stdin, stdout in zip(value[input_key], value[output_key]):
            partial_value = value.copy()
            partial_value[input_key] = stdin
            partial_value[output_key] = stdout
            new_value.append(partial_value)
        d[key] = new_value
    return d


def read_yml(path: str) -> Dict:
    """Safely reads yml file and returns a dictionary."""
    if path == "":
        return {}
    with open(path, "r") as ymlfile:
        try:
            return safe_load(ymlfile)
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

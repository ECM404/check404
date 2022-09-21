from .parser import Parser
from pprint import pprint


def main():
    p = Parser()
    check_tree = p.generate_tree()
    for node in check_tree.depth_first_search(check_tree.root):
        print(f" {node.check.name}\n{node.check.run()}")

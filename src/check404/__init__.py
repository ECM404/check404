from .parser import Parser
from pprint import pprint


def main():
    p = Parser()
    p.generate_tree()
    for file in p.check_tree:
        for check in file:
            print(f"{check.name} - {check.run()}")

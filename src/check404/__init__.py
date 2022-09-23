from .parser import Parser
from os import system


def main():
    p = Parser()
    check_tree = p.generate_tree()
    for node in check_tree.depth_first_search(check_tree.root):
        print(f"{'':>8s} {node.check.name}\n{node.check.run()}\n")
    print(f"{'':>8s} Testes encerrados. Limpando diretório.")
    system("rm -rf ./dll ./bin")

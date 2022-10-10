from .parser import Parser
from os import system


def main():
    p = Parser()
    check_tree = p.generate_tree()
    for node in check_tree.depth_first_search(check_tree.root):
        if node.check.name:
            print(f"\n{'':>8s} {node.check.name}")
        print(f"{node.check.run()}")
    print(f"\n{'':>8s} Testes encerrados. Limpando o diretório.")
    system("rm -rf ./dll ./bin")

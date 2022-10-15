from os import system
from check404.parser import Parser


def check(yml_path: str = "**/*.yml"):
    p = Parser(yml_path)
    check_tree = p.generate_tree()
    for node in check_tree.depth_first_search(check_tree.root):
        if node.check.name:
            print(f"\n{'':>8s} {node.check.name}")
        print(f"{node.check.run()}")
    print(f"\n{'':>8s} Testes encerrados. Limpando o diretório.")
    system("rm -rf ./dll ./bin")

from __future__ import annotations
from typing import List, Any, Optional


class Tree():
    root: Node
    nodes: List

    def __init__(self, root: Node):
        self.root = root
        self.nodes = []
        self.add_node(self.root)

    def add_node(self, node: Node):
        self.nodes.append(node)

    def dfs_util(self, v, visited):
        if not v.root:
            yield v
        visited.add(v)
        neighbors = v.children
        for node in self.nodes:
            if node in neighbors and node not in visited:
                yield from self.dfs_util(node, visited)

    def depth_first_search(self, v):
        visited = set()
        yield from self.dfs_util(v, visited)


class Node():
    check: Any
    parent: Node
    root: bool = True
    children: List[Node]

    def __init__(self,
                 check: Optional[Any] = None,
                 parent: Optional[Node] = None):
        if check:
            self.check = check
            self.root = False
        self.children = []
        if parent:
            self.parent = parent
            self.parent.add_child(self)
            self.root = False

    def add_child(self, child: Node):
        self.children.append(child)

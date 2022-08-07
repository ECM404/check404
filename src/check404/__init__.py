from . import check, behaviors
from .parser import Parser
from anytree import RenderTree,  PreOrderIter
import pprint


def main():
    p = Parser()
    p.generate_tree()
    print(p.check_tree[0][0].run())
    # c = check.Check(
    #         file='b.out',
    #         inputs=['5'],
    #         expect=['5'],
    #         run_behavior=behaviors.iostream_run,
    #         validation_behavior=behaviors.iostream_validation
    #         )
    # result = c.run()
    # print(result)

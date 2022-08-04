from . import check, behaviors, parser
import pprint


def main():
    pprint.pprint(parser.Parser().parse_yaml())
    # c = check.Check(
    #         file='b.out',
    #         inputs=['5'],
    #         expect=['5'],
    #         run_behavior=behaviors.iostream_run,
    #         validation_behavior=behaviors.iostream_validation
    #         )
    # result = c.run()
    # print(result)

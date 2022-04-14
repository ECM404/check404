from . import testing, behaviors


def main():
    check = testing.Check(
            file='b.out',
            input='5',
            expect='5',
            run_behavior=behaviors.iostream_run,
            validation_behavior=behaviors.iostream_validation
            )
    result = check.run()
    print(result)

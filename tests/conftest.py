import pytest
from check404 import testing, behaviors


@pytest.fixture(scope="session")
def create_check():
    check = testing.Check(
            file='b.out',
            input='5',
            expect='5',
            run_behavior=behaviors.iostream_run,
            validation_behavior=behaviors.iostream_validation
            )
    return check

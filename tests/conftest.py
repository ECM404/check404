import pytest
from check404 import testing, behaviors


@pytest.fixture(scope="function")
def compile_check():
    def _compile_check(file):
        check = testing.Check(
                file=file,
                run_behavior=behaviors.compilation_run,
                validation_behavior=behaviors.file_validation
                )
        return check.run()
    return _compile_check

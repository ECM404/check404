import pytest
from check404 import check, behaviors


@pytest.fixture(scope="function")
def compile_check():
    def _compile_check(file):
        c = check.Check(
                file=file,
                run_behavior=behaviors.compilation_run,
                validation_behavior=behaviors.file_validation
                )
        return c.run()
    return _compile_check


@pytest.fixture(scope="function")
def compile_dll_check():
    def _compile_dll(file):
        c = check.Check(
                file=file,
                run_behavior=behaviors.compilation_run,
                validation_behavior=behaviors.file_validation
                )
        return c.run(dll=True)
    return _compile_dll

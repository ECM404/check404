from check404 import check, behaviors
from .test_iostream import get_testfiles
import pytest


@pytest.mark.parametrize("file", get_testfiles('./c_src'))
def test_dll_compilation(compile_dll_check, file):
    """Test function that checks for dll compilation.
    Checks files inside c_src dir
    """
    assert compile_dll_check(file).state is check.CheckState.PASSED


def test_cdll_open():
    """Test function that checks if CDLL is loading correctly
    """
    c = check.Check(
            './dll/iostream_simple.so',
            inputs=[0, ''],
            expect=["0"],
            run_behavior=behaviors.function_run,
            validation_behavior=behaviors.iostream_validation
            )
    results = c.run(func="main", types=['c_int', ['c_int', 'c_wchar_p']])
    assert results.state is check.CheckState.PASSED


def test_cdll_open_fail():
    """Test function that checks if OSError is being raised
    """
    c = check.Check(
            './dll/iostream_simple.dll',
            '5',
            'O valor digitado foi 5',
            behaviors.function_run
            )
    results = c.run(func="", types="")
    assert results.state is check.CheckState.ERROR

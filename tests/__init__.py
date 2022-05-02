from check404 import check
from .test_iostream import get_testfiles
import pytest


@pytest.mark.parametrize("file", get_testfiles('./c_src'))
def test_dll_compilation(compile_dll_check, file):
    """Test function that checks for compilation. Checks files inside c_src dir
    """
    assert compile_dll_check(file).state is check.CheckState.PASSED

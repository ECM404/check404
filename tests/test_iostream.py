from check404 import testing, behaviors
import pytest
import os


def get_testfiles(dir: str) -> list:
    """Function used to get list of files with full pathname"""
    file_list = os.listdir(dir)
    return [f"{dir}/{file}" for file in file_list]


@pytest.mark.parametrize("file", get_testfiles('./c_src'))
def test_compilation(compile_check, file):
    """Test function that checks for compilation. Checks files inside c_src dir
    """
    assert compile_check(file).state is testing.CheckState.PASSED


def test_simpleIO_correct():
    """Test function that checks for simpleIO - correct case"""
    check = testing.Check(
            './bin/iostream_simple.out',
            '5',
            'O valor digitado foi 5',
            behaviors.iostream_run, behaviors.iostream_validation
            )
    results = check.run()
    assert results.state is testing.CheckState.PASSED


def test_simpleIO_incorrect():
    """Test function that checks for simpleIO - incorrect case"""
    check = testing.Check(
            './bin/iostream_simple_inc.out',
            '5',
            'O valor digitado foi 5',
            behaviors.iostream_run, behaviors.iostream_validation
            )
    results = check.run()
    assert results.state is testing.CheckState.FAILED


def test_simpleIO_nofile():
    """Test function that checks for simpleIO - no file case"""
    check = testing.Check(
            './bin/iostream_simple_inc2.out',
            '5',
            'O valor digitado foi 5',
            behaviors.iostream_run, behaviors.iostream_validation
            )
    results = check.run()
    assert results.state is testing.CheckState.ERROR

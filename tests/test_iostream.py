from check404 import check, behaviors
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
    assert compile_check(file).state is check.CheckState.PASSED


def test_simpleIO_correct():
    """Test function that checks for simpleIO - correct case"""
    c = check.Check(
            './bin/iostream_simple.out',
            ['5'],
            ['O valor digitado foi 5'],
            behaviors.iostream_run, behaviors.iostream_validation
            )
    results = c.run()
    assert results.state is check.CheckState.PASSED


def test_simpleIO_incorrect():
    """Test function that checks for simpleIO - incorrect case"""
    c = check.Check(
            './bin/iostream_simple_inc.out',
            ['5'],
            ['O valor digitado foi 5'],
            behaviors.iostream_run, behaviors.iostream_validation
            )
    results = c.run()
    assert results.state is check.CheckState.FAILED


def test_simpleIO_nofile():
    """Test function that checks for simpleIO - no file case"""
    c = check.Check(
            './bin/iostream_simple_inc2.out',
            ['5'],
            ['O valor digitado foi 5'],
            behaviors.iostream_run, behaviors.iostream_validation
            )
    results = c.run()
    assert results.state is check.CheckState.ERROR


def test_doubleIO():
    """Test function that checks for double input case"""
    c = check.Check(
            './bin/iostream_double.out',
            ['5 6'],
            ['Os valores digitados foram: 5, 6'],
            behaviors.iostream_run, behaviors.iostream_validation
            )
    results = c.run()
    assert results.state is check.CheckState.PASSED


def test_double_str():
    """Test function that checks for double string input"""
    c = check.Check(
            './bin/iostream_double_string.out',
            ['5', 'Mundo'],
            ['Mundo 5'],
            behaviors.iostream_run, behaviors.iostream_validation
            )
    results = c.run()
    assert results.state is check.CheckState.PASSED

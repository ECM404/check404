from .types import parse_types, get_args
from subprocess import PIPE
from collections import namedtuple
from enum import Enum
from typing import List
import typing
import subprocess
import os
import ctypes

if typing.TYPE_CHECKING:
    from .check import Check

TIMEOUT = 2  # seconds

RED = "\u001b[31;1m"
GREEN = "\u001b[32;1m"
YELLOW = "\u001b[33;1m"
RESET = "\u001b[0m"

COLORS = {"ERROR": RED, "PASSED": GREEN, "FAILED": YELLOW}


class CheckResult (namedtuple("CheckResult", ['state', 'msg'])):
    """Named tuple with custom str function. Represents the check result."""

    def __str__(self):
        return f"{self.state} {self.msg}"


class CheckState(Enum):
    """Enum that stores state of a Check result."""
    ERROR = 1
    PASSED = 2
    FAILED = 3

    def __str__(self):
        return f"[{COLORS[self.name]}{self.name}{RESET}]"


def function_run(check: 'Check') -> CheckResult:
    """Run behavior to compose Check class.
    Simple function run. Uses dll compiled from c file and runs some function
    inside of it. Can be used with io_validation.

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        function -- function that needs to be run
    """
    _, filename = os.path.split(check.file)
    dll_name = filename.replace('.c', '.dll')
    # type name(type name, type name)
    functype = check.function[:check.function.index(" ")]
    funcname = check.function[
                        check.function.index(" "):check.function.index("(")
                        ]
    argtypes = check.function[
                        check.function.index("("):check.function.index(")")
                        ]
    try:
        c_lib = ctypes.CDLL(f"./dll/{dll_name}")
    except OSError:
        msg = f"O arquivo './dll/{dll_name}' não foi encontrado."
        return CheckResult(CheckState.ERROR, msg)
    try:
        c_func = getattr(c_lib, funcname)
    except AttributeError:
        msg = f"A função '{funcname}' não foi encontrada."
        return CheckResult(CheckState.ERROR, msg)
    c_func.restype, c_func.argtypes = parse_types(types)
    arglist = get_args(check.input, c_func.argtypes)
    output = c_func(*arglist)
    return check.validate(output=str(output))


def iostream_run(check: 'Check') -> CheckResult:
    """Run behavior to compose Check class.
    Simple running behavior. Run entire program as subprocess.
    Caputres stdout to be passed as argument to validation method.

    Parameters:
        check -- Check class instance. Should be passed as 'self'
    """
    _, filename = os.path.split(check.file)
    executable_name = filename.replace('.c', '.out')
    if not check.input:
        check.input = ""

    try:
        process = subprocess.Popen([f"./bin/{executable_name}"],
                                   stdin=PIPE,
                                   stdout=PIPE,
                                   encoding='utf-8')
    except OSError:
        msg = f"O arquivo './bin/{executable_name}' não foi encontrado. "
        return CheckResult(CheckState.ERROR, msg)
    try:
        output, _ = process.communicate(check.input+"\n", timeout=TIMEOUT)
    except subprocess.TimeoutExpired as e:
        msg = f"Programa não respondeu após {e.timeout} segundos. "
        return CheckResult(CheckState.ERROR, msg)
    return check.validate(output=output)


def iostream_validation(check: 'Check', output: str) -> CheckResult:
    """Validation behavior to compose Check class.
    Simple check to see if output matches exactly what was expected

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        output -- Stdout from run method.
    """

    if check.output in output:
        msg = "Teste concluído com sucesso! "
        return CheckResult(CheckState.PASSED, msg)
    else:
        msg = (f"Não passou. Esperava encontrar '{check.output}' na saída. ")
        return CheckResult(CheckState.FAILED, msg)


def compilation_run(check: 'Check') -> CheckResult:
    """Compilation run behavior to compose Check. Uses gcc for compilation.

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        dll -- Flag that defines if it will compile as dll
    """

    _, filename = os.path.split(check.file)
    if not os.path.isdir('./bin'):
        os.mkdir('./bin')
    elif not os.path.isdir('./dll'):
        os.mkdir('./dll')
    dll_path = f"./dll/{filename.replace('.c', '.so')}"
    bin_path = f"./bin/{filename.replace('.c', '.out')}"
    dll_cmd = ['gcc', check.file, '-o', dll_path, '-fPIC', '-shared']
    bin_cmd = ['gcc', check.file, '-o', bin_path]
    dll_result = subprocess.run(dll_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                                encoding='utf-8')
    bin_result = subprocess.run(bin_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                                encoding='utf-8')
    if not bin_result.returncode == 0:
        msg = (f"Erro ao compilar o arquivo {check.file} como executável. ")
        return CheckResult(CheckState.ERROR, msg)
    if not dll_result.returncode == 0:
        msg = (f"Erro ao compilar o arquivo {check.file} como dll. ")
        return CheckResult(CheckState.ERROR, msg)
    filenames = [bin_path, dll_path]
    return check.validate(filenames=filenames)


def file_validation(check: 'Check', filenames: list) -> CheckResult:
    """File validation behavior to compose Check. Checks if each file in a
    filename list exists.

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        filenames -- List of filenames to be checked
    """
    for filename in filenames:
        if not os.path.isfile(filename):
            _, name = os.path.split(filename)
            msg = f"Arquivo compilado {name} não foi encontrado. "
            return CheckResult(CheckState.FAILED, msg)
    msg = "Compilação bem sucedida!"
    return CheckResult(CheckState.PASSED, msg)

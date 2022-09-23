from .types import parse_function, parse_ctype, get_args
from subprocess import PIPE
from collections import namedtuple
from enum import Enum
from typing import Any
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
    dll_name = filename.replace('.c', '.so')
    try:
        c_lib = ctypes.CDLL(f"./dll/{dll_name}")
    except OSError:
        msg = f"O arquivo './dll/{dll_name}' não foi encontrado."
        return CheckResult(CheckState.ERROR, msg)

    ret_type, funcname, argtypes = parse_function(check.function)
    try:
        c_func = getattr(c_lib, funcname)
    except AttributeError:
        msg = f"A função '{funcname}' não foi encontrada."
        return CheckResult(CheckState.ERROR, msg)
    c_ret_type = parse_ctype(ret_type)
    c_arg_types = [parse_ctype(x) for x in argtypes]
    c_func.restype, c_func.argtypes = c_ret_type, c_arg_types
    c_args = get_args(c_arg_types, check.input)
    if check.varpos != -1:
        c_func(*c_args)
        output = c_args[check.varpos]
    else:
        output = c_func(*c_args)
    return check.validate(output=output)


def function_validation(check: 'Check', output: Any) -> CheckResult:
    """Validation behavior to compose Check class.
    Simple check to see if output matches exactly output from function

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        output -- Stdout from run method.
    """
    APPROX = 0.2
    if abs(check.output - output) < APPROX:
        msg = "Teste concluído com sucesso! "
        return CheckResult(CheckState.PASSED, msg)
    else:
        msg = (f"Não passou. "
               f"Esperava encontrar {check.output} ± {APPROX} na saída. ")
        return CheckResult(CheckState.FAILED, msg)


def variable_validation(check: 'Check', output: Any) -> CheckResult:
    """Validation behavior to compose Check class.
    Simple check to see if variable matches expectation after function run.

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        output -- Stdout from run method.
    """
    if isinstance(check.output, list):
        output = list(output)[:len(check.output)]
    if check.output == output:
        msg = "Teste concluído com sucesso! "
        return CheckResult(CheckState.PASSED, msg)
    else:
        msg = (f"Não passou. "
               f"Esperava encontrar {check.output} na saída. "
               f" Encontrei {output}.")
        return CheckResult(CheckState.FAILED, msg)


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

    output = output.replace("\n", "")
    if check.output in output:
        msg = "Teste concluído com sucesso! "
        return CheckResult(CheckState.PASSED, msg)
    else:
        msg = (f"Não passou. Esperava encontrar '{check.output}' na saída. "
               f"\n{' ':9s}Encontrei '{output}'")
        return CheckResult(CheckState.FAILED, msg)


def compilation_run(check: 'Check') -> CheckResult:
    """Compilation run behavior to compose Check. Uses gcc for compilation.

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        dll -- Flag that defines if it will compile as dll
    """

    _, filename = os.path.split(check.file)
    os.system("rm -rf ./dll ./bin")
    os.mkdir('./bin')
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
        msg = (f"Erro ao compilar o arquivo {check.file} como executável. "
               f" {bin_result.stderr}")
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

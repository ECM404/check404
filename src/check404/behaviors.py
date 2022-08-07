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

CheckResult = namedtuple("CheckResult", ['state', 'msg'])


class CheckState(Enum):
    """Enum that stores state of a Check result."""
    ERROR = 1
    PASSED = 2
    FAILED = 3


def function_run(check: 'Check', func: str, types: List[str]) -> CheckResult:
    """Run behavior to compose Check class.
    Simple function run. Uses dll compiled from c file and runs some function
    inside of it. Can be used with io_validation.

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        function -- function that needs to be run
    """
    try:
        c_lib = ctypes.CDLL(f"./{check.file}")
    except OSError:
        msg = f"O arquivo '{check.file}' não foi encontrado."
        return CheckResult(CheckState.ERROR, msg)
    try:
        c_func = getattr(c_lib, func)
    except AttributeError:
        msg = f"A função '{func}' não foi encontrada."
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
    if check.inputs is None:
        check.inputs = []

    try:
        process = subprocess.Popen([f"./{check.file}"],
                                   stdin=PIPE,
                                   stdout=PIPE,
                                   encoding='utf-8')
    except OSError:
        msg = f"O arquivo '{check.file}' não foi encontrado."
        return CheckResult(CheckState.ERROR, msg)
    try:
        output, stderr = process.communicate(input="\n".join(check.inputs),
                                             timeout=TIMEOUT)
    except subprocess.TimeoutExpired as e:
        msg = f"Programa não respondeu após {e.timeout} segundos."
        return CheckResult(CheckState.ERROR, msg)
    return check.validate(output=output)


def iostream_validation(check: 'Check', output: str) -> CheckResult:
    """Validation behavior to compose Check class.
    Simple check to see if output matches exactly what was expected

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        output -- Stdout from run method.
    """

    if check.expect is None:
        check.expect = []
    if "".join(check.expect) in output:
        msg = "Teste concluído com sucesso!"
        return CheckResult(CheckState.PASSED, msg)
    else:
        msg = (f"Não passou. Esperava encontrar '{check.expect}' na saída."
               f"Encontrei '{output}'")
        return CheckResult(CheckState.FAILED, msg)


def compilation_run(check: 'Check', dll: bool = False) -> CheckResult:
    """Compilation run behavior to compose Check. Uses gcc for compilation.

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        dll -- Flag that defines if it will compile as dll
    """

    dirpath, filename = os.path.split(check.file)
    output_dir = "dll" if dll else "bin"
    output_ext = ".so" if dll else ".out"
    output_path = f"./{output_dir}/{filename.replace('.c', output_ext)}"
    if not dll and not os.path.isdir('./bin'):
        os.mkdir('./bin')
    elif dll and not os.path.isdir('./dll'):
        os.mkdir('./dll')
    command = ['gcc', check.file, '-o', output_path]
    flags = ['-fPIC', '-shared'] if dll else []
    result = subprocess.run(command + flags,
                            stdin=PIPE,
                            stdout=PIPE,
                            stderr=PIPE,
                            encoding='utf-8')
    if not result.returncode == 0:
        msg = (f"Não foi possível compilar o arquivo {check.file}."
               f" O erro relatado pelo gcc foi:\n{result.stderr}")
        return CheckResult(CheckState.ERROR, msg)
    return check.validate(filename=output_path)


def file_validation(check: 'Check', filename: str) -> CheckResult:
    """File validation behavior to compose Check. Checks if file exists

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        filename -- Name of file to be checked
    """

    if os.path.isfile(filename):
        msg = "Compilação bem sucedida!"
        return CheckResult(CheckState.PASSED, msg)
    else:
        msg = "Arquivo compilado não foi encontrado após compilação."
        return CheckResult(CheckState.FAILED, msg)

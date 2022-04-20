from . import testing
import subprocess
import os
from subprocess import PIPE

Check = testing.Check
CheckResult = testing.CheckResult
CheckState = testing.CheckState
TIMEOUT = testing.TIMEOUT


def iostream_run(check: Check) -> CheckResult:
    """Run behavior to compose Check class.
    Simple running behavior. Run entire program as subprocess.
    Caputres stdout to be passed as argument to validation method.

    Parameters:
        check -- Check class instance. Should be passed as 'self'
    """

    try:
        process = subprocess.Popen([f"./{check.file}"],
                                   stdin=PIPE,
                                   stdout=PIPE,
                                   encoding='utf-8')
    except OSError:
        msg = f"O arquivo '{check.file}' não foi encontrado."
        return CheckResult(CheckState.ERROR, msg)
    try:
        output, stderr = process.communicate(input=check.input,
                                             timeout=TIMEOUT)
    except subprocess.TimeoutExpired as e:
        msg = f"Programa não respondeu após {e.timeout} segundos."
        return CheckResult(CheckState.ERROR, msg)
    return check.validate(output=output)


def iostream_validation(check: Check, output: str) -> CheckResult:
    """Validation behavior to compose Check class.
    Simple check to see if output matches exactly what was expected

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        output -- Stdout from run method.
    """

    if check.expect in output:
        msg = "Teste concluído com sucesso!"
        return CheckResult(CheckState.PASSED, msg)
    else:
        msg = f"Não passou. Esperava encontrar '{check.expect}' na saída."
        return CheckResult(CheckState.FAILED, msg)


def compilation_run(check: Check, dll: bool = False) -> CheckResult:
    """Compilation run behavior to compose Check. Uses gcc for compilation.

    Parameters:
        check -- Check class instance. Should be passed as 'self'
        flags -- gcc flags to be used for compilation
    """

    dirpath, filename = os.path.split(check.file)
    output_path = f"./bin/{filename.replace('.c', '.out')}"
    if not os.path.isdir('./bin'):
        os.mkdir('./bin')
    result = subprocess.run(['gcc', check.file, '-o', output_path],
                            stdin=PIPE,
                            stdout=PIPE,
                            stderr=PIPE,
                            encoding='utf-8')
    if not result.returncode == 0:
        msg = (f"Não foi possível compilar o arquivo {check.file}."
               f" O erro relatado pelo gcc foi:\n{result.stderr}")
        return CheckResult(CheckState.ERROR, msg)
    return check.validate(filename=output_path)


def file_validation(check: Check, filename: str) -> CheckResult:
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

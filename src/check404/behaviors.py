from .testing import Check, TIMEOUT, CheckResult, CheckState
import subprocess
from subprocess import PIPE


def iostream_run(check: Check) -> CheckResult:
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
    return check.validate(output)


def iostream_validation(check: Check, output: str) -> CheckResult:
    if check.expect in output:
        msg = "Teste concluído com sucesso!"
        return CheckResult(CheckState.ERROR, msg)
    else:
        msg = f"Não passou. Esperava encontrar '{check.expect}' na saída."
        return CheckResult(CheckState.ERROR, msg)


def function_run(check: Check) -> CheckResult:
    pass


def function_validation(check: Check, output: str) -> CheckResult:
    pass

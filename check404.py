import subprocess
from subprocess import PIPE
from dataclasses import dataclass
from collections import namedtuple
from enum import Enum

GREEN = "\033[1;32;49m"
RED = "\033[1;31;49m"
WHITE = "\033[1;37;49m"
TIMEOUT = 2

CheckResult = namedtuple("CheckResult", ['state', 'msg'])


class CheckState(Enum):
    ERROR = 1
    PASSED = 2
    FAILED = 3


@dataclass
class Check():
    file: str
    input: str
    expect: str

    def run(self) -> CheckResult:
        try:
            process = subprocess.Popen([f"./{self.file}"],
                                       stdin=PIPE,
                                       stdout=PIPE,
                                       encoding='utf-8')
        except OSError as e:
            msg = f"O arquivo {e.filename[2:]} não foi encontrado."
            return CheckState.ERROR, msg
        try:
            output, stderr = process.communicate(input=self.input,
                                                 timeout=TIMEOUT)
        except subprocess.TimeoutExpired as e:
            msg = f"Programa não respondeu após {e.timeout} segundos."
            return CheckState.ERROR, msg

        if self.expect in output:
            msg = "Teste concluído com sucesso!"
            return CheckState.PASSED, msg
        else:
            msg = f"Não passou. Esperava encontrar '{self.expect}' na saída."
            return CheckState.FAILED, msg


def main():
    check = Check(file='b.out', input='5', expect='5')
    result = check.run()
    print(result)


if __name__ == "__main__":
    main()

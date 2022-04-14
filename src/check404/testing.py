from __future__ import annotations
from dataclasses import dataclass
from collections import namedtuple
from collections.abc import Callable
from enum import Enum

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
    run_behavior: Callable[[Check], CheckResult]
    validation_behavior: Callable[[Check, str], CheckResult]

    def run(self) -> CheckResult:
        return self.run_behavior(self)

    def validate(self, output) -> CheckResult:
        return self.validation_behavior(self, output)

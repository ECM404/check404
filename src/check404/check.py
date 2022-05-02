from __future__ import annotations
from typing import Any, List, Optional
from dataclasses import dataclass
from collections import namedtuple
from collections.abc import Callable
from enum import Enum

TIMEOUT = 2  # seconds

CheckResult = namedtuple("CheckResult", ['state', 'msg'])


class CheckState(Enum):
    """Enum that stores state of a Check result."""
    ERROR = 1
    PASSED = 2
    FAILED = 3


@dataclass
class Check():
    """Base class for check404 Check.

    Attributes:
        file -- Full pathname of file to be run/used as dll
        input -- Stdin to be injected into the subprocess
        expect -- Stdout expected as result from the subprocess
        run_behavior -- Function to be used in place of abstract run method
        validation_behavior -- Function used as abstract validate method
    """

    file: str
    inputs: Optional[List] = None
    expect: Optional[List] = None
    run_behavior: Callable = lambda default_function: None
    validation_behavior: Callable = lambda default_function: None

    def run(self, **kwargs: Any) -> CheckResult:
        """Abstract method implemented by run_behavior"""
        return self.run_behavior(self, **kwargs)

    def validate(self, **kwargs: Any) -> CheckResult:
        """Abstract method implemented by validation_behavior"""
        return self.validation_behavior(self, **kwargs)

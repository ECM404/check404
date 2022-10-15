from __future__ import annotations
from typing import Any
from collections.abc import Callable
from check404 import behaviors
from check404.behaviors import CheckResult, CheckState

RUN_BEHAVIORS = {
    "stdin": behaviors.iostream_run,
    "input": behaviors.function_run
}

VALIDATION_BEHAVIORS = {
    "stdout": behaviors.iostream_validation,
    "output": behaviors.function_validation,
    "varout": behaviors.variable_validation
}


class Check():
    """Base class for check404 Check.

    Attributes:
        file -- Full pathname of file to be run/used as dll
        input -- Stdin to be injected into the subprocess
        expect -- Stdout expected as result from the subprocess
        run_behavior -- Function to be used in place of abstract run method
        validation_behavior -- Function used as abstract validate method
    """

    name: str
    file: str
    weight: float
    function: str = ""
    varpos: int = -1
    input: Any = None
    output: str = ""
    result: CheckResult = CheckResult(CheckState.NONE, "Teste não foi rodado.")
    run_behavior: Callable
    validation_behavior: Callable

    def __init__(self, *args, **kwargs):
        self.name = args[0]
        self.file = kwargs["file"]
        self.weight = kwargs["weight"]
        for behavior in RUN_BEHAVIORS:
            if behavior in kwargs:
                self.input = kwargs[behavior]
                self.run_behavior = RUN_BEHAVIORS[behavior]
        if self.input is None:
            self.run_behavior = behaviors.compilation_run
        for behavior in VALIDATION_BEHAVIORS:
            if behavior in kwargs:
                self.output = kwargs[behavior]
                self.validation_behavior = VALIDATION_BEHAVIORS[behavior]
        if self.output == "":
            self.validation_behavior = behaviors.file_validation
        if "function" in kwargs:
            self.function = kwargs["function"]
        if "varpos" in kwargs:
            self.varpos = kwargs["varpos"]

    def run(self, **kwargs: Any) -> CheckResult:
        """Abstract method implemented by run_behavior"""
        self.result = self.run_behavior(self, **kwargs)
        return self.result

    def validate(self, **kwargs: Any) -> CheckResult:
        """Abstract method implemented by validation_behavior"""
        return self.validation_behavior(self, **kwargs)

    def __repr__(self) -> str:
        return (f"{self.name}(w={self.weight}, i={self.input}, o={self.output}"
                f", r={self.run_behavior}, v={self.validation_behavior})")

    def __str__(self) -> str:
        return (f"{self.name}(w={self.weight}, i={self.input}, o={self.output}"
                f", r={self.run_behavior}, v={self.validation_behavior})")

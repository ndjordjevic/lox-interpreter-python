from time import time
from typing import List, Any
from .lox_callable import LoxCallable


class NativeClock(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> float:
        """Return the current time in seconds since the epoch."""
        return time()

    def __call__(self, interpreter: 'Interpreter', arguments: List[Any]) -> float:
        return self.call(interpreter, arguments)

    def __str__(self) -> str:
        return "<native fn>"

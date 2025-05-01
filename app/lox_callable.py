from abc import ABC, abstractmethod
from typing import List, Any


class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int:
        """Returns the number of arguments this function expects."""
        pass

    @abstractmethod
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        """Execute the callable with the given arguments."""
        pass

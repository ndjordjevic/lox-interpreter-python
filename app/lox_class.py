from .lox_callable import LoxCallable
from .lox_instance import LoxInstance


class LoxClass(LoxCallable):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)
        return instance

    def arity(self):
        return 0 
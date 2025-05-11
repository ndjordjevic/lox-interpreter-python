from .lox_callable import LoxCallable
from .lox_instance import LoxInstance


class LoxClass(LoxCallable):
    def __init__(self, name, methods=None):
        self.name = name
        self.methods = methods or {}

    def __str__(self):
        return self.name

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)
        return instance

    def arity(self):
        return 0

    def find_method(self, name):
        return self.methods.get(name, None) 
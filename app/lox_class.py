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
        initializer = self.find_method("init")
        if initializer is not None:
            initializer = initializer.bind(instance)
            initializer.is_initializer = True
            return initializer.call(interpreter, arguments)
        return instance

    def arity(self):
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def find_method(self, name):
        return self.methods.get(name, None) 
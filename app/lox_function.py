from .lox_callable import LoxCallable
from .environment import Environment
from .return_exception import ReturnException


class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure, is_initializer=False):
        self.declaration = declaration  # This is a stmt.Function node
        self.closure = closure
        self.is_initializer = is_initializer

    def call(self, interpreter, arguments):
        # Create a new environment for the function call, enclosing the closure
        environment = Environment(self.closure)
        # Bind parameters to arguments
        for i in range(len(self.declaration.params)):
            param_name = self.declaration.params[i].lexeme
            environment.define(param_name, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None  # Lox functions return nil by default

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"

    def __call__(self, interpreter, arguments):
        return self.call(interpreter, arguments)

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

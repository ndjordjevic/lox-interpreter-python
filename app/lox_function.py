from .lox_callable import LoxCallable
from .environment import Environment
from .return_exception import ReturnException

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure):
        self.declaration = declaration  # This is a stmt.Function node
        self.closure = closure

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
            return return_value.value
        return None  # Lox functions return nil by default

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"

from .error_handler import RuntimeError


class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def __str__(self):
        return f"{self.klass.name} instance"

    def get(self, name):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        raise RuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name, value):
        self.fields[name.lexeme] = value 
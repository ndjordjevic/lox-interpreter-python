from .error_handler import RuntimeError


class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        """Define a new variable in the current scope."""
        self.values[name.lexeme if hasattr(name, 'lexeme') else name] = value

    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def ancestor(self, distance):
        """Get the environment at the specified distance in the chain."""
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

    def get_at(self, distance, name):
        """Get a variable's value from a specific scope depth."""
        return self.ancestor(distance).values[name if isinstance(name, str) else name.lexeme]

    def assign_at(self, distance, name, value):
        """Assign to a variable at a specific scope depth."""
        self.ancestor(distance).values[name.lexeme] = value

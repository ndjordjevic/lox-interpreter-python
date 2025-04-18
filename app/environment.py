from .error_handler import RuntimeError

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        # Store the variable by name string, not by lexeme
        self.values[name] = value

    def get(self, name):
        # Check if variable exists in current scope using lexeme
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        
        # If not found and enclosing scope exists, check there
        if self.enclosing is not None:
            return self.enclosing.get(name)
            
        # Not found anywhere
        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name, value):
        # Check if variable exists in current scope
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        
        # If not found and enclosing scope exists, try there
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        # Not found anywhere
        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

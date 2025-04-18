from .token_type import TokenType
import sys

error_state = {"had_error": False, "had_runtime_error": False}


class RuntimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token


def error(arg, message):
    if isinstance(arg, int):  # If the first argument is a line number
        report(arg, "", message)
    elif hasattr(arg, "type") and hasattr(arg, "line"):
        if arg.type == TokenType.EOF:
            report(arg.line, " at end", message)
        else:
            report(arg.line, f" at '{arg.lexeme}'", message)
    else:
        raise TypeError("Invalid argument type for error function")


def report(line, where, message):
    global error_state
    error_state["had_error"] = True
    print(f"[line {line}] Error{where}: {message}", file=sys.stderr)  # Print to stderr


def runtime_error(error):
    global error_state
    error_state["had_runtime_error"] = True
    print(f"{error}", file=sys.stderr)  # Only print the error message

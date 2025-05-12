from .token_type import TokenType
import sys

error_state = {"had_error": False, "had_runtime_error": False}


class RuntimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token


class Return(Exception):
    def __init__(self, value):
        self.value = value


def error(arg, message):
    if isinstance(arg, int):
        report_error(arg, "", message)
    elif hasattr(arg, "type") and hasattr(arg, "line"):
        if arg.type == TokenType.EOF:
            report_error(arg.line, " at end", message)
        else:
            report_error(arg.line, f" at '{arg.lexeme}'", message)
    else:
        raise TypeError("Invalid argument type for error function")


def report_error(line, where, message):
    global error_state
    error_state["had_error"] = True
    print(f"[line {line}] Error{where}: {message}", file=sys.stderr)  # Print to stderr


def report_runtime_error(error):
    global error_state
    error_state["had_runtime_error"] = True
    print(f"{error}", file=sys.stderr)  # Only print the error message

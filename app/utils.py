import sys
from app.token_type import TokenType

error_state = {"had_error": False}


def error(arg, message):
    if isinstance(arg, int):  # If the first argument is a line number
        report(arg, "", message)
    elif hasattr(arg, "type") and hasattr(arg, "line"):  # If the first argument is a Token
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

from .utils import error_state


def error(token, message):
    if token.type.name == "EOF":
        report(token.line, " at end", message)
    else:
        report(token.line, f" at '{token.lexeme}'", message)


def report(line, where, message):
    print(f"[line {line}] Error{where}: {message}")
    error_state["had_error"] = True

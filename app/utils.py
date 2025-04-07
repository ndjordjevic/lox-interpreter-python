import sys

error_state = {"had_error": False}


def error(token, message):
    if token.type == "EOF":
        report(token.line, " at end", message)
    else:
        report(token.line, f" at '{token.lexeme}'", message)


def report(line, where, message):
    global error_state
    error_state["had_error"] = True
    print(f"[line {line}] Error{where}: {message}", file=sys.stderr)  # Print to stderr


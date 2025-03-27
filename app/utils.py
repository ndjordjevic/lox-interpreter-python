import sys

error_state = {"had_error": False}


def error(line, message):
    error_state["had_error"] = True
    report(line, "", message)


def report(line, where, message):
    print(f"[line {line}] Error{where}: {message}", file=sys.stderr)

import sys

error_state = {"had_error": False}


def error(line, message):
    print(f"[line {line}] Error: {message}")


def report(line, where, message):
    print(f"[line {line}] Error{where}: {message}", file=sys.stderr)

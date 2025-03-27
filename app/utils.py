import sys

error_state = {"had_error": False}


def error(line, message):
    global error_state
    error_state["had_error"] = True  # Set the error flag
    print(f"[line {line}] Error: {message}", file=sys.stderr)  # Print to stderr


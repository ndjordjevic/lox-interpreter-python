import sys
from .scanner import Scanner
from .parser import Parser
from .interpreter import Interpreter
from .resolver import Resolver
from .error_handler import error_state

lox_interpreter = Interpreter()


def main():
    if len(sys.argv) > 2:
        print("Usage: ./your_program.sh [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()


def run_file(path):
    with open(path, "r", encoding="utf-8") as file:
        run(file.read())
    if error_state["had_error"]:
        sys.exit(65)
    if error_state["had_runtime_error"]:
        sys.exit(70)


def run_prompt():
    try:
        while True:
            line = input("> ")
            if line is None:
                break
            run(line)
            error_state["had_error"] = False
    except EOFError:
        pass


def run(source: str) -> None:
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()
    if error_state["had_error"]:
        return
    resolver = Resolver(lox_interpreter)
    resolver.resolve(statements)
    if error_state["had_error"]:
        return
    lox_interpreter.interpret(statements)


if __name__ == "__main__":
    main()

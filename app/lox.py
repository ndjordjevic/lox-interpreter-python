import sys

from .scanner import Scanner
from .ast_printer import AstPrinter
from .error_handler import error_state
from .parser import Parser
from .interpreter import Interpreter
from .stmt import Expression as StmtExpression

lox_interpreter = Interpreter()  # Static instance of the interpreter


def parse(file_contents: str):
    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)  # Use the Parser class1
    expression = parser.parse()  # Parse the tokens
    if expression:
        printer = AstPrinter()
        print(printer.print(expression))


def tokenize(file_contents: str):
    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()
    for token in tokens:
        # Print each token in the expected format
        literal = "null" if token.literal is None else token.literal
        print(f"{token.type.name} {token.lexeme} {literal}")


def evaluate(file_contents: str):
    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()

    # Parse the tokens into an expression.
    parser = Parser(tokens)
    statements = parser.parse()

    # Stop if there was a syntax error.
    if error_state["had_error"]:
        print("Error during parsing.")
        return

    # Interpret all parsed statements at once.
    lox_interpreter.interpret(statements, repl_mode=True)


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh <command> <filename>")
        sys.exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command == "tokenize":
        with open(filename, "r", encoding="utf-8") as file:
            file_contents = file.read()
        tokenize(file_contents)
    elif command == "parse":
        with open(filename, "r", encoding="utf-8") as file:
            file_contents = file.read()
        parse(file_contents)
    elif command == "evaluate":
        with open(filename, "r", encoding="utf-8") as file:
            file_contents = file.read()
        evaluate(file_contents)
    elif command == "run":
        run_file(filename)  # Use the existing run_file function
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    if error_state["had_error"]:
        sys.exit(65)

    if error_state["had_runtime_error"]:
        sys.exit(70)


def run_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        run(file.read())
        if error_state["had_error"]:
            sys.exit(65)
        if error_state["had_runtime_error"]:
            sys.exit(70)


def run_prompt():
    try:
        while True:
            line = input("> ")
            if line is None or line.strip() == "":
                break
            run(line)
            error_state["had_error"] = False
    except EOFError:
        pass


def run(source):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    # Parse the tokens into a list of statements.
    parser = Parser(tokens)
    statements = parser.parse()  # Updated to parse a list of statements

    # Stop if there was a syntax error.
    if error_state["had_error"]:
        return

    # Interpret the parsed statements.
    lox_interpreter.interpret(statements)  # Updated to interpret a list of statements


if __name__ == "__main__":
    main()

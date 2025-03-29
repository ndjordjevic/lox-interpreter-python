import sys

from .expr import Unary
from .scanner import Scanner
from .ast_printer import AstPrinter
from .utils import error_state


def parse(file_contents: str):
    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()
    expression = parse_tokens(tokens)
    if expression:
        printer = AstPrinter()
        print(printer.print(expression))


def parse_tokens(tokens):
    # Example parsing logic for unary expressions
    if tokens[0].type == "BANG":  # Assuming "BANG" represents the "!" operator
        operator = "!"
        right = parse_tokens(tokens[1:])  # Parse the right-hand side expression
        return Unary(operator, right)
    # Add logic for other expressions as needed


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh <command> <filename>")
        sys.exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    with open(filename, "r", encoding="utf-8") as file:
        file_contents = file.read()

    if command == "tokenize":
        run(file_contents)
    elif command == "parse":
        parse(file_contents)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


def run_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        run(file.read())


def run_prompt():
    try:
        while True:
            line = input("> ")
            if line is None or line.strip() == "":
                break
            run(line)
    except EOFError:
        pass


def run(source):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    # Format and print tokens
    for token in tokens:
        token_type = (
            token.type.name
        )  # Get the uppercase string representation of the token type
        literal = "null" if token.literal is None else token.literal
        print(f"{token_type} {token.lexeme} {literal}")

    # Check for errors and exit with code 65 if any occurred
    if error_state["had_error"]:
        sys.exit(65)


if __name__ == "__main__":
    main()

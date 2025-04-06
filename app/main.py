import sys

from .scanner import Scanner
from .ast_printer import AstPrinter
from .utils import error_state
from .parser import Parser


def parse(file_contents: str):
    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)  # Use the Parser class
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


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh <command> <filename>")
        sys.exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    with open(filename, "r", encoding="utf-8") as file:
        file_contents = file.read()

    if command == "tokenize":
        tokenize(file_contents)
    elif command == "parse":
        parse(file_contents)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    # Exit with code 65 if there was a syntax error.
    if error_state["had_error"]:
        sys.exit(65)


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

    # Parse the tokens into an expression.
    parser = Parser(tokens)
    expression = parser.parse()

    # Stop if there was a syntax error.
    if error_state["had_error"]:
        return

    # Print the syntax tree using AstPrinter.
    printer = AstPrinter()
    print(printer.print(expression))


if __name__ == "__main__":
    main()

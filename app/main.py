import sys
import os

# Add the parent directory of 'app' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .scanner import Scanner
from .parser import Parser  # Ensure you have a Parser class implemented in parser.py

had_error = False


def parse(file_contents: str):
    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()  # Tokenize the input
    parser = Parser(tokens)  # Pass tokens to the Parser
    print(parser.parse())


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh <command> <filename>")
        sys.exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    with open(filename, "r", encoding="utf-8") as file:
        file_contents = file.read()

    match command:
        case "tokenize":
            run(file_contents)
        case "parse":
            parse(file_contents)
        case _:
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

    # For now, just print the tokens.
    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()

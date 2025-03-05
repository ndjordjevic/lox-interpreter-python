import sys

# Define reserved words
reserved_words = {
    "and": "AND",
    "class": "CLASS",
    "else": "ELSE",
    "false": "FALSE",
    "for": "FOR",
    "fun": "FUN",
    "if": "IF",
    "nil": "NIL",
    "or": "OR",
    "print": "PRINT",
    "return": "RETURN",
    "super": "SUPER",
    "this": "THIS",
    "true": "TRUE",
    "var": "VAR",
    "while": "WHILE",
}


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command != "tokenize":
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        file_contents = file.read()

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    error = False
    i = 0
    line = 1
    while i < len(file_contents):
        c = file_contents[i]
        if c == "(":
            print("LEFT_PAREN ( null")
        elif c == ")":
            print("RIGHT_PAREN ) null")
        elif c == "{":
            print("LEFT_BRACE { null")
        elif c == "}":
            print("RIGHT_BRACE } null")
        elif c == ",":
            print("COMMA , null")
        elif c == ".":
            print("DOT . null")
        elif c == "-":
            print("MINUS - null")
        elif c == "+":
            print("PLUS + null")
        elif c == ";":
            print("SEMICOLON ; null")
        elif c == "*":
            print("STAR * null")
        elif c == "=":
            if i + 1 < len(file_contents) and file_contents[i + 1] == "=":
                print("EQUAL_EQUAL == null")
                i += 1  # Skip the next character
            else:
                print("EQUAL = null")
        elif c == "!":
            if i + 1 < len(file_contents) and file_contents[i + 1] == "=":
                print("BANG_EQUAL != null")
                i += 1  # Skip the next character
            else:
                print("BANG ! null")
        elif c == "<":
            if i + 1 < len(file_contents) and file_contents[i + 1] == "=":
                print("LESS_EQUAL <= null")
                i += 1  # Skip the next character
            else:
                print("LESS < null")
        elif c == ">":
            if i + 1 < len(file_contents) and file_contents[i + 1] == "=":
                print("GREATER_EQUAL >= null")
                i += 1  # Skip the next character
            else:
                print("GREATER > null")
        elif c == "/":
            if i + 1 < len(file_contents) and file_contents[i + 1] == "/":
                # It's a comment, skip the rest of the line
                while i < len(file_contents) and file_contents[i] != "\n":
                    i += 1
                line += 1
            else:
                print("SLASH / null")
        elif c == '"':
            start = i
            i += 1
            while i < len(file_contents) and file_contents[i] != '"':
                if file_contents[i] == "\n":
                    line += 1
                i += 1
            if i >= len(file_contents):
                error = True
                print(f"[line {line}] Error: Unterminated string.", file=sys.stderr)
            else:
                string_value = file_contents[start + 1 : i]
                print(f"STRING {file_contents[start:i + 1]} {string_value}")
        elif c.isdigit():
            start = i
            while i < len(file_contents) and file_contents[i].isdigit():
                i += 1
            if i < len(file_contents) and file_contents[i] == ".":
                i += 1
                while i < len(file_contents) and file_contents[i].isdigit():
                    i += 1
            number_value = file_contents[start:i]
            print(f"NUMBER {number_value} {float(number_value)}")
            i -= 1  # Adjust for the increment at the end of the loop
        elif c.isalpha() or c == "_":
            start = i
            while i < len(file_contents) and (
                file_contents[i].isalnum() or file_contents[i] == "_"
            ):
                i += 1
            identifier_value = file_contents[start:i]
            token_type = reserved_words.get(identifier_value, "IDENTIFIER")
            print(f"{token_type} {identifier_value} null")
            i -= 1  # Adjust for the increment at the end of the loop
        elif c in [" ", "\r", "\t"]:
            pass
        elif c == "\n":
            line += 1
        else:
            error = True
            print(f"[line {line}] Error: Unexpected character: {c}", file=sys.stderr)
        i += 1
    print("EOF  null")

    if error:
        exit(65)
    else:
        exit(0)


if __name__ == "__main__":
    main()

import sys
import typing


# Define TokenType and Token classes
class TokenType:
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    COMMA = "COMMA"
    DOT = "DOT"
    MINUS = "MINUS"
    PLUS = "PLUS"
    SEMICOLON = "SEMICOLON"
    STAR = "STAR"
    BANG = "BANG"
    BANG_EQUAL = "BANG_EQUAL"
    EQUAL = "EQUAL"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"
    SLASH = "SLASH"
    STRING = "STRING"
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    AND = "AND"
    CLASS = "CLASS"
    ELSE = "ELSE"
    FALSE = "FALSE"
    FOR = "FOR"
    FUN = "FUN"
    IF = "IF"
    NIL = "NIL"
    OR = "OR"
    PRINT = "PRINT"
    RETURN = "RETURN"
    SUPER = "SUPER"
    THIS = "THIS"
    TRUE = "TRUE"
    VAR = "VAR"
    WHILE = "WHILE"
    EOF = "EOF"


class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: typing.Any, line: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line


class Scanner:
    keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def __init__(self, source: str):
        self.source = source
        self.tokens: typing.List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.had_error = False

    @property
    def is_at_end(self):
        return self.current >= len(self.source)

    @property
    def text(self):
        return self.source[self.start : self.current]

    def scan_tokens(self):
        while not self.is_at_end:
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        character = self.advance()
        match character:
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
                )
            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS
                )
            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
                )
            case "/":
                (
                    self.advance_next_line()
                    if self.match("/")
                    else self.add_token(TokenType.SLASH)
                )
            case " ":
                pass
            case "\r":
                pass
            case "\t":
                pass
            case "\n":
                self.line += 1
            case '"':
                self.string()
            case _:
                if self.is_number(character):
                    self.number()
                elif self.is_alpha(character):
                    self.identifier()
                else:
                    self.error(self.line, f"Unexpected character: {character}")

    def peek(self, n=0):
        index = self.current + n
        if index >= len(self.source):
            return "\0"
        return self.source[index]

    def advance(self):
        index = self.current
        self.current += 1
        return self.source[index]

    def match(self, expected: str):
        if self.is_at_end:
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def advance_next_line(self):
        while self.peek() != "\n" and not self.is_at_end:
            self.advance()

    def add_token(self, type: TokenType, literal: typing.Any = None):
        self.tokens.append(Token(type, self.text, literal, self.line))

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        self.had_error = True

    def string(self):
        while self.peek() != '"' and not self.is_at_end:
            if self.peek() == "\n":
                self.line += 1
            self.advance()
        if self.is_at_end:
            self.error(self.line, "Unterminated string.")
            return
        # closing "
        self.advance()
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.is_number(self.peek()):
            self.advance()
        if self.peek() == "." and self.is_number(self.peek(1)):
            # consume .
            self.advance()
            while self.is_number(self.peek()):
                self.advance()
        value = float(self.text)
        self.add_token(TokenType.NUMBER, value)

    def identifier(self):
        while self.is_alpha_or_number(self.peek()):
            self.advance()
        type = self.keywords.get(self.text, TokenType.IDENTIFIER)
        self.add_token(type)

    def is_number(self, character: str):
        return character.isnumeric()

    def is_alpha(self, character: str):
        return character.isalpha() or character == "_"

    def is_alpha_or_number(self, character: str):
        return self.is_number(character) or self.is_alpha(character)


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

    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()

    for token in tokens:
        literal = token.literal
        if literal is None:
            literal = "null"
        print(f"{token.type} {token.lexeme} {literal}")

    if scanner.had_error:
        exit(65)
    else:
        exit(0)


if __name__ == "__main__":
    main()

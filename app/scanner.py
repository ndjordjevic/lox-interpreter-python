from .token import Token
from .token_type import TokenType
from .utils import error


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

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

    def scan_tokens(self):
        while not self.is_at_end():
            # We are at the beginning of the next lexeme.
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def scan_token(self):
        c = self.advance()
        if c == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif c == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ",":
            self.add_token(TokenType.COMMA)
        elif c == ".":
            self.add_token(TokenType.DOT)
        elif c == "-":
            self.add_token(TokenType.MINUS)
        elif c == "+":
            self.add_token(TokenType.PLUS)
        elif c == ";":
            self.add_token(TokenType.SEMICOLON)
        elif c == "*":
            self.add_token(TokenType.STAR)
        elif c == "!":
            self.add_token(TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG)
        elif c == "=":
            self.add_token(
                TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
            )
        elif c == "<":
            self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
        elif c == ">":
            self.add_token(
                TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
            )
        elif c == "/":
            if self.match("/"):
                # A single-line comment goes until the end of the line.
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            elif self.match("*"):
                # A multiline comment goes until "*/".
                while not self.is_at_end():
                    if self.peek() == "*" and self.peek_next() == "/":
                        self.advance()  # Consume '*'
                        self.advance()  # Consume '/'
                        break
                    if self.peek() == "\n":
                        self.line += 1
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c in {" ", "\r", "\t"}:
            # Ignore whitespace.
            pass
        elif c == "\n":
            self.line += 1
        elif c == '"':
            self.string()
        elif self.is_digit(c):
            self.number()
        elif self.is_alpha(c):
            self.identifier()
        else:
            error(self.line, f"Unexpected character: {c}")

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def get_current_lexeme(self):
        return self.source[self.start : self.current]

    def add_token(self, type, literal=None):
        text = self.get_current_lexeme()
        self.tokens.append(Token(type, text, literal, self.line))

    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            error(self.line, "Unterminated string.")  # Report the error
            return  # Stop further tokenization

        # The closing quote
        self.advance()

        # Trim the surrounding quotes
        value = self.get_current_lexeme()[1:-1]
        self.add_token(TokenType.STRING, value)

    def is_digit(self, c):
        return "0" <= c <= "9"

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        # Look for a fractional part.
        if self.peek() == "." and self.is_digit(self.peek_next()):
            # Consume the "."
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        # Add the number token.
        self.add_token(TokenType.NUMBER, float(self.get_current_lexeme()))

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()

        # Check if the identifier matches a reserved keyword.
        text = self.get_current_lexeme()
        type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(type)

    def is_alpha(self, c):
        return ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_"

    def is_alphanumeric(self, c):
        return self.is_alpha(c) or self.is_digit(c)

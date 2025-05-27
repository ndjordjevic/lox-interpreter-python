from .token import Token
from .token_type import TokenType
from .error_handler import error


class Scanner:
    """Scans source code and converts it into a list of tokens for the interpreter.
    
    Attributes:
        source (str): The input source code to scan.
        tokens (list[Token]): List of tokens generated during scanning.
        start (int): Starting index of the current lexeme being scanned.
        current (int): Current index being scanned in the source.
        line (int): Current line number in the source (for error reporting).
    """

    def __init__(self, source: str):
        """Initializes the scanner with source code.
        
        Args:
            source: The source code string to tokenize.
        """
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

    def scan_tokens(self) -> list[Token]:
        """Scans the entire source code and generates tokens.
        
        Returns:
            A list of tokens representing the source code.
        """
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self) -> bool:
        """Checks if the scanner has reached the end of the source.
        
        Returns:
            True if scanning is complete, False otherwise.
        """
        return self.current >= len(self.source)

    def scan_token(self) -> None:
        """Processes the next character and generates a token."""
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
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            elif self.match("*"):
                while not self.is_at_end():
                    if self.peek() == "*" and self.peek_next() == "/":
                        self.advance()
                        self.advance()
                        break
                    if self.peek() == "\n":
                        self.line += 1
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c in {" ", "\r", "\t"}:
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

    def advance(self) -> str:
        """Consumes the next character in the source.
        
        Returns:
            The consumed character.
        """
        self.current += 1
        return self.source[self.current - 1]

    def get_current_lexeme(self) -> str:
        """Extracts the current lexeme being scanned.
        
        Returns:
            The substring from start to current position.
        """
        return self.source[self.start : self.current]

    def add_token(self, type: TokenType, literal=None) -> None:
        """Adds a token to the tokens list.
        
        Args:
            type: The TokenType of the token.
            literal: Optional literal value (e.g., string or number).
        """
        text = self.get_current_lexeme()
        self.tokens.append(Token(type, text, literal, self.line))

    def match(self, expected: str) -> bool:
        """Conditionally consumes a character if it matches the expected value.
        
        Args:
            expected: The character to match against.
            
        Returns:
            True if matched, False otherwise.
        """
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self) -> str:
        """Looks at the next character without consuming it.
        
        Returns:
            The next character, or '\\0' if at end.
        """
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def string(self) -> None:
        """Scans a string literal until the closing quote."""
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            error(self.line, "Unterminated string.")
            return

        self.advance()
        value = self.get_current_lexeme()[1:-1]
        self.add_token(TokenType.STRING, value)

    def is_digit(self, c: str) -> bool:
        """Checks if a character is a digit (0-9).
        
        Args:
            c: The character to check.
            
        Returns:
            True if the character is a digit, False otherwise.
        """
        return "0" <= c <= "9"

    def number(self) -> None:
        """Scans a numeric literal (integer or float)."""
        while self.is_digit(self.peek()):
            self.advance()

        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.get_current_lexeme()))

    def peek_next(self) -> str:
        """Looks at the character after the next one (two characters ahead).
        
        Returns:
            The character or '\\0' if out of bounds.
        """
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def identifier(self) -> None:
        """Scans an identifier or reserved keyword."""
        while self.is_alphanumeric(self.peek()):
            self.advance()

        text = self.get_current_lexeme()
        type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(type)

    def is_alpha(self, c: str) -> bool:
        """Checks if a character is alphabetic (a-z, A-Z) or underscore.
        
        Args:
            c: The character to check.
            
        Returns:
            True if valid, False otherwise.
        """
        return ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_"

    def is_alphanumeric(self, c: str) -> bool:
        """Checks if a character is alphanumeric (a-z, A-Z, 0-9) or underscore.
        
        Args:
            c: The character to check.
            
        Returns:
            True if valid, False otherwise.
        """
        return self.is_alpha(c) or self.is_digit(c)

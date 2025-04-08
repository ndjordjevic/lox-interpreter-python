from .expr import Visitor, Binary, Grouping, Literal, Unary
from .token import Token
from .token_type import TokenType


class AstPrinter(Visitor):
    def print(self, expr):
        return expr.accept(self)  # Delegate to the visitor methods

    def visit_binary(self, binary):
        return self.parenthesize(binary.operator.lexeme, binary.left, binary.right)

    def visit_grouping(self, grouping):
        return self.parenthesize("group", grouping.expression)

    def visit_literal(self, literal):
        if isinstance(literal.value, bool):  # Handle boolean values
            return "true" if literal.value else "false"
        if literal.value is None:  # Handle nil values
            return "nil"
        return str(literal.value)  # Handle numbers and strings

    def visit_unary(self, unary):
        return self.parenthesize(unary.operator.lexeme, unary.right)

    def parenthesize(self, name, *exprs):
        builder = []
        builder.append(f"({name}")
        for expr in exprs:
            builder.append(" ")
            builder.append(expr.accept(self))
        builder.append(")")
        return "".join(builder)


# Temporary main function to see how it works
if __name__ == "__main__":
    # Create Token objects for the operators
    minus_token = Token(TokenType.MINUS, "-", None, 1)
    star_token = Token(TokenType.STAR, "*", None, 1)

    # Construct the expression using Token objects
    expression = Binary(
        Unary(minus_token, Literal(123)), star_token, Grouping(Literal(45.67))
    )

    print(AstPrinter().print(expression))

import sys
import os

# Add the parent directory of 'app' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.expr import Visitor, Binary, Grouping, Literal, Unary


class RpnPrinter(Visitor):
    def print(self, expr):
        return expr.accept(self)

    def visit_binary(self, binary):
        left = binary.left.accept(self)
        right = binary.right.accept(self)
        return f"{left} {right} {binary.operator}"

    def visit_grouping(self, grouping):
        return grouping.expression.accept(self)

    def visit_literal(self, literal):
        if literal.value is None:
            return "nil"
        return str(literal.value)

    def visit_unary(self, unary):
        right = unary.right.accept(self)
        return f"{right} {unary.operator}"


# Temporary main function to see how it works
if __name__ == "__main__":
    expression = Binary(
        Binary(Literal(1), "+", Literal(2)), "*", Binary(Literal(4), "-", Literal(3))
    )

    print(RpnPrinter().print(expression))
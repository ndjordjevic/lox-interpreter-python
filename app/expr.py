class Visitor:
    def visit_binary(self, binary):
        pass

    def visit_grouping(self, grouping):
        pass

    def visit_literal(self, literal):
        pass

    def visit_unary(self, unary):
        pass


class Binary:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary(self)


class Grouping:
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping(self)


class Literal:
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal(self)


class Unary:
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary(self)


class Evaluator(Visitor):
    def visit_binary(self, binary):
        left = binary.left.accept(self)
        right = binary.right.accept(self)
        if binary.operator == "+":
            return left + right
        elif binary.operator == "-":
            return left - right
        elif binary.operator == "*":
            return left * right
        elif binary.operator == "/":
            return left / right
        # Add more operators as needed

    def visit_grouping(self, grouping):
        return grouping.expression.accept(self)

    def visit_literal(self, literal):
        return literal.value

    def visit_unary(self, unary):
        right = unary.right.accept(self)
        if unary.operator == "-":
            return -right
        elif unary.operator == "!":  # Add support for '!'
            return not right


# Temporary main function to see how it works
if __name__ == "__main__":
    # Create a unary expression: -123
    unary_expression = Unary("-", Literal(123))

    # Create a grouping expression: (45.67)
    grouping_expression = Grouping(Literal(45.67))

    # Combine the unary and grouping expressions into a binary expression: (-123) * (45.67)
    expression = Binary(unary_expression, "*", grouping_expression)

    evaluator = Evaluator()
    result = expression.accept(evaluator)
    print(result)  # Expected output: -123 * 45.67 = -5615.41

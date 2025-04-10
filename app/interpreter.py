from app.expr import Visitor


class RuntimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token


class Interpreter(Visitor):

    def visit_literal(self, expr):
        return expr.value

    def visit_grouping(self, expr):
        return self.evaluate(expr.expression)

    def evaluate(self, expr):
        if expr is None:
            return None
        return expr.accept(self)

    def visit_unary(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator.type == "MINUS":
            self.check_number_operand(expr.operator, right)
            return -float(right)  # Ensure numeric negation is applied
        elif expr.operator.type == "BANG":
            return not self.is_truthy(right)

        # Unreachable
        return None

    def visit_binary(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.type == "MINUS":
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        elif expr.operator.type == "SLASH":
            self.check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        elif expr.operator.type == "STAR":
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        elif expr.operator.type == "PLUS":
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeError(
                expr.operator, "Operands must be two numbers or two strings."
            )
        elif expr.operator.type == "GREATER":
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        elif expr.operator.type == "GREATER_EQUAL":
            self.check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        elif expr.operator.type == "LESS":
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        elif expr.operator.type == "LESS_EQUAL":
            self.check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        elif expr.operator.type == "BANG_EQUAL":
            return not self.is_equal(left, right)
        elif expr.operator.type == "EQUAL_EQUAL":
            return self.is_equal(left, right)

        # Unreachable
        return None

    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return
        raise RuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise RuntimeError(operator, "Operands must be numbers.")

    def is_equal(self, a, b):
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def is_truthy(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True

    def interpret(self, expression):
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))
        except RuntimeError as error:
            self.runtime_error(error)

    def stringify(self, obj):
        if obj is None:
            return "nil"

        if isinstance(obj, bool):
            return "true" if obj else "false"

        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text

        return str(obj)

    def runtime_error(self, error):
        # Placeholder for handling runtime errors
        print(f"[Runtime Error] {error}")

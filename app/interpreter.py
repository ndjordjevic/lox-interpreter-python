from .stmt import Visitor as StmtVisitor
from .expr import Visitor as ExprVisitor
from .token_type import TokenType
from .error_handler import report_runtime_error, RuntimeError
from .environment import Environment
from .lox_callable import LoxCallable
from .native_functions import NativeClock
from app.lox_instance import LoxInstance


from .lox_function import LoxFunction
from .return_exception import ReturnException
from .lox_class import LoxClass


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}  # Map to store resolved variable depths
        self.repl_mode = False

        # Define native functions
        self.globals.define("clock", NativeClock())

    def interpret(self, statements, repl_mode=False):
        self.repl_mode = repl_mode
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as error:
            report_runtime_error(error)

    def resolve(self, expr, depth):
        """Store a resolved variable's scope depth."""
        self.locals[expr] = depth

    def evaluate(self, expr):
        return expr.accept(self)

    def execute(self, stmt):
        stmt.accept(self)

    def visit_block_stmt(self, stmt):
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def visit_class_stmt(self, stmt):
        self.environment.define(stmt.name.lexeme, None)

        methods = {}
        for method in stmt.methods:
            function = LoxFunction(method, self.environment, 
                                 method.name.lexeme == "init")
            methods[method.name.lexeme] = function

        klass = LoxClass(stmt.name.lexeme, methods)
        self.environment.assign(stmt.name, klass)
        return None

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_expression_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        # Print the result only if in REPL/evaluate mode
        if self.repl_mode:
            print(self.stringify(value))
        return None

    def visit_if_stmt(self, stmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None

    def visit_return_stmt(self, stmt):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise ReturnException(value)

    def visit_while_stmt(self, stmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None

    def visit_function_stmt(self, stmt):
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return None

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)

        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)
        elif expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)

        return None

    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise RuntimeError(
                expr.paren,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.",
            )

        return callee.call(self, arguments)

    def visit_get_expr(self, expr):
        object = self.evaluate(expr.object)
        if isinstance(object, LoxInstance):
            return object.get(expr.name)

        raise RuntimeError(expr.name, "Only instances have properties.")

    def visit_set_expr(self, expr):
        object = self.evaluate(expr.object)

        if not isinstance(object, LoxInstance):
            raise RuntimeError(expr.name, "Only instances have fields.")

        value = self.evaluate(expr.value)
        object.set(expr.name, value)
        return value

    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        elif expr.operator.type == TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        elif expr.operator.type == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        elif expr.operator.type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeError(
                expr.operator, "Operands must be two numbers or two strings."
            )
        elif expr.operator.type == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)  # Restored correct comparison
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        elif expr.operator.type == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        elif expr.operator.type == TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        elif expr.operator.type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

        return None

    def visit_variable_expr(self, expr):
        return self.look_up_variable(expr.name, expr)

    def visit_logical_expr(self, expr):
        left = self.evaluate(expr.left)

        # For 'or', if the left operand is truthy, we can short-circuit and return it
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        # For 'and', if the left operand is falsey, we can short-circuit and return it
        else:  # TokenType.AND
            if not self.is_truthy(left):
                return left

        # If we couldn't short-circuit, evaluate and return the right operand
        return self.evaluate(expr.right)

    def visit_this_expr(self, expr):
        return self.look_up_variable(expr.keyword, expr)

    def look_up_variable(self, name, expr):
        """Look up a variable using its resolved scope depth if available."""
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        return self.globals.get(name)

    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return
        raise RuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator, left, right):
        if not (isinstance(left, float) and isinstance(right, float)):
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

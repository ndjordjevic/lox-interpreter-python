from enum import Enum, auto
from typing import Dict, List
from app.expr import Expr, Visitor as ExprVisitor
from app.stmt import Stmt, Visitor as StmtVisitor, Block, Var, Function
from app.interpreter import Interpreter
from app.token import Token
from app.error_handler import error


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    METHOD = auto()
    INITIALIZER = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes: List[Dict[str, bool]] = [{}]  # Always have a global scope
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def resolve(self, statements: List[Stmt]) -> None:
        """Resolve a list of statements."""
        for statement in statements:
            self._resolve_stmt(statement)

    def _resolve_stmt(self, stmt: Stmt) -> None:
        """Resolve a single statement."""
        stmt.accept(self)

    def _resolve_expr(self, expr: Expr) -> None:
        """Resolve a single expression."""
        expr.accept(self)

    def _begin_scope(self) -> None:
        """Create a new scope."""
        self.scopes.append({})

    def _end_scope(self) -> None:
        """Remove the most recently added scope."""
        self.scopes.pop()

    def _declare(self, name: Token) -> None:
        """Declare a variable in the current scope.

        This adds the variable to the innermost scope to shadow any outer one,
        but marks it as "not ready yet" by binding its name to false.
        """
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope:
            error(name, "Already a variable with this name in this scope.")
            return
        scope[name.lexeme] = False

    def _define(self, name: Token) -> None:
        """Define a variable in the current scope.

        This marks the variable as ready for use by setting its value to true
        in the scope map.
        """
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    def _resolve_local(self, expr: Expr, name: Token) -> None:
        """Resolve a local variable in the current scope chain.

        If we find the variable, we tell the interpreter how many scopes there are between
        the current scope and the scope where the variable is found.
        If we walk through all scopes and never find it, we assume it's global.
        """
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def visit_block_stmt(self, stmt: Block) -> None:
        """Visit a block statement."""
        self._begin_scope()
        self.resolve(stmt.statements)
        self._end_scope()
        return None

    def visit_class_stmt(self, stmt: Stmt) -> None:
        """Visit a class declaration."""
        self._declare(stmt.name)
        self._define(stmt.name)

        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        if (
            stmt.superclass is not None
            and stmt.name.lexeme == stmt.superclass.name.lexeme
        ):
            error(stmt.superclass.name, "A class can't inherit from itself.")

        if stmt.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            self._resolve_expr(stmt.superclass)

            self._begin_scope()
            self.scopes[-1]["super"] = True

        self._begin_scope()
        self.scopes[-1]["this"] = True
        method_names = set()
        for method in stmt.methods:
            if method.name.lexeme in method_names:
                error(
                    method.name,
                    f"Method '{method.name.lexeme}' is already defined in this class.",
                )
            method_names.add(method.name.lexeme)

            # Determine if this is an initializer
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER

            self._resolve_function(method, declaration)
        self._end_scope()

        if stmt.superclass is not None:
            self._end_scope()

        self.current_class = enclosing_class
        return None

    def visit_var_stmt(self, stmt: Var) -> None:
        """Visit a variable declaration statement."""
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve_expr(stmt.initializer)
        self._define(stmt.name)
        return None

    def visit_variable_expr(self, expr: Expr) -> None:
        """Visit a variable expression."""
        if self.scopes and self.scopes[-1].get(expr.name.lexeme) is False:
            error(expr.name, f"Can't read local variable in its own initializer.")
            return

        declared = False
        for scope in reversed(self.scopes):
            if expr.name.lexeme in scope:
                declared = True
                break
        if not declared and self.scopes:
            error(expr.name, f"Variable '{expr.name.lexeme}' used before declaration.")
            return

        self._resolve_local(expr, expr.name)
        return None

    def visit_assign_expr(self, expr: Expr) -> None:
        """Visit an assignment expression."""
        self._resolve_expr(expr.value)
        self._resolve_local(expr, expr.name)
        return None

    def visit_function_stmt(self, stmt: Function) -> None:
        """Visit a function declaration."""
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt, FunctionType.FUNCTION)
        return None

    def _resolve_function(self, function: Function, type: FunctionType) -> None:
        """Resolve a function's body."""
        enclosing_function = self.current_function
        self.current_function = type

        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)
        self.resolve(function.body)
        self._end_scope()

        self.current_function = enclosing_function

    def visit_expression_stmt(self, stmt: Stmt) -> None:
        """Visit an expression statement."""
        self._resolve_expr(stmt.expression)
        return None

    def visit_if_stmt(self, stmt: Stmt) -> None:
        """Visit an if statement."""
        self._resolve_expr(stmt.condition)
        self._resolve_stmt(stmt.then_branch)
        if stmt.else_branch is not None:
            self._resolve_stmt(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt: Stmt) -> None:
        """Visit a print statement."""
        self._resolve_expr(stmt.expression)
        return None

    def visit_return_stmt(self, stmt: Stmt) -> None:
        """Visit a return statement."""
        if self.current_function == FunctionType.NONE:
            error(stmt.keyword, "Can't return from top-level code.")
            return
        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                error(stmt.keyword, "Can't return a value from an initializer.")
            self._resolve_expr(stmt.value)
        return None

    def visit_while_stmt(self, stmt: Stmt) -> None:
        """Visit a while statement."""
        self._resolve_expr(stmt.condition)
        self._resolve_stmt(stmt.body)
        return None

    def visit_binary_expr(self, expr: Expr) -> None:
        """Visit a binary expression."""
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)
        return None

    def visit_call_expr(self, expr: Expr) -> None:
        """Visit a call expression."""
        self._resolve_expr(expr.callee)
        for argument in expr.arguments:
            self._resolve_expr(argument)
        return None

    def visit_get_expr(self, expr: Expr) -> None:
        """Visit a get expression."""
        self._resolve_expr(expr.object)
        return None

    def visit_grouping_expr(self, expr: Expr) -> None:
        """Visit a grouping expression."""
        self._resolve_expr(expr.expression)
        return None

    def visit_literal_expr(self, expr: Expr) -> None:
        """Visit a literal expression."""
        return None

    def visit_logical_expr(self, expr: Expr) -> None:
        """Visit a logical expression."""
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)
        return None

    def visit_set_expr(self, expr: Expr) -> None:
        """Visit a set expression."""
        self._resolve_expr(expr.value)
        self._resolve_expr(expr.object)
        return None

    def visit_unary_expr(self, expr: Expr) -> None:
        """Visit a unary expression."""
        self._resolve_expr(expr.right)
        return None

    def visit_this_expr(self, expr: Expr) -> None:
        """Visit a this expression."""
        if self.current_class == ClassType.NONE:
            error(expr.keyword, "Can't use 'this' outside of a class.")
            return
        self._resolve_local(expr, expr.keyword)
        return None

    def visit_super_expr(self, expr: Expr) -> None:
        """Visit a super expression."""
        if self.current_class == ClassType.NONE:
            error(expr.keyword, "Can't use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            error(expr.keyword, "Can't use 'super' in a class with no superclass.")
            
        self._resolve_local(expr, expr.keyword)
        return None

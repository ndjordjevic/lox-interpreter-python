# Lox Interpreter in Python

This project is a Python implementation of a tree-walk interpreter for the [Lox language](https://craftinginterpreters.com/the-lox-language.html), inspired by the book [Crafting Interpreters](https://craftinginterpreters.com/) by Robert Nystrom. It was developed as part of my learning journey in Python programming and to deepen my understanding of interpreter architecture and language implementation.

## Project Purpose & Learning Goals

- **Learn Python**: Practice advanced Python programming, OOP, and modular design.
- **Understand Interpreters**: Explore the architecture and implementation of a tree-walk interpreter.
- **Language Design**: Gain hands-on experience with tokenization, parsing, static analysis, and execution of a custom language.

## How It Works

The interpreter is organized into several key components:

### 1. Scanner (Lexer)
- **File:** `app/scanner.py`
- **Purpose:** Converts raw source code into a stream of tokens (keywords, identifiers, literals, operators, etc.).
- **Details:** Handles single-line and multi-line comments, string and number literals, and recognizes reserved keywords.

### 2. Parser
- **File:** `app/parser.py`
- **Purpose:** Consumes the token stream and builds an Abstract Syntax Tree (AST) representing the program structure.
- **Details:** Implements recursive descent parsing for expressions, statements, control flow, functions, and classes.

### 3. Resolver (Static Analysis)
- **File:** `app/resolver.py`
- **Purpose:** Performs static analysis to resolve variable scopes, detect errors like using variables before initialization, and handle class/function resolution.
- **Details:** Walks the AST before execution to annotate variable usage and scope depth.

### 4. Interpreter (Tree-Walk Execution)
- **File:** `app/interpreter.py`
- **Purpose:** Walks the AST and executes statements and expressions according to Lox semantics.
- **Details:** Supports variables, functions, classes, inheritance, control flow, and native functions (e.g., `clock`).

### 5. Environment (Scope Management)
- **File:** `app/environment.py`
- **Purpose:** Manages variable scopes and lifetimes using a chain of environments for lexical scoping.

### 6. AST Printer (Debugging/Visualization)
- **File:** `app/ast_printer.py`
- **Purpose:** Provides a way to print or visualize the AST for debugging and learning.

### 7. Error Handling
- **File:** `app/error_handler.py`
- **Purpose:** Centralizes error reporting for syntax and runtime errors.

## Entry Point
- The main entry point is in `app/lox.py`, which provides both a REPL and script execution mode.
- Run the interpreter with `./your_program.sh [script]` or interactively with no arguments.

## How to Run
1. Ensure you have Python 3.12+ installed.
2. Run the interpreter:
   ```sh
   ./your_program.sh [script]
   ```
   Or start the REPL (interactive mode):
   ```sh
   ./your_program.sh
   ```

## REPL Mode

If you run `./your_program.sh` with no arguments, it will start an interactive Lox REPL. You can type Lox statements and see their results immediately.

## How to Test
- Unit tests are provided for all major components (scanner, parser, interpreter, etc.).
- To run all tests:
  ```sh
  python3 -m unittest discover -s tests -p "*.py"
  ```
- To run a specific test file:
  ```sh
  python3 -m unittest tests/test_scanner.py
  ```

## How to Run Test Coverage
- To measure test coverage and see a summary in the terminal:
  ```sh
  coverage run -m unittest discover -s tests -p "*.py"
  coverage report
  ```
- To generate and view an HTML coverage report:
  ```sh
  coverage html
  # Then open htmlcov/index.html in your browser
  ```

## References
- [Crafting Interpreters](https://craftinginterpreters.com/) by Robert Nystrom
- [Lox Language Specification](https://craftinginterpreters.com/the-lox-language.html)

## Examples

A variety of example Lox programs are provided in the `examples/` folder. These demonstrate data structures, algorithms, and language features. Example files include:

- all_in_one.lox
- binary_tree.lox
- calculator.lox
- counter_closure.lox
- doubly_linked_list.lox
- factorial.lox
- fibonacci.lox
- fibonacci_loop.lox
- hello_world.lox
- inheritance_super_this.lox
- linked_list_count.lox
- linked_list_max_min.lox
- linked_list_search.lox
- linked_list_sort.lox
- list.lox
- queue.lox
- stack.lox
- temperature_converter.lox

You can run any of these with:

```sh
./your_program.sh examples/<example_file>
```

---

This project is a personal learning exercise and a demonstration of building a programming language interpreter from scratch in Python. Contributions and suggestions are welcome!

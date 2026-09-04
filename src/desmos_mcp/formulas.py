"""Build SymPy expressions from a small AST whitelist; never eval user input."""

import ast
import math
import re

import sympy as sp

X = sp.Symbol("x", real=True)
FUNCTIONS = {
    name: getattr(sp, name)
    for name in ("sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh", "exp", "log")
}
FUNCTIONS.update({"sqrt": sp.sqrt, "abs": sp.Abs, "Abs": sp.Abs, "ln": sp.log})
CONSTANTS = {"x": X, "pi": sp.pi, "e": sp.E, "E": sp.E}


def parse_formula(formula: str) -> sp.Expr:
    if not isinstance(formula, str) or not formula.strip() or len(formula) > 500:
        raise ValueError("Enter a non-empty formula of at most 500 characters, e.g. y = sin(x).")
    source = re.sub(r"^\s*y\s*=\s*", "", formula.strip()).replace("^", "**").replace("π", "pi")
    try:
        tree = ast.parse(source, mode="eval")
    except (SyntaxError, RecursionError) as exc:
        raise ValueError("Use x^2, sin(x), or y = 2*x + 1. Write multiplication explicitly as *.") from exc
    if sum(1 for _ in ast.walk(tree)) > 100:
        raise ValueError("Formula is too complex; split it into simpler expressions.")

    def build(node: ast.AST, depth: int = 0) -> sp.Expr:
        if depth > 16:
            raise ValueError("Formula nesting is too deep (maximum 16).")
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if not math.isfinite(node.value) or abs(node.value) > 1_000_000:
                raise ValueError("Numeric literals must be finite and at most 1,000,000 in magnitude.")
            return sp.Number(node.value)
        if isinstance(node, ast.Name) and node.id in CONSTANTS:
            return CONSTANTS[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = build(node.operand, depth + 1)
            return value if isinstance(node.op, ast.UAdd) else sp.Mul(-1, value, evaluate=False)
        if isinstance(node, ast.BinOp):
            a, b = build(node.left, depth + 1), build(node.right, depth + 1)
            if isinstance(node.op, ast.Add):
                return sp.Add(a, b, evaluate=False)
            if isinstance(node.op, ast.Sub):
                return sp.Add(a, sp.Mul(-1, b, evaluate=False), evaluate=False)
            if isinstance(node.op, ast.Mult):
                return sp.Mul(a, b, evaluate=False)
            if isinstance(node.op, ast.Div):
                return sp.Mul(a, sp.Pow(b, -1, evaluate=False), evaluate=False)
            if isinstance(node.op, ast.Pow):
                exponent_node = node.right
                while isinstance(exponent_node, ast.UnaryOp):
                    exponent_node = exponent_node.operand
                if isinstance(exponent_node, ast.Constant) and abs(exponent_node.value) > 100:
                    raise ValueError("Numeric exponents must be between -100 and 100.")
                return sp.Pow(a, b, evaluate=False)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in FUNCTIONS
            and len(node.args) == 1
            and not node.keywords
        ):
            return FUNCTIONS[node.func.id](build(node.args[0], depth + 1), evaluate=False)
        raise ValueError(
            "Supported syntax: numbers, x, pi, e, + - * / ^, and single-argument math functions. "
            "Use create_interactive_graph for Desmos LaTeX, sliders, or implicit equations."
        )

    return build(tree.body)


def validate_range(values: list[float] | None, default: tuple[float, float] | None = None):
    if values is None:
        return list(default) if default else None
    if (
        len(values) != 2
        or any(not math.isfinite(v) for v in values)
        or values[0] >= values[1]
        or any(abs(v) > 1e6 for v in values)
    ):
        raise ValueError("A range must contain two finite increasing numbers within [-1e6, 1e6], e.g. [-10, 10].")
    return values

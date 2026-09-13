"""Compare two Python files structurally, ignoring comments and docstrings.

Usage: python tools/ast_compare.py before.py after.py
Exit code 0 when the code (everything except comments and docstrings) is identical.
"""
import ast
import sys


def strip_docstrings(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                node.body = body[1:] or [ast.Pass()]
    return tree


def canon(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    return ast.dump(strip_docstrings(tree), include_attributes=False)


if __name__ == "__main__":
    a, b = sys.argv[1], sys.argv[2]
    same = canon(a) == canon(b)
    print("IDENTICAL" if same else "DIFFERENT", a, b)
    sys.exit(0 if same else 1)

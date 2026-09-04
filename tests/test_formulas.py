import pytest
import sympy as sp

from desmos_mcp.formulas import X, parse_formula, validate_range
from desmos_mcp.worker import analyze


@pytest.mark.parametrize(
    "formula,value",
    [
        ("y = x^2", 4),
        ("2*x+1", 5),
        ("sin(pi/2)", 1),
        ("sqrt(x)", sp.sqrt(2)),
        ("abs(-x)", 2),
        ("log(e)", 1),
        ("cos(π)", -1),
        ("3", 3),
    ],
)
def test_formulas(formula, value):
    assert sp.simplify(parse_formula(formula).subs(X, 2) - value) == 0


@pytest.mark.parametrize(
    "formula",
    [
        "",
        "2x",
        "__import__('os').system('echo unsafe')",
        "x.__class__",
        "[x]",
        "lambda: 1",
        "True",
        "1e999",
        "x^101",
        "x^(-101)",
        "z+1",
        "sin(x, x)",
        "sin(x=1)",
        "x" * 501,
    ],
)
def test_reject_unsafe_or_unsupported_inputs(formula):
    with pytest.raises(ValueError):
        parse_formula(formula)


@pytest.mark.parametrize("values", [[], [1], [1, 2, 3], [2, 1], [1, 1], [0, float("nan")], [0, float("inf")]])
def test_reject_bad_ranges(values):
    with pytest.raises(ValueError):
        validate_range(values)


def test_real_analysis_and_corner():
    result = analyze("x^3-3*x", "detailed")
    assert result["domain"] == "Reals"
    assert result["range"] == "Interval(-oo, oo)"
    assert result["stationary_points"] == "{-1, 1}"
    corner = analyze("abs(x)", "critical_points")
    assert corner["nondifferentiable_candidates"] == "{0}"
    assert corner["stationary_points"] == "EmptySet"
    smooth = analyze("abs(x^2)", "critical_points")
    assert smooth["nondifferentiable_candidates"] == "EmptySet"
    assert smooth["stationary_points"] == "{0}"


def test_domain_is_not_cancelled_away():
    result = analyze("x/x", "basic")
    assert "0" in result["domain"] and result["domain"] != "Reals"

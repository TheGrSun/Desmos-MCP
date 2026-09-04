"""Disposable calculation process. stdout contains one JSON response only."""

import base64
import io
import json
import sys
import warnings

import sympy as sp
from sympy.calculus.util import continuous_domain, function_range

from .formulas import X, parse_formula


def analyze(formula: str, analysis_type: str) -> dict:
    expr = parse_formula(formula)
    result = {"formula": formula, "normalized": str(expr), "variable": "x", "warnings": []}
    domain = None
    try:
        domain = continuous_domain(expr, X, sp.S.Reals)
        result["domain"] = str(domain)
    except (NotImplementedError, ValueError) as exc:
        result["warnings"].append(f"Domain could not be determined: {exc}")
    if analysis_type == "detailed" and domain is not None:
        try:
            result["range"] = str(function_range(expr, X, domain))
        except (NotImplementedError, ValueError) as exc:
            result["warnings"].append(f"Range could not be determined: {exc}")
    if analysis_type in ("detailed", "critical_points"):
        derivative = sp.diff(expr, X)
        result["derivative"] = str(derivative)
        search_domain = domain if domain is not None else sp.S.Reals
        stationary = None
        try:
            stationary = sp.solveset(derivative, X, domain=search_domain)
            if stationary.has(sp.ConditionSet):
                result["warnings"].append("The stationary-point equation is unresolved; this is not an empty set.")
        except (NotImplementedError, ValueError) as exc:
            result["warnings"].append(f"Stationary points could not be determined: {exc}")
        try:
            differentiable_domain = continuous_domain(derivative, X, sp.S.Reals)
            candidates = search_domain - differentiable_domain
        except (NotImplementedError, ValueError):
            candidates = sp.S.EmptySet
            for term in expr.atoms(sp.Abs):
                candidates |= sp.solveset(term.args[0], X, domain=search_domain)
            result["warnings"].append("Differentiability was not fully resolved; corner candidates may be incomplete.")
        # SymPy assigns sign(0)=0, but abs(x) has no derivative at zero.
        # Conversely abs(x^2) IS differentiable there. Check finite candidate sets
        # with the difference quotient before calling any point stationary.
        if isinstance(candidates, sp.FiniteSet) and len(candidates) <= 12:
            for point in list(candidates):
                try:
                    quotient = (expr - expr.subs(X, point)) / (X - point)
                    left = sp.limit(quotient, X, point, dir="-")
                    right = sp.limit(quotient, X, point, dir="+")
                    if left.is_finite is True and right.is_finite is True and left == right:
                        candidates -= sp.FiniteSet(point)
                except (NotImplementedError, ValueError):
                    result["warnings"].append(f"Could not verify differentiability at {point}.")
        result["nondifferentiable_candidates"] = str(candidates)
        if stationary is not None:
            result["stationary_points"] = str(stationary - candidates)
    return result


def render(payload: dict) -> dict:
    import matplotlib

    matplotlib.use("Agg")
    import numpy as np
    from matplotlib.figure import Figure

    cfg = payload["rendering"]
    fig = Figure(figsize=(cfg["default_width"] / 100, cfg["default_height"] / 100), dpi=100)
    ax = fig.subplots()
    x = np.linspace(*payload["x_range"], cfg["samples"])
    messages = []
    for formula in payload["formulas"]:
        expr = parse_formula(formula)
        with warnings.catch_warnings(), np.errstate(all="ignore"):
            warnings.simplefilter("ignore", RuntimeWarning)
            values = np.asarray(sp.lambdify(X, expr, modules="numpy")(x), dtype=complex)
            values = np.broadcast_to(values, x.shape)
            y = np.where(np.isfinite(values) & (np.abs(values.imag) < 1e-10), values.real, np.nan).copy()
        if not np.isfinite(y).any():
            messages.append(f"{formula}: no finite real values in this interval.")
        # Break large sampled jumps. This is an approximation, not a continuity proof.
        finite = y[np.isfinite(y)]
        if finite.size:
            span = (
                np.diff(payload["y_range"])[0]
                if payload["y_range"]
                else max(float(np.percentile(finite, 95) - np.percentile(finite, 5)), 1)
            )
            jumps = np.flatnonzero(np.abs(np.diff(y)) > 5 * span)
            y[jumps] = np.nan
            y[jumps + 1] = np.nan
        ax.plot(x, y, label=formula, linewidth=2)
    ax.set(xlim=payload["x_range"], xlabel="x", ylabel="y")
    if payload["y_range"]:
        ax.set_ylim(payload["y_range"])
    ax.axhline(0, color="#64748b", linewidth=0.7)
    ax.axvline(0, color="#64748b", linewidth=0.7)
    ax.grid(alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    fig.clear()
    return {"png": base64.b64encode(buf.getvalue()).decode("ascii"), "warnings": messages}


def main():
    try:
        payload = json.load(sys.stdin)
        result = (
            analyze(payload["formula"], payload["analysis_type"])
            if payload["operation"] == "analyze"
            else render(payload)
        )
        print(json.dumps({"result": result}))
    except Exception as exc:
        print(json.dumps({"error": f"{type(exc).__name__}: {exc}"}))


if __name__ == "__main__":
    main()

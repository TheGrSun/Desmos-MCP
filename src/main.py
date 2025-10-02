import base64
import io
import json
import os
from datetime import datetime
from typing import Dict, List, Literal, Optional, Union

import sympy
from sympy.calculus.util import continuous_domain, function_range
from fastmcp import FastMCP, Context as MCPContext
from mcp.types import Resource, Content, JSONRPCMessage as Message
from pydantic import BaseModel, Field

from desmos_api import DesmosAPIClient

# Initialize FastMCP server
mcp = FastMCP(
    "desmos-mcp",
    "A server for visualizing math formulas.",
)

# --- API Client Initialization ---
API_KEY = os.environ.get("DESMOS_API_KEY")
try:
    desmos_client = DesmosAPIClient(api_key=API_KEY) if API_KEY else None
except ValueError:
    desmos_client = None

# --- Pydantic Models for Tool and Prompt Inputs ---
class AdvancedAnalysisArgs(BaseModel):
    analysis_focus: Optional[str] = Field(default='derivatives', description="Focus of the analysis (e.g., derivatives, integrals, limits).")

AnalysisType = Literal["basic", "detailed", "critical_points"]

# --- In-memory Resource Definitions ---
SUPPORTED_FUNCTIONS = {
    "Trigonometric": ["sin", "cos", "tan"],
    "Hyperbolic": ["sinh", "cosh", "tanh"],
    "Exponential": ["exp", "log"],
    "Other": ["sqrt", "abs"]
}

GRAPH_TEMPLATES = {
    "dark_mode": {"backgroundColor": "#333", "axesColor": "#FFF", "gridColor": "#555"},
    "presentation": {"backgroundColor": "#FFF", "axesColor": "#000", "gridColor": "#DDD"}
}

EXAMPLE_FORMULAS = """
# Basic Examples
y = x^2
y = sin(x)

# Advanced Examples
y = exp(-x^2) * sin(pi*x)
"""

# --- Resource Provider (Following Documented Pattern) ---
@mcp.resource("resources://info")
def handle_resources() -> str:
    """Provides basic server information."""
    return "This is the Desmos-MCP server."

# --- Prompt Providers (Following Documented Pattern) ---
@mcp.prompt("basic_graphing_assistant", description="Assist user with plotting basic math functions.")
def basic_prompt_handler(args: Dict) -> List[Message]:
    return [Message(role="user", content=Content(text="I need help plotting a simple function."))]

@mcp.prompt("advanced_math_analysis", description="Guide user through deep analysis of complex functions.")
def advanced_prompt_handler(args: AdvancedAnalysisArgs) -> List[Message]:
    return [
        Message(role="user", content=Content(text=f"I want to perform an advanced analysis on a function, focusing on {args.analysis_focus}.")),
        Message(role="assistant", content=Content(text="Of course. Please provide the function you'd like to analyze."))
    ]

# --- Tools ---
@mcp.tool()
def hello(name: str = "World") -> str:
    """A simple tool that returns a greeting."""
    return f"Hello, {name}!"

@mcp.tool()
async def validate_formula(ctx: MCPContext, formula: str) -> str:
    """Validates the syntax of a mathematical formula, offering intelligent help on failure."""
    try:
        sympy.sympify(formula)
        return f"Formula '{formula}' is syntactically valid."
    except (sympy.SympifyError, SyntaxError) as e:
        technical_error = f"Details: {e}"
        ctx.info(f"Validation failed with technical error: {technical_error}")

        # Use LLM Sampling to get a user-friendly explanation
        try:
            sample_result = await ctx.sample(f"Please explain this Python sympy error in simple terms for a non-programmer: {technical_error}")
            user_friendly_error = sample_result.text
        except Exception as sample_err:
            ctx.error(f"LLM Sampling failed: {sample_err}")
            user_friendly_error = technical_error # Fallback to technical error

        # Elicit user confirmation with the friendly error
        return f"The formula '{formula}' is invalid. Here is an explanation: {user_friendly_error}"

@mcp.tool()
async def plot_math_function(
    ctx: MCPContext,
    formula: str,
    x_range: Optional[List[float]] = [-10, 10],
    y_range: Optional[List[float]] = None,
    use_api: bool = True
) -> str:
    """Generates a 2D plot. Tries Desmos API if available, otherwise falls back to local rendering."""
    await ctx.progress.start(message="Initializing plot...")
    
    if use_api and desmos_client:
        ctx.info("Attempting to plot with Desmos API...")
        await ctx.progress.report(1, 2, "Calling Desmos API...")
        try:
            image_bytes = await desmos_client.plot_formula(formula, x_range, y_range)
            if image_bytes:
                await ctx.progress.report(2, 2, "Encoding image...")
                img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                data_uri = f"data:image/png;base64,{img_base64}"
                await ctx.progress.end()
                return f"Successfully plotted '{formula}' using Desmos API. Image: {data_uri}"
            else:
                ctx.warning("Desmos API call failed, falling back to local rendering.")
        except Exception as e:
            ctx.error(f"An exception occurred with Desmos API: {e}. Falling back to local rendering.")

    ctx.info("Using local rendering...")
    try:
        await ctx.progress.start(total=3, message="Starting local rendering...")
        
        await ctx.progress.report(1, 3, "Parsing formula...")
        expr = sympy.sympify(formula)
        x = sympy.symbols('x')

        await ctx.progress.report(2, 3, "Generating plot data...")
        plot_kwargs = {
            'show': False,
            'xlabel': 'x',
            'ylabel': 'y',
            'title': formula
        }
        if x_range:
            plot_kwargs['xlim'] = x_range
        if y_range:
            plot_kwargs['ylim'] = y_range

        p = sympy.plot(expr, (x, x_range[0], x_range[1]), **plot_kwargs)

        # Save the plot to a file
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        save_dir = os.path.join(desktop_path, 'Desmos-MCP')
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"plot_{timestamp}.png"
        p.save(os.path.join(save_dir, filename))

        await ctx.progress.report(3, 3, "Encoding image...")
        buf = io.BytesIO()
        p.save(buf)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        data_uri = f"data:image/png;base64,{img_base64}"
        
        await ctx.progress.end()
        return f"Successfully plotted '{formula}' using local rendering. Image: {data_uri}"

    except Exception as e:
        await ctx.progress.end()
        return f"Error plotting formula '{formula}' locally. Details: {e}"

@mcp.tool()
def analyze_formula(formula: str, analysis_type: AnalysisType = "basic") -> str:
    """Analyzes mathematical properties of a formula (domain, range, critical points)."""
    try:
        x = sympy.symbols('x')
        expr = sympy.sympify(formula)
        results = [f"Analysis for '{formula}' ('{analysis_type}' type):"]
        if analysis_type == "basic" or analysis_type == "detailed":
            domain = continuous_domain(expr, x, sympy.S.Reals)
            results.append(f"- Domain: {domain}")
        if analysis_type == "detailed":
            f_range = function_range(expr, x, domain)
            results.append(f"- Range: {f_range}")
        if analysis_type == "critical_points":
            derivative = sympy.diff(expr, x)
            results.append(f"- Derivative: {derivative}")
            critical_points = sympy.solveset(derivative, x, domain=sympy.S.Reals)
            if not critical_points:
                results.append("- Critical Points: None found.")
            else:
                results.append(f"- Critical Points: {critical_points}")
        return "\n".join(results)
    except Exception as e:
        return f"Error analyzing formula '{formula}'. Details: {e}"

@mcp.tool()
async def plot_multiple_functions(
    ctx: MCPContext,
    formulas: List[str],
    x_range: Optional[List[float]] = [-10, 10],
    y_range: Optional[List[float]] = None,
) -> str:
    """Plots multiple functions on the same graph."""
    try:
        await ctx.progress.start(total=len(formulas) + 1, message="Starting multi-plot...")
        x = sympy.symbols('x')
        p = sympy.plot(show=False)
        
        for i, formula in enumerate(formulas):
            await ctx.progress.report(i + 1, message=f"Processing formula {i+1}: {formula}")
            expr = sympy.sympify(formula)
            line_label = formula
            line_color = f"C{i}"
            series = sympy.plot(expr, (x, x_range[0], x_range[1]), show=False, line_color=line_color, label=line_label)[0]
            p.append(series)

        if x_range:
            p.xlim = x_range
        if y_range:
            p.ylim = y_range
        
        p.legend = True

        # Save the plot to a file
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        save_dir = os.path.join(desktop_path, 'Desmos-MCP')
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"multi_plot_{timestamp}.png"
        p.save(os.path.join(save_dir, filename))

        await ctx.progress.report(len(formulas) + 1, message="Encoding image...")
        buf = io.BytesIO()
        p.save(buf)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        data_uri = f"data:image/png;base64,{img_base64}"
        
        await ctx.progress.end()
        return f"Successfully plotted {len(formulas)} functions. Image: {data_uri}"

    except Exception as e:
        await ctx.progress.end()
        return f"Error plotting multiple functions. Details: {e}"

if __name__ == "__main__":
    mcp.run()

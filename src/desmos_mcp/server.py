"""MCP tools, resources, and prompts. The stdio channel is reserved for MCP."""

import argparse
import asyncio
import base64
import json
import re
import sys
from typing import Annotated, Literal
from uuid import uuid4

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from mcp.types import ImageContent, TextContent
from pydantic import Field

from .config import Settings, load_settings
from .formulas import FUNCTIONS, parse_formula, validate_range
from .interactive import make_page

Formula = Annotated[str, Field(min_length=1, max_length=500)]
FormulaList = Annotated[list[Formula], Field(min_length=1, max_length=12)]
Bounds = Annotated[list[float], Field(min_length=2, max_length=2)]
AnalysisType = Literal["basic", "detailed", "critical_points"]

GUIDE = """Desmos MCP workflow
1. For offline y=f(x), call validate_formula, then plot_math_function or plot_multiple_functions.
   Accept x^2, y = sin(x), sqrt(x), abs(x), pi, e. Write 2*x, not 2x. Angles use radians.
2. For domain, range, and derivatives call analyze_formula. Explain warnings and unresolved sets.
   Stationary points are not necessarily extrema; nondifferentiable candidates may also matter.
3. For sliders, implicit curves, inequalities or editable graphs, use create_interactive_graph.
   Its expressions are DESMOS LATEX, not SymPy strings: ["a=1", "y=a x^2"].
   Open the returned HTML file in a browser and enter your own key from https://www.desmos.com/my-api.
   No browser is launched automatically. The SDK requires internet access. The key is not saved in HTML.
   Edit in the sidebar, drag/zoom, export PNG, save/import JSON state, or reset to the starting graph.
4. Ask for missing intent when it changes the result. Otherwise start with x=[-10,10] and explain it.
   Suggest one useful follow-up, such as changing a parameter or comparing a derivative.
5. Images are native MCP image content. If your host cannot display them, open the saved PNG locally.
   Paths refer to the SERVER machine; remote clients need their own file-transfer mechanism.
   Browser changes and JSON state files are not automatically synchronized to this MCP session.
6. Static graphs use finite sampling; discontinuities and rapid oscillations can require a narrower range.
"""


async def run_worker(payload: dict, timeout: float) -> dict:
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "desmos_mcp.worker",
        payload["operation"],
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    ready = False
    try:
        assert process.stdin and process.stdout and process.stderr
        process.stdin.write(json.dumps(payload).encode())
        await process.stdin.drain()
        process.stdin.close()

        # A cold macOS runner may spend tens of seconds importing Matplotlib and
        # creating its font cache. That setup is not part of the calculation budget.
        ready_line = await asyncio.wait_for(process.stdout.readline(), max(60.0, timeout))
        try:
            worker_ready = json.loads(ready_line) == {"ready": True}
        except (json.JSONDecodeError, UnicodeDecodeError):
            worker_ready = False
        if not worker_ready:
            stderr = await process.stderr.read()
            await process.wait()
            raise ToolError(
                "Calculation worker did not initialize correctly. " + stderr.decode(errors="replace")[-500:]
            )
        ready = True
        stdout, _stderr, _returncode = await asyncio.wait_for(
            asyncio.gather(process.stdout.read(), process.stderr.read(), process.wait()), timeout
        )
    except (asyncio.TimeoutError, asyncio.CancelledError) as exc:
        if process.returncode is None:
            process.kill()
        await process.communicate()
        if isinstance(exc, asyncio.CancelledError):
            raise
        if ready:
            message = f"Calculation exceeded {timeout:g}s. Simplify the formula or use basic analysis."
        else:
            message = "Calculation worker initialization exceeded its startup timeout."
        raise ToolError(message) from exc
    if process.returncode:
        raise ToolError("Calculation process failed. Try a simpler expression or reduce the plotting range.")
    result = json.loads(stdout)
    if "error" in result:
        raise ToolError(result["error"])
    return result["result"]


def create_server(settings: Settings | None = None) -> FastMCP:
    cfg = settings if settings is not None else load_settings()
    mcp = FastMCP("desmos-mcp", instructions=GUIDE)
    worker_slots = asyncio.Semaphore(2)

    async def calculate(payload: dict):
        async with worker_slots:
            return await run_worker(payload, cfg.timeout_seconds)

    @mcp.resource("resources://info")
    def info() -> dict:
        return {
            "name": "desmos-mcp",
            "version": "0.2.0",
            "offline_png": True,
            "interactive_backend": "Desmos JavaScript SDK v1.11",
            "guide": "resources://guide",
        }

    @mcp.resource("resources://guide")
    def guide() -> str:
        return GUIDE

    @mcp.resource("resources://examples")
    def examples() -> dict:
        return {
            "offline": ["y = x^2", "sin(x)", "exp(-x^2)*cos(3*x)", "1/x", "abs(x)"],
            "functions": sorted(FUNCTIONS),
            "interactive_latex": ["a=1", "y=a x^2", "x^2+y^2=9"],
        }

    @mcp.resource("graphs://{graph_id}", mime_type="text/html")
    def graph_page(graph_id: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{32}", graph_id):
            raise ValueError("Invalid graph ID.")
        return (cfg.output_dir / f"graph_{graph_id}.html").read_text(encoding="utf-8")

    @mcp.prompt("basic_graphing_assistant")
    def basic_prompt(formula: str = "x^2") -> str:
        """Start a guided plotting conversation with a formula or a description."""
        return f"Help me explore this formula: {formula}\n{GUIDE}\nRespond in my language, explain the axes, and suggest one experiment."

    @mcp.prompt("advanced_math_analysis")
    def advanced_prompt(formula: str = "x^3-3*x", analysis_focus: str = "derivatives") -> str:
        """Guide symbolic analysis and verify its interpretation with a plot."""
        return (
            f"Analyze {formula}, focusing on {analysis_focus}. Use the supported tools; distinguish exact results "
            "from sampled plots and unresolved symbolic results. Plot the function and, when useful, its derivative. "
            "Do not claim integration or limit tools exist.\n" + GUIDE
        )

    @mcp.tool()
    def validate_formula(formula: Formula) -> dict:
        """Check offline y=f(x) syntax. Returns repair guidance without requiring client sampling."""
        try:
            expr = parse_formula(formula)
            return {"valid": True, "normalized": str(expr), "syntax": "offline", "next_tool": "plot_math_function"}
        except ValueError as exc:
            return {"valid": False, "error": str(exc), "examples": ["y = x^2", "2*x + 1", "sin(x)"]}

    @mcp.tool()
    async def analyze_formula(ctx: Context, formula: Formula, analysis_type: AnalysisType = "basic") -> dict:
        """Analyze a real function of x. Detailed adds range and derivative; critical_points includes corner candidates."""
        await ctx.report_progress(0, 1, "Analyzing formula")
        result = await calculate({"operation": "analyze", "formula": formula, "analysis_type": analysis_type})
        await ctx.report_progress(1, 1, "Analysis complete")
        return result

    async def plot(ctx: Context, formulas: list[str], x_range, y_range, use_api: bool = False):
        try:
            xs = validate_range(x_range, (-10, 10))
            ys = validate_range(y_range)
        except ValueError as exc:
            raise ToolError(str(exc)) from exc
        await ctx.report_progress(0, 2, "Rendering offline PNG")
        result = await calculate(
            {
                "operation": "render",
                "formulas": formulas,
                "x_range": xs,
                "y_range": ys,
                "rendering": cfg.rendering.model_dump(),
            }
        )
        metadata = {"backend": "matplotlib", "formulas": formulas, "x_range": xs, "warnings": result["warnings"]}
        if use_api:
            metadata["warnings"].append(
                "use_api is deprecated. PNG is offline; use create_interactive_graph for Desmos."
            )
        if cfg.rendering.save_files:
            cfg.output_dir.mkdir(parents=True, exist_ok=True)
            path = cfg.output_dir / f"plot_{uuid4().hex}.png"
            path.write_bytes(base64.b64decode(result["png"]))
            metadata["path"] = str(path.resolve())
        await ctx.report_progress(2, 2, "Plot ready")
        return [
            TextContent(type="text", text=json.dumps(metadata)),
            ImageContent(type="image", data=result["png"], mimeType="image/png"),
        ]

    @mcp.tool()
    async def plot_math_function(
        ctx: Context,
        formula: Formula,
        x_range: Bounds | None = None,
        y_range: Bounds | None = None,
        use_api: bool = False,
    ) -> list[TextContent | ImageContent]:
        """Plot y=f(x) offline and return a native PNG image. Defaults x to [-10,10]; use_api is deprecated."""
        return await plot(ctx, [formula], x_range, y_range, use_api)

    @mcp.tool()
    async def plot_multiple_functions(
        ctx: Context, formulas: FormulaList, x_range: Bounds | None = None, y_range: Bounds | None = None
    ) -> list[TextContent | ImageContent]:
        """Compare 1–12 offline formulas on shared axes, with a legend and native PNG output."""
        return await plot(ctx, formulas, x_range, y_range)

    @mcp.tool()
    def create_interactive_graph(
        expressions: FormulaList,
        title: Annotated[str, Field(max_length=120)] = "Math exploration",
        x_range: Bounds | None = None,
        y_range: Bounds | None = None,
        language: Literal["en", "zh-CN"] = "en",
    ) -> dict:
        """Create editable Desmos HTML. Input DESMOS LATEX (e.g. ['a=1','y=a x^2']), not Python/SymPy syntax.

        Open the returned file, supply your own Desmos API key in the page, then edit, zoom, save/import state or export PNG.
        Requires internet for the SDK; key is not embedded. Expressions are checked by Desmos after connection, not locally.
        """
        try:
            xs, ys = validate_range(x_range, (-10, 10)), validate_range(y_range, (-10, 10))
            if any(not expression.strip() for expression in expressions):
                raise ValueError("Expressions cannot be blank. Try ['a=1', 'y=a x^2'].")
        except ValueError as exc:
            raise ToolError(str(exc)) from exc
        graph_id = uuid4().hex
        cfg.output_dir.mkdir(parents=True, exist_ok=True)
        path = cfg.output_dir / f"graph_{graph_id}.html"
        path.write_text(make_page(expressions, title, xs, ys, language), encoding="utf-8")
        return {
            "graph_id": graph_id,
            "path": str(path.resolve()),
            "uri": path.resolve().as_uri(),
            "resource_uri": f"graphs://{graph_id}",
            "expressions": expressions,
            "next_step": "Open the HTML on the server machine in a browser. Enter your own Desmos API key in the page.",
            "requires": ["Internet access", "Desmos API key (https://www.desmos.com/my-api)"],
            "state_sync": "Save/import JSON in the browser. Browser edits do not update the MCP session.",
        }

    return mcp


def main():
    parser = argparse.ArgumentParser(description="Desmos MCP: offline PNG and interactive Desmos graphs over stdio")
    parser.add_argument("--config", help="Path to a JSON configuration file")
    args = parser.parse_args()
    try:
        server = create_server(load_settings(args.config))
    except (OSError, ValueError) as exc:
        parser.error(f"Invalid configuration: {exc}")
    server.run(transport="stdio")


if __name__ == "__main__":
    main()

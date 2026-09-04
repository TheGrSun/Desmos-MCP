# Desmos MCP

[中文](README.zh.md) · [Client setup](docs/CLIENTS.md) · [Examples](docs/EXAMPLES.md)

Give an AI assistant offline function plots and symbolic analysis, plus editable Desmos graphs in a browser.
Python 3.10+ · FastMCP 2.x · Apache-2.0 · Independent project, not affiliated with Desmos.

## What works

| Tool | Result | Requirements |
| --- | --- | --- |
| `validate_formula` | Normalized formula or actionable syntax guidance | Offline |
| `plot_math_function` | PNG image and optional saved file | Offline |
| `plot_multiple_functions` | 1–12 curves on shared axes | Offline |
| `analyze_formula` | Domain; optionally range, derivative, stationary points and corner candidates | Offline |
| `create_interactive_graph` | Standalone HTML with editable expressions, sliders, zoom, PNG export and JSON state import/export | Browser, internet and your own Desmos API key |

Offline tools accept `y = x^2`, `2*x + 1`, `sin(x)`, `sqrt(x)`, `abs(x)`, `pi` and `e`.
The interactive tool accepts **Desmos LaTeX**, including `a=1`, `y=ax^2` and `x^2+y^2=9`.
These are separate syntax contracts. Interactive expressions are checked by Desmos when the page connects.

## Quick start

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if needed, then:

```sh
git clone https://github.com/TheGrSun/Desmos-MCP.git
cd Desmos-MCP
uv sync --locked
uv run desmos-mcp --help
```

Connect your MCP client using the [copyable configuration](docs/CLIENTS.md). The server uses stdio:

```sh
uv run desmos-mcp
```

Waiting for input is normal: this command starts an MCP server, not a command-line chat.
The compatibility command `uv run src/main.py` also works.

Try asking your assistant:

> Plot sin(x) and cos(x) from -2*pi to 2*pi and explain where they cross.

> Create a Desmos graph with a=1 and y=ax^2 so I can explore the parameter.

For the second request, open the returned HTML file, get your own key from [Desmos](https://www.desmos.com/my-api),
and enter it on the page. The key is used in memory to load the official SDK; it is not embedded in the generated file
or included in exported state JSON. The page explains editing, sliders, reset, and saving. No browser opens automatically.
Browser edits do not automatically sync to the assistant: save state before closing the page.

## Configuration

Configuration priority: `--config PATH` → `DESMOS_MCP_CONFIG` → `./config.json` → built-in defaults.
Relative output directories resolve against the configuration file, not the caller's current directory.

```json
{
  "output_dir": "graphs",
  "timeout_seconds": 20,
  "rendering": {
    "default_width": 900,
    "default_height": 600,
    "samples": 1600,
    "save_files": true
  }
}
```

Without a configuration file, artifacts go to the operating system's temporary directory under `desmos-mcp`.
Use an explicit directory for lasting files. File names contain UUIDs. `save_files=false` disables saved PNGs;
interactive HTML is always saved because it is the result of that tool. Images still return as native MCP content.
Generated files are not automatically deleted. Delete unwanted artifacts from the configured output directory.

Offline inputs have length, syntax, and range limits. Symbolic analysis and rendering run in disposable processes
with a configurable timeout and at most two active workers. The whitelist parser never evaluates Python from user input.
This is a local stdio service, not a hardened public multi-tenant computation service.

## Accuracy and limits

- Offline analysis supports real-valued functions of `x` with explicit multiplication and radians.
  Allowed functions: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`, `exp`, `log`/`ln`, `sqrt`, `abs`/`Abs`.
- `basic` analyzes the domain. `detailed` adds range and derivative analysis. `critical_points` reports stationary points
  and possible nondifferentiable points separately. Candidates are not classified extrema.
- Unresolved symbolic results include warnings; a `ConditionSet` is not “no solutions.” Some requests can time out.
- Static PNG curves are sampled approximations; inspect a narrower range near discontinuities or rapid oscillations.
- Desmos's public integration is a [JavaScript SDK](https://www.desmos.com/api/v1.11/docs/index.html), not a REST PNG endpoint.
  No API key is needed for offline tools. Requests to the SDK happen only after connecting in the browser.
- Returned file paths refer to the server machine. Remote clients need a separate file-transfer mechanism.
- Tools do not provide symbolic integration, limits, 3D analysis, or automatic browser-to-MCP state synchronization.

## Development

```sh
uv sync --locked
uv run pytest
uv run ruff check src tests
node --test tests/interactive.test.cjs
uv build
```

Node.js 22+ is needed only for the isolated interactive-controller tests, not for running the MCP server.
See [CONTRIBUTING.md](CONTRIBUTING.md) for module boundaries and validation requirements.
[CHANGELOG.md](CHANGELOG.md) documents the 0.2 migration, including removal of the old `desmos` configuration block.
The Python package includes the HTML template; the CLI works after wheel installation.

Licensed under [Apache-2.0](LICENSE).

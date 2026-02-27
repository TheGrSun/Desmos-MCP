# Desmos-MCP Server

---

English | [中文](./README.zh.md)

---

This is a standard Model Context Protocol (MCP) server designed to provide powerful mathematical formula visualization and analysis capabilities for Large Language Models (LLMs). It utilizes `sympy` for local rendering and computation, and can optionally integrate with the Desmos API.

<a href="https://glama.ai/mcp/servers/@TheGrSun/Desmos-MCP">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@TheGrSun/Desmos-MCP/badge" alt="Desmos Server MCP server" />
</a>

## ✨ Features

- **Interactive Formula Validation**: Use the `validate_formula` tool to check the syntax of mathematical formulas. If a formula is invalid, it uses the LLM sampling feature to provide an easy-to-understand explanation of the error.
- **Single Function Plotting**: Use the `plot_math_function` tool to generate a 2D plot from a formula. It supports using the Desmos API (configurable via `config.json`) or falling back to local `matplotlib` rendering, and provides progress reports during execution.
- **Multiple Function Plotting**: Use the `plot_multiple_functions` tool to plot multiple functions on the same graph.
- **Symbolic Analysis**: Use the `analyze_formula` tool to calculate mathematical properties of a formula, such as its domain, range, and critical points.
- **Save Plot to File**: Automatically saves the generated plot as a PNG file to a `Desmos-MCP` folder on your desktop.

## ⚙️ Tech Stack

- Python 3.10+
- FastMCP
- Sympy
- Matplotlib
- HTTPX

## 🚀 Installation & Setup

1.  **Clone the project** (if you haven't already)
2.  **Install `uv`**
    If you don't have `uv` installed, run the following command in your terminal:
    ```sh
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```
3.  **Create a virtual environment**
    In the project root directory, run:
    ```sh
    uv venv
    ```
4.  **Install dependencies**
    ```sh
    uv sync
    ```
    This command will install all the necessary dependencies based on the `pyproject.toml` file.

## 🔧 Configuration

The server's behavior is controlled by the `config.json` file in the project root.

```json
{
  "desmos": {
    "use_api": true,
    "api_key_env_var": "DESMOS_API_KEY",
    "fallback_to_local": true
  },
  "rendering": {
    "default_width": 600,
    "default_height": 400
  }
}
```

- `desmos.use_api`: If `true`, the server will first attempt to use the Desmos API for plotting.
- `desmos.api_key_env_var`: Specifies the name of the environment variable used to get the Desmos API key.
- `desmos.fallback_to_local`: If `use_api` is `true` but the API call fails, this determines if the server should automatically fall back to local rendering.

### Set Desmos API Key (Optional)

To use the Desmos API feature, you need to set an environment variable. For example, in PowerShell:

```powershell
$env:DESMOS_API_KEY="your_actual_api_key_here"
```

## ▶️ Running the Server

To run the server independently for testing, execute the following command in the project root:

```sh
uv run src/main.py
```

The server will start via standard input/output (stdio) and will be ready to be connected by an MCP client (like the Gemini CLI).

## 📝 To-Do

- [ ] **Add 3D plotting support.**
- [ ] **Implement real-time formula analysis and interactive plotting, similar to Desmos.**

## 📄 License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
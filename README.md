# Desmos-MCP Server

---

English | [中文](./README.zh.md) <!-- This is a placeholder, I will generate a single file with both languages -->

---

This is a standard Model Context Protocol (MCP) server designed to provide powerful mathematical formula visualization and analysis capabilities for Large Language Models (LLMs). It utilizes `sympy` for local rendering and computation, and can optionally integrate with the Desmos API.

这是一个标准的模型上下文协议 (MCP) 服务器，旨在为大型语言模型 (LLM) 提供强大的数学公式可视化和分析功能。它利用 `sympy` 进行本地渲染和计算，并能选择性地集成 Desmos API。

## ✨ Features / 功能特性

- **Interactive Formula Validation**: Use the `validate_formula` tool to check the syntax of mathematical formulas. If a formula is invalid, it uses the LLM sampling feature to provide an easy-to-understand explanation of the error.
- **交互式公式验证**: 使用 `validate_formula` 工具检查数学公式的语法。如果公式无效，它会利用 LLM 采样功能提供简单易懂的错误解释。

- **Single Function Plotting**: Use the `plot_math_function` tool to generate a 2D plot from a formula. It supports using the Desmos API (configurable via `config.json`) or falling back to local `matplotlib` rendering, and provides progress reports during execution.
- **单函数绘图**: 使用 `plot_math_function` 工具根据公式生成 2D 图形。支持通过 `config.json` 配置使用 Desmos API 或回退到本地 `matplotlib` 渲染，并在执行期间提供进度报告。

- **Multiple Function Plotting**: Use the `plot_multiple_functions` tool to plot multiple functions on the same graph.
- **多函数绘图**: 使用 `plot_multiple_functions` 工具在同一张图表上绘制多个函数。

- **Symbolic Analysis**: Use the `analyze_formula` tool to calculate mathematical properties of a formula, such as its domain, range, and critical points.
- **符号分析**: 使用 `analyze_formula` 工具计算公式的数学特性，如定义域、值域和临界点。

- **Save Plot to File**: Automatically saves the generated plot as a PNG file to a `Desmos-MCP` folder on your desktop.
- **保存绘图文件**: 自动将生成的图像保存为 PNG 文件到您桌面上的 `Desmos-MCP` 文件夹中。

## ⚙️ Tech Stack / 技术栈

- Python 3.10+
- FastMCP
- Sympy
- Matplotlib
- HTTPX

## 🚀 Installation & Setup / 安装与设置

1.  **Clone the project** (if you haven't already)
    **克隆项目** (如果您尚未这样做)

2.  **Install `uv`**
    If you don't have `uv` installed, run the following command in your terminal:
    如果您尚未安装 `uv`，请在终端中运行以下命令：
    ```sh
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

3.  **Create a virtual environment**
    In the project root directory, run:
    在项目根目录运行：
    ```sh
    uv venv
    ```

4.  **Install dependencies**
    **安装依赖**
    ```sh
    uv sync
    ```
    This command will install all the necessary dependencies based on the `pyproject.toml` file.
    此命令将根据 `pyproject.toml` 文件安装所有必需的依赖项。

## 🔧 Configuration / 配置

The server's behavior is controlled by the `config.json` file in the project root.
服务器的行为由项目根目录下的 `config.json` 文件控制。

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
- `desmos.use_api`: 如果为 `true`，服务器将优先尝试使用 Desmos API 进行绘图。
- `desmos.api_key_env_var`: Specifies the name of the environment variable used to get the Desmos API key.
- `desmos.api_key_env_var`: 指定用于获取 Desmos API 密钥的环境变量的名称。
- `desmos.fallback_to_local`: If `use_api` is `true` but the API call fails, this determines if the server should automatically fall back to local rendering.
- `desmos.fallback_to_local`: 如果 `use_api` 为 `true` 但 API 调用失败，服务器是否应自动回退到本地渲染。

### Set Desmos API Key (Optional) / 设置 Desmos API 密钥 (可选)

To use the Desmos API feature, you need to set an environment variable. For example, in PowerShell:
要使用 Desmos API 功能，您需要设置一个环境变量。例如，在 PowerShell 中：

```powershell
$env:DESMOS_API_KEY="your_actual_api_key_here"
```

## ▶️ Running the Server / 运行服务器

To run the server independently for testing, execute the following command in the project root:
要独立运行服务器以进行测试，请在项目根目录中执行：

```sh
uv run src/main.py
```

The server will start via standard input/output (stdio) and will be ready to be connected by an MCP client (like the Gemini CLI).
服务器将通过标准输入/输出 (stdio) 启动，并准备好由 MCP 客户端（如 Gemini CLI）连接。

## 📝 To-Do / 未来计划

- [ ] **Add 3D plotting support.**
- [ ] **添加对3D图像的支持。**

- [ ] **Implement real-time formula analysis and interactive plotting, similar to Desmos.**
- [ ] **实现类似于Desmos的实时公式分析和交互式绘图功能。**

## 📄 License / 许可证

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
该项目根据 Apache 2.0 许可证授权。详情请参阅 [LICENSE](LICENSE) 文件。
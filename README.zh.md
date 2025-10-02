# Desmos-MCP 服务器

---

[English](./README.md) | 中文

---

这是一个标准的模型上下文协议 (MCP) 服务器，旨在为大型语言模型 (LLM) 提供强大的数学公式可视化和分析功能。它利用 `sympy` 进行本地渲染和计算，并能选择性地集成 Desmos API。

## ✨ 功能特性

- **交互式公式验证**: 使用 `validate_formula` 工具检查数学公式的语法。如果公式无效，它会利用 LLM 采样功能提供简单易懂的错误解释。
- **单函数绘图**: 使用 `plot_math_function` 工具根据公式生成 2D 图形。支持通过 `config.json` 配置使用 Desmos API 或回退到本地 `matplotlib` 渲染，并在执行期间提供进度报告。
- **多函数绘图**: 使用 `plot_multiple_functions` 工具在同一张图表上绘制多个函数。
- **符号分析**: 使用 `analyze_formula` 工具计算公式的数学特性，如定义域、值域和临界点。
- **保存绘图文件**: 自动将生成的图像保存为 PNG 文件到您桌面上的 `Desmos-MCP` 文件夹中。

## ⚙️ 技术栈

- Python 3.10+
- FastMCP
- Sympy
- Matplotlib
- HTTPX

## 🚀 安装与设置

1.  **克隆项目** (如果您尚未这样做)
2.  **安装 `uv`**
    如果您尚未安装 `uv`，请在终端中运行以下命令：
    ```sh
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```
3.  **创建虚拟环境**
    在项目根目录运行：
    ```sh
    uv venv
    ```
4.  **安装依赖**
    ```sh
    uv sync
    ```
    此命令将根据 `pyproject.toml` 文件安装所有必需的依赖项。

## 🔧 配置

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

- `desmos.use_api`: 如果为 `true`，服务器将优先尝试使用 Desmos API 进行绘图。
- `desmos.api_key_env_var`: 指定用于获取 Desmos API 密钥的环境变量的名称。
- `desmos.fallback_to_local`: 如果 `use_api` 为 `true` 但 API 调用失败，服务器是否应自动回退到本地渲染。

### 设置 Desmos API 密钥 (可选)

要使用 Desmos API 功能，您需要设置一个环境变量。例如，在 PowerShell 中：

```powershell
$env:DESMOS_API_KEY="your_actual_api_key_here"
```

## ▶️ 运行服务器

要独立运行服务器以进行测试，请在项目根目录中执行：

```sh
uv run src/main.py
```

服务器将通过标准输入/输出 (stdio) 启动，并准备好由 MCP 客户端（如 Gemini CLI）连接。

## 📝 未来计划

- [ ] **添加对3D图像的支持。**
- [ ] **实现类似于Desmos的实时公式分析和交互式绘图功能。**

## 📄 许可证

该项目根据 Apache 2.0 许可证授权。详情请参阅 [LICENSE](LICENSE) 文件。

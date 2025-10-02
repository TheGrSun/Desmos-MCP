# Desmos-MCP 服务开发计划

## 1. 项目概述

本项目旨在根据 `ref.md` 的详细规格，构建一个标准的 Model Context Protocol (MCP) 服务器。该服务器将利用 `FastMCP` Python 库，实现一个能够接收数学公式、生成并返回相应数学图形（二维及三维）的服务。

## 2. 技术选型

- **语言**: Python 3.10+
- **框架**: FastMCP (基于 FastAPI)
- **核心库**:
    - `httpx`: 用于与 Desmos API 进行异步 HTTP 通信。
    - `sympy`: 用于公式解析、分析和本地渲染。
    - `matplotlib`: 用于生成图形的本地渲染引擎。
- **环境管理**: `uv`

## 3. 开发阶段

### 阶段一：环境设置与基础框架 (预计时间: 1天)

1.  **项目初始化**:
    - 使用 `uv init` 创建项目结构。
    - 创建 `src` 目录存放核心代码。
    - `uv venv` 创建并激活虚拟环境。
2.  **安装依赖**:
    - `uv add fastmcp httpx sympy matplotlib`
3.  **构建基础服务器**:
    - 创建 `src/main.py`。
    - 参照 `MCP.md` 的示例，初始化一个基础的 `FastMCP` 服务器实例。
    - 实现一个简单的 "hello-world" tool 来验证服务器可以正常启动和响应。

### 阶段二：核心工具 (Tools) 实现 (预计时间: 3-4天)

此阶段将根据 `ref.md` 中定义的 `Tools` 规格进行开发。

1.  **`validate_formula` 工具**:
    - 使用 `sympy.sympify` 来验证数学公式的语法正确性。
    - 定义 `FastMCP` tool，接收 `formula` 字符串，返回验证结果。
2.  **`plot_math_function` 工具 (本地渲染)**:
    - 重点实现离线渲染能力。
    - 使用 `sympy.plot` 结合 `matplotlib` 后端来根据公式、范围和样式参数生成图形。
    - 将生成的图形（PNG/SVG）编码为 Base64 字符串。
    - 返回 `ref.md` 中定义的 `image` 和 `text` 内容。
3.  **`analyze_formula` 工具**:
    - 利用 `sympy` 的强大符号计算能力。
    - 实现 `basic`, `detailed`, `critical_points` 等不同级别的分析。
    - 计算定义域 (`calculus.util.continuous_domain`)、值域 (`calculus.util.function_range`)、临界点等。
4.  **`plot_multiple_functions` 工具**:
    - 扩展 `plot_math_function` 的逻辑，使其能够接受一个公式列表。
    - 在同一个 `matplotlib` 图形实例上绘制多个函数，并为每个函数应用不同的样式。

### 阶段三：Desmos API 集成 (预计时间: 2天)

1.  **API 客户端**:
    - 创建一个 `src/desmos_api.py` 模块。
    - 使用 `httpx.AsyncClient` 封装对 Desmos API 的请求。
    - 处理 API Key 认证和错误响应。
2.  **功能切换逻辑**:
    - 在 `plot_math_function` 工具中增加逻辑，根据服务器配置 (`use_api`) 决定使用 Desmos API 还是本地渲染。
    - 实现 `fallback_to_local` 机制，当 API 调用失败时，自动切换到本地渲染。

### 阶段四：资源 (Resources) 和提示 (Prompts) 实现 (预计时间: 1-2天)

1.  **实现 Resources**:
    - `math-functions`: 创建一个 JSON 文件或 Python 字典，列出 `sympy` 支持的函数，并通过 `resources/list` 端点暴露。
    - `graph-templates`: 定义多种预设的 `matplotlib` 样式表。
    - `example-formulas`: 创建一个文本文件包含示例公式。
2.  **实现 Prompts**:
    - 根据 `ref.md` 定义 `basic_graphing_assistant` 等提示模板。
    - 实现 `prompts/get` 请求的处理逻辑，根据参数动态生成引导性消息。

### 阶段五：测试、文档和优化 (预计时间: 2-3天)

1.  **单元测试**:
    - 使用 `pytest` 为每个 tool 编写单元测试。
    - 重点测试公式解析、图形生成和边界条件。
2.  **集成测试**:
    - 参照 `MCP.md` 中的方法，配置 Claude for Desktop 或其他 MCP 客户端。
    - 端到端测试所有 tools 和 prompts 的功能。
3.  **完善文档**:
    - 更新 `README.md`，包含详细的安装、配置和使用说明。
    - 为代码添加必要的注释和文档字符串。
4.  **性能优化**:
    - 实现 `ref.md` 中提到的缓存策略（图像缓存、API响应缓存）。

## 4. 下一步行动

1.  **执行阶段一**: 开始项目初始化和环境搭建。
2.  **获取 Desmos API Key**: 申请并配置 Desmos API 密钥，以便在阶段三中使用。

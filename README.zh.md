# Desmos MCP

[English](README.md) · [客户端接入](docs/CLIENTS.md) · [调用示例](docs/EXAMPLES.md)

让 AI 助手离线绘制函数、分析数学性质，并生成可在浏览器中编辑的 Desmos 交互图表。
Python 3.10+ · FastMCP 2.x · Apache-2.0 · 独立开源项目，非 Desmos 官方产品。

## 可以做什么

| 工具 | 结果 | 使用条件 |
| --- | --- | --- |
| `validate_formula` | 标准化公式，或返回可操作的修正建议 | 离线 |
| `plot_math_function` | 原生 PNG 图片及可选的保存路径 | 离线 |
| `plot_multiple_functions` | 同一坐标系比较 1–12 个函数 | 离线 |
| `analyze_formula` | 定义域；可进一步计算值域、导数、驻点和不可导候选点 | 离线 |
| `create_interactive_graph` | 可编辑公式、调滑块、缩放、导出 PNG、保存和导入状态的 HTML | 浏览器、联网、自有 Desmos API key |

离线工具使用 `y = x^2`、`2*x + 1`、`sin(x)`、`sqrt(x)`、`abs(x)` 等语法。
交互工具使用 **Desmos LaTeX**，例如 `a=1`、`y=ax^2`、`x^2+y^2=9`。
两种输入格式有明确区分；交互公式由连接后的 Desmos 计算器检查。

## 助手会返回什么

离线绘图返回 **MCP 原生 PNG 图片内容**，同时返回公式、警告，以及启用保存时的文件路径等文本信息。
支持图片的客户端可直接在对话中显示图形。

交互绘图返回 **HTML 文件路径和资源 URI**，不是自动嵌入的浏览器会话。
需要在浏览器中打开文件，连接 Desmos 后编辑图表。客户端可以提供自己的预览界面，
但不是所有 MCP 客户端都会直接渲染 HTML 资源。本地文件 URI 也不是可公开分享的网址。

目前工具支持二维图形，三维绘图尚未实现。

## 验证状态

0.2 实现在本地 macOS/Python 3.10 环境通过了 41 个 Python 测试和 3 个隔离的 JavaScript 控制器测试。
另在独立安装的 wheel 中验证了命令入口、PNG 返回及 HTML 模板打包。
CI 已配置 Linux、macOS、Windows 和 Python 3.10/3.12；不表示远端所有任务已经运行通过。

HTML 控制器测试使用模拟 Desmos SDK。真实 API key 连接和浏览器布局验证仍待完成；
审阅环境的浏览器策略阻止了自动访问本地 HTML 文件。

## 安装并接入

先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)，然后执行：

```sh
git clone https://github.com/TheGrSun/Desmos-MCP.git
cd Desmos-MCP
uv sync --locked
uv run desmos-mcp --help
```

按[客户端接入文档](docs/CLIENTS.md)配置 MCP。手动启动命令：

```sh
uv run desmos-mcp
```

启动后等待输入是正常现象：这是 stdio MCP 服务，需要客户端通过协议调用，不是终端聊天程序。
旧命令 `uv run src/main.py` 仍可使用。

接入后可以对助手说：

> 在 -2π 到 2π 上比较 sin(x) 和 cos(x)，解释它们的交点。

> 创建 a=1、y=ax^2 的交互图，用中文引导我观察参数变化。

第二个请求会生成 HTML 文件。打开后，在 [Desmos](https://www.desmos.com/my-api)申请自己的 key，填入页面即可连接。
Key 在页面内存中使用，用来从官方加载 SDK；不会写入生成的 HTML 或导出的状态 JSON。
页面提供公式编辑、滑块、恢复初始图、图片导出及状态导入/导出指导，不会自动启动浏览器。
网页修改不会自动回传给 MCP 助手；刷新或关闭前请保存状态。

## 配置

优先级：`--config 路径` → `DESMOS_MCP_CONFIG` 环境变量 → 当前目录 `config.json` → 内置默认值。
相对输出路径以配置文件所在目录为基准。

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

没有配置文件时，文件保存在系统临时目录下的 `desmos-mcp` 中；长期保存请指定输出目录。
文件名含 UUID，避免并发覆盖。`save_files=false` 只关闭 PNG 落盘，MCP 仍返回图片；交互 HTML 始终保存。
文件不会自动清理，可在输出目录手动删除不需要的图表。

公式长度、语法、坐标范围均有校验。绘图与符号计算在独立进程运行，超过时限会终止，同时最多运行两个计算进程。
白名单解析器不会执行输入中的 Python 代码。这是本地 stdio 服务，不是面向公开多租户环境的计算沙箱。

## 数学能力与边界

- 离线计算支持实变量 `x`，显式乘法及弧度制；常数包括 `pi`、`π`、`e`。
  函数包括 `sin/cos/tan`、`asin/acos/atan`、`sinh/cosh/tanh`、`exp`、`log/ln`、`sqrt`、`abs/Abs`。
- `basic` 计算定义域；`detailed` 增加值域和导数分析；`critical_points` 分别报告驻点和不可导候选点，不直接断言其为极值。
- 符号求解未完成时返回警告。`ConditionSet` 不代表无解；复杂计算可能超时。
- PNG 来自有限采样，间断点或高频振荡附近应缩小区间进一步检查。
- Desmos 官方提供[浏览器 JavaScript SDK](https://www.desmos.com/api/v1.11/docs/index.html)，没有使用假定的 REST 绘图接口。
  离线工具不需要 key；只有在交互页面点击连接后才请求 SDK。
- 返回路径属于服务端机器。远程客户端需要另外传输文件，不能直接打开另一台机器的本地路径。
- 暂不提供符号积分、极限工具、3D 分析及网页与 MCP 的自动状态同步。

## 开发与迁移

```sh
uv sync --locked
uv run pytest
uv run ruff check src tests
node --test tests/interactive.test.cjs
uv build
```

Node.js 22+ 仅用于交互控制器的隔离测试，运行 MCP 服务不需要 Node。
参见[贡献指南](CONTRIBUTING.md)和 [0.2 迁移说明](CHANGELOG.md)。旧配置中的 `desmos` 块已移除，需要替换为上面的格式。
HTML 模板随 Python 包一起发布，安装 wheel 后可直接使用命令入口。

许可证：[Apache-2.0](LICENSE)。

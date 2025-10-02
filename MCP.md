快速开始
面向服务器开发者
开始构建你自己的服务器，以便在 Claude Desktop 和其他客户端中使用。

在本教程中，我们将构建一个简单的 MCP 天气服务器，并将其连接到一个 host，即 Claude for Desktop。我们将从基本设置开始，然后逐步介绍更复杂的用例。
​
我们将构建什么
许多 LLM 目前不具备获取天气预报和恶劣天气警报的能力。让我们使用 MCP 来解决这个问题！
我们将构建一个服务器，它暴露两个 tools：get-alerts 和 get-forecast。然后，我们将服务器连接到一个 MCP host（在本例中是 Claude for Desktop）：


服务器可以连接到任何 client。我们在这里选择 Claude for Desktop 是为了简单起见，但我们也有关于构建你自己的 client 的指南以及其他 clients 列表。
为什么选择 Claude for Desktop 而不是 Claude.ai？

因为服务器是本地运行的，所以 MCP 目前仅支持 desktop hosts。远程 hosts 正在积极开发中。
​
核心 MCP 概念
MCP 服务器可以提供三种主要类型的能力：
Resources: 可以被 clients 读取的类文件数据（如 API 响应或文件内容）
Tools: 可以被 LLM 调用的函数（需要用户批准）
Prompts: 预先编写的模板，帮助用户完成特定任务
本教程将主要关注 tools。
Python
Node
Java
Kotlin
C#
让我们开始构建我们的天气服务器！你可以在这里找到我们将构建的完整代码。
​
前提知识
本快速入门假设你熟悉：
Python
LLMs，如 Claude
​
系统要求
已安装 Python 3.10 或更高版本。
你必须使用 Python MCP SDK 1.2.0 或更高版本。
​
设置你的环境
首先，让我们安装 uv 并设置我们的 Python 项目和环境：

MacOS/Linux

Windows

Copy
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
之后请务必重启你的终端，以确保 uv 命令被识别。
现在，让我们创建并设置我们的项目：

MacOS/Linux

Windows

Copy
# 为我们的项目创建一个新 directory
uv init weather
cd weather

# 创建 virtual environment 并激活它
uv venv
.venv\Scripts\activate

# 安装 dependencies
uv add mcp[cli] httpx

# 创建我们的 server file
new-item weather.py
现在让我们深入构建你的服务器。
​
构建你的服务器
​
导入 packages 并设置 instance
将这些添加到你的 weather.py 文件的顶部：

Copy
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"
FastMCP class 使用 Python type hints 和 docstrings 来自动生成 tool definitions，从而轻松创建和维护 MCP tools。
​
Helper functions
接下来，让我们添加 helper functions，用于查询和格式化来自 National Weather Service API 的数据：

Copy
async def make_nws_request(url: str) -> dict[str, Any] | None:
    """向 NWS API 发送请求，并进行适当的错误处理。"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """将警报 feature 格式化为可读的字符串。"""
    props = feature["properties"]
    return f"""
事件: {props.get('event', 'Unknown')}
区域: {props.get('areaDesc', 'Unknown')}
严重性: {props.get('severity', 'Unknown')}
描述: {props.get('description', 'No description available')}
指示: {props.get('instruction', 'No specific instructions provided')}
"""
​
实现 tool execution
Tool execution handler 负责实际执行每个 tool 的逻辑。让我们添加它：

Copy
@mcp.tool()
async def get_alerts(state: str) -> str:
    """获取美国州的天气警报。

    Args:
        state: 两个字母的美国州代码（例如 CA、NY）
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "无法获取警报或未找到警报。"

    if not data["features"]:
        return "该州没有活跃的警报。"

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """获取某个位置的天气预报。

    Args:
        latitude: 位置的纬度
        longitude: 位置的经度
    """
    # 首先获取预报网格 endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "无法获取此位置的预报数据。"

    # 从 points response 中获取预报 URL
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "无法获取详细预报。"

    # 将 periods 格式化为可读的预报
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # 仅显示接下来的 5 个 periods
        forecast = f"""
{period['name']}:
温度: {period['temperature']}°{period['temperatureUnit']}
风: {period['windSpeed']} {period['windDirection']}
预报: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)
​
运行 server
最后，让我们初始化并运行 server：

Copy
if __name__ == "__main__":
    # 初始化并运行 server
    mcp.run(transport='stdio')
你的 server 已经完成！运行 uv run weather.py 以确认一切正常。
现在让我们从现有的 MCP host，Claude for Desktop 测试你的 server。
​
使用 Claude for Desktop 测试你的 server
Claude for Desktop 尚不适用于 Linux。Linux 用户可以继续阅读 构建 client 教程，以构建一个连接到我们刚刚构建的 server 的 MCP client。
首先，确保你已安装 Claude for Desktop。你可以在这里安装最新版本。 如果你已经安装了 Claude for Desktop，请确保它已更新到最新版本。
我们需要为你想要使用的任何 MCP servers 配置 Claude for Desktop。为此，请在文本编辑器中打开 ~/Library/Application Support/Claude/claude_desktop_config.json 中的 Claude for Desktop App configuration。如果该 file 不存在，请确保创建它。
例如，如果你安装了 VS Code：
MacOS/Linux
Windows

Copy
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
然后，你将在 mcpServers key 中添加你的 servers。只有正确配置了至少一个 server，MCP UI 元素才会显示在 Claude for Desktop 中。
在本例中，我们将添加我们的单个天气服务器，如下所示：
MacOS/Linux
Windows
Python

Copy
{
    "mcpServers": {
        "weather": {
            "command": "uv",
            "args": [
                "--directory",
                "C:\\ABSOLUTE\\PATH\\TO\\PARENT\\FOLDER\\weather",
                "run",
                "weather.py"
            ]
        }
    }
}
你可能需要在 command 字段中放入 uv executable 的完整 path。你可以在 MacOS/Linux 上运行 which uv 或在 Windows 上运行 where uv 来获取它。
确保你传入的是你的 server 的绝对 path。
这告诉 Claude for Desktop：
有一个名为 “weather” 的 MCP server
通过运行 uv --directory /ABSOLUTE/PATH/TO/PARENT/FOLDER/weather run weather.py 来启动它
保存 file，并重新启动 Claude for Desktop。
​
使用 commands 测试
让我们确保 Claude for Desktop 正在接收我们在 weather server 中暴露的两个 tools。你可以通过查找锤子  icon 来做到这一点：

单击锤子 icon 后，你应该看到列出了两个 tools：

如果你的 server 未被 Claude for Desktop 接收，请继续阅读 故障排除 部分以获取 debug 提示。
如果锤子 icon 已经显示，你现在可以通过在 Claude for Desktop 中运行以下 commands 来测试你的 server：
Sacramento 的天气怎么样？
Texas 有哪些活跃的天气警报？


由于这是美国国家气象局，因此查询仅适用于美国的位置。
​
底层发生了什么
当你提出问题时：
client 将你的问题发送给 Claude
Claude 分析可用的 tools 并决定使用哪些 tool
client 通过 MCP server 执行选择的 tool
结果被发回给 Claude
Claude 制定自然语言响应
响应显示给你！






核心概念
核心架构
了解 MCP 如何连接 clients、servers 和 LLMs

Model Context Protocol (MCP) 构建在一个灵活且可扩展的架构上，使 LLM 应用和集成之间的无缝通信成为可能。本文档涵盖了核心架构组件和概念。
​
概述
MCP 遵循一个 client-server 架构，其中：
Hosts 是 LLM 应用（如 Claude Desktop 或 IDEs），它们发起连接
Clients 在 host 应用中与 servers 保持 1:1 的连接
Servers 为 clients 提供上下文、tools 和 prompts
Server 进程

Server 进程

Host

传输层

传输层

MCP Client

MCP Client

MCP Server

MCP Server

​
核心组件
​
协议层
协议层处理消息框架、请求/响应链接和高级通信模式。
TypeScript
Python

Copy
class Protocol<Request, Notification, Result> {
    // 处理传入请求
    setRequestHandler<T>(schema: T, handler: (request: T, extra: RequestHandlerExtra) => Promise<Result>): void

    // 处理传入通知
    setNotificationHandler<T>(schema: T, handler: (notification: T) => Promise<void>): void

    // 发送请求并等待响应
    request<T>(request: Request, schema: T, options?: RequestOptions): Promise<T>

    // 发送单向通知
    notification(notification: Notification): Promise<void>
}
关键的 classes 包括：
Protocol
Client
Server
​
传输层
传输层处理 clients 和 servers 之间的实际通信。MCP 支持多种传输机制：
Stdio 传输
使用标准输入/输出进行通信
适用于本地进程
通过 HTTP 的 SSE 传输
使用服务器发送事件进行服务器到客户端的消息传递
使用 HTTP POST 进行客户端到服务器的消息传递
所有传输都使用 JSON-RPC 2.0 进行消息交换。有关 Model Context Protocol 消息格式的详细信息，请参阅规范。
​
消息类型
MCP 具有以下主要类型的消息：
Requests 期望来自另一端的响应：

Copy
interface Request {
  method: string;
  params?: { ... };
}
Results 是对请求的成功响应：

Copy
interface Result {
  [key: string]: unknown;
}
Errors 表示请求失败：

Copy
interface Error {
  code: number;
  message: string;
  data?: unknown;
}
Notifications 是不期望响应的单向消息：

Copy
interface Notification {
  method: string;
  params?: { ... };
}
​
连接生命周期
​
1. 初始化
Server
Client
Server
Client
连接准备就绪
初始化请求
初始化响应
已初始化通知
Client 发送包含协议版本和能力的 initialize 请求
Server 以其协议版本和能力响应
Client 发送 initialized 通知作为确认
开始正常消息交换
​
2. 消息交换
初始化后，支持以下模式：
请求-响应：客户端或服务器发送请求，另一方响应
通知：任一方发送单向消息
​
3. 终止
任一方可以终止连接：
通过 close() 进行干净关闭
传输断开
错误条件
​
错误处理
MCP 定义了以下标准错误代码：

Copy
enum ErrorCode {
  // 标准 JSON-RPC 错误代码
  ParseError = -32700,
  InvalidRequest = -32600,
  MethodNotFound = -32601,
  InvalidParams = -32602,
  InternalError = -32603
}
SDK 和应用可以定义其自己的错误代码，范围在 -32000 以上。
错误通过以下方式传播：
对请求的错误响应
传输上的错误事件
协议级别的错误处理程序
​
实现示例
以下是实现 MCP 服务器的基本示例：
TypeScript
Python

Copy
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({
  name: "example-server",
  version: "1.0.0"
}, {
  capabilities: {
    resources: {}
  }
});

// 处理请求
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: "example://resource",
        name: "Example Resource"
      }
    ]
  };
});

// 连接传输
const transport = new StdioServerTransport();
await server.connect(transport);
​
最佳实践
​
传输选择
本地通信
对于本地进程使用 stdio 传输
对于同一机器的通信效率高
简单的进程管理
远程通信
在需要 HTTP 兼容性的场景中使用 SSE
考虑安全隐患，包括身份验证和授权
​
消息处理
请求处理
彻底验证输入
使用类型安全的模式
优雅地处理错误
实现超时
进度报告
对于长时间操作使用进度令牌
增量报告进度
在已知时包括总进度
错误管理
使用适当的错误代码
包含有帮助的错误信息
在错误时清理资源
​
安全考虑
传输安全
对于远程连接使用 TLS
验证连接来源
在需要时实现身份验证
消息验证
验证所有传入消息
清理输入
检查消息大小限制
验证 JSON-RPC 格式
资源保护
实现访问控制
验证资源路径
监控资源使用
限制请求速率
错误处理
不泄露敏感信息
记录安全相关错误
实现适当的清理
处理 DoS 场景
​
调试和监控
日志记录
记录协议事件
跟踪消息流
监控性能
记录错误
诊断
实现健康检查
监控连接状态
跟踪资源使用
性能分析
测试
测试不同的传输
验证错误处理
检查边界情况
负载测试服务器


Resources
从你的 server 向 LLMs 暴露数据和内容

Resources 是 Model Context Protocol (MCP) 中的一个核心原语，它允许服务器暴露可以被 clients 读取并用作 LLM 交互上下文的数据和内容。
Resources 被设计为由应用控制，这意味着客户端应用程序可以决定如何以及何时使用它们。 不同的 MCP clients 可能会以不同的方式处理 resources。例如：
Claude Desktop 目前要求用户在可以使用 resources 之前显式地选择它们
其他 clients 可能会根据启发式方法自动选择 resources
某些实现甚至可能允许 AI 模型本身来确定使用哪些 resources
服务器作者在实现 resource 支持时，应该准备好处理任何这些交互模式。为了自动向模型暴露数据，服务器作者应该使用模型控制原语，例如 Tools。
​
概述
Resources 代表 MCP server 想要提供给 clients 的任何类型的数据。这可以包括：
文件内容
数据库记录
API 响应
实时系统数据
屏幕截图和图像
日志文件
等等
每个 resource 都由一个唯一的 URI 标识，并且可以包含文本或二进制数据。
​
Resource URIs
Resources 使用以下格式的 URIs 进行标识：

Copy
[protocol]://[host]/[path]
例如：
file:///home/user/documents/report.pdf
postgres://database/customers/schema
screen://localhost/display1
协议和路径结构由 MCP server 实现定义。服务器可以定义自己的自定义 URI 方案。
​
Resource 类型
Resources 可以包含两种类型的内容：
​
文本资源
文本资源包含 UTF-8 编码的文本数据。这些适用于：
源代码
配置文件
日志文件
JSON/XML 数据
纯文本
​
二进制资源
二进制资源包含以 base64 编码的原始二进制数据。这些适用于：
图像
PDFs
音频文件
视频文件
其他非文本格式
​
Resource 发现
Clients 可以通过两种主要方法发现可用的 resources：
​
直接 resources
服务器通过 resources/list 端点暴露一个具体的 resources 列表。每个 resource 包括：

Copy
{
  uri: string;           // 资源的唯一标识符
  name: string;          // 易于理解的名称
  description?: string;  // 可选描述
  mimeType?: string;     // 可选 MIME 类型
}
​
Resource 模板
对于动态 resources，服务器可以暴露 URI 模板，clients 可以使用它们来构造有效的 resource URIs：

Copy
{
  uriTemplate: string;   // 遵循 RFC 6570 的 URI 模板
  name: string;          // 这种类型的易于理解的名称
  description?: string;  // 可选描述
  mimeType?: string;     // 所有匹配资源的 MIME 类型（可选）
}
​
读取 resources
要读取 resource，clients 使用 resource URI 发送 resources/read 请求。
服务器使用一个 resource 内容列表进行响应：

Copy
{
  contents: [
    {
      uri: string;        // 资源的 URI
      mimeType?: string;  // 可选 MIME 类型

      // 其中之一：
      text?: string;      // 对于文本资源
      blob?: string;      // 对于二进制资源（base64 编码）
    }
  ]
}
服务器可能会响应一个 resources/read 请求返回多个 resources。例如，当读取目录时，可以使用此方法返回目录中的文件列表。
​
Resource 更新
MCP 通过两种机制支持 resources 的实时更新：
​
列表更改
当可用 resources 列表发生更改时，服务器可以通过 notifications/resources/list_changed 通知 clients。
​
内容更改
Clients 可以订阅特定 resources 的更新：
Client 使用 resource URI 发送 resources/subscribe
当 resource 更改时，服务器发送 notifications/resources/updated
Client 可以使用 resources/read 获取最新内容
Client 可以使用 resources/unsubscribe 取消订阅
​
实现示例
以下是在 MCP server 中实现 resource 支持的简单示例：
TypeScript
Python

Copy
const server = new Server({
  name: "example-server",
  version: "1.0.0"
}, {
  capabilities: {
    resources: {}
  }
});

// 列出可用 resources
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: "file:///logs/app.log",
        name: "Application Logs",
        mimeType: "text/plain"
      }
    ]
  };
});

// 读取 resource 内容
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const uri = request.params.uri;

  if (uri === "file:///logs/app.log") {
    const logContents = await readLogFile();
    return {
      contents: [
        {
          uri,
          mimeType: "text/plain",
          text: logContents
        }
      ]
    };
  }

  throw new Error("Resource not found");
});
​
最佳实践
在实现 resource 支持时：
使用清晰、描述性的 resource 名称和 URIs
包含有用的描述以指导 LLM 理解
在已知时设置适当的 MIME 类型
为动态内容实现 resource 模板
对频繁更改的 resources 使用订阅
使用清晰的错误消息优雅地处理错误
考虑对大型 resource 列表进行分页
在适当的时候缓存 resource 内容
在处理之前验证 URIs
记录你的自定义 URI 方案
​
安全考虑
在暴露 resources 时：
验证所有 resource URIs
实现适当的访问控制
清理文件路径以防止目录遍历
谨慎处理二进制数据
考虑对 resource 读取进行速率限制
审核 resource 访问
加密传输中的敏感数据
验证 MIME 类型
为长时间运行的读取操作实现超时
适当处理 resource 清理


Prompts
创建可复用的提示模板和工作流

Prompts 允许 servers 定义可复用的提示模板和工作流，clients 可以轻松地将它们呈现给用户和 LLMs。它们提供了一种强大的方式来标准化和共享常见的 LLM 交互。
Prompts 的设计是用户控制的，这意味着它们从 servers 暴露给 clients，目的是让用户能够明确地选择使用它们。
​
概述
MCP 中的 Prompts 是预定义的模板，可以：
接受动态参数
包含来自 resources 的上下文
链接多个交互
引导特定的工作流程
呈现为 UI 元素（如斜杠命令）
​
Prompt 结构
每个 prompt 都定义如下：

Copy
{
  name: string;              // Prompt 的唯一标识符
  description?: string;      // 易于理解的描述
  arguments?: [              // 可选的参数列表
    {
      name: string;          // 参数标识符
      description?: string;  // 参数描述
      required?: boolean;    // 参数是否必需
    }
  ]
}
​
发现 prompts
Clients 可以通过 prompts/list 端点发现可用的 prompts：

Copy
// 请求
{
  method: "prompts/list"
}

// 响应
{
  prompts: [
    {
      name: "analyze-code",
      description: "分析代码以获得潜在改进",
      arguments: [
        {
          name: "language",
          description: "编程语言",
          required: true
        }
      ]
    }
  ]
}
​
使用 prompts
要使用 prompt，clients 发出 prompts/get 请求：

Copy
// 请求
{
  method: "prompts/get",
  params: {
    name: "analyze-code",
    arguments: {
      language: "python"
    }
  }
}

// 响应
{
  description: "分析 Python 代码以获得潜在改进",
  messages: [
    {
      role: "user",
      content: {
        type: "text",
        text: "请分析以下 Python 代码以获得潜在改进:\n\n```python\ndef calculate_sum(numbers):\n    total = 0\n    for num in numbers:\n        total = total + num\n    return total\n\nresult = calculate_sum([1, 2, 3, 4, 5])\nprint(result)\n```"
      }
    }
  ]
}
​
动态 prompts
Prompts 可以是动态的，并且包括：
​
嵌入的 resource 上下文

Copy
{
  "name": "analyze-project",
  "description": "分析项目日志和代码",
  "arguments": [
    {
      "name": "timeframe",
      "description": "分析日志的时间段",
      "required": true
    },
    {
      "name": "fileUri",
      "description": "要审查的代码文件的 URI",
      "required": true
    }
  ]
}
当处理 prompts/get 请求时：

Copy
{
  "messages": [
    {
      "role": "user",
      "content": {
        "type": "text",
        "text": "分析这些系统日志和代码文件以查找任何问题:"
      }
    },
    {
      "role": "user",
      "content": {
        "type": "resource",
        "resource": {
          "uri": "logs://recent?timeframe=1h",
          "text": "[2024-03-14 15:32:11] ERROR: Connection timeout in network.py:127\n[2024-03-14 15:32:15] WARN: Retrying connection (attempt 2/3)\n[2024-03-14 15:32:20] ERROR: Max retries exceeded",
          "mimeType": "text/plain"
        }
      }
    },
    {
      "role": "user",
      "content": {
        "type": "resource",
        "resource": {
          "uri": "file:///path/to/code.py",
          "text": "def connect_to_service(timeout=30):\n    retries = 3\n    for attempt in range(retries):\n        try:\n            return establish_connection(timeout)\n        except TimeoutError:\n            if attempt == retries - 1:\n                raise\n            time.sleep(5)\n\ndef establish_connection(timeout):\n    # Connection implementation\n    pass",
          "mimeType": "text/x-python"
        }
      }
    }
  ]
}
​
多步骤工作流程

Copy
const debugWorkflow = {
  name: "debug-error",
  async getMessages(error: string) {
    return [
      {
        role: "user",
        content: {
          type: "text",
          text: `我看到的错误是: ${error}`
        }
      },
      {
        role: "assistant",
        content: {
          type: "text",
          text: "我将帮助分析这个错误。你到目前为止尝试了什么？"
        }
      },
      {
        role: "user",
        content: {
          type: "text",
          text: "我已经尝试重新启动服务，但错误仍然存在。"
        }
      }
    ];
  }
};
​
实现示例
以下是在 MCP server 中实现 prompts 的完整示例：
TypeScript
Python

Copy
import { Server } from "@modelcontextprotocol/sdk/server";
import {
  ListPromptsRequestSchema,
  GetPromptRequestSchema
} from "@modelcontextprotocol/sdk/types";

const PROMPTS = {
  "git-commit": {
    name: "git-commit",
    description: "生成 Git commit 消息",
    arguments: [
      {
        name: "changes",
        description: "Git diff 或更改描述",
        required: true
      }
    ]
  },
  "explain-code": {
    name: "explain-code",
    description: "解释代码的工作原理",
    arguments: [
      {
        name: "code",
        description: "要解释的代码",
        required: true
      },
      {
        name: "language",
        description: "编程语言",
        required: false
      }
    ]
  }
};

const server = new Server({
  name: "example-prompts-server",
  version: "1.0.0"
}, {
  capabilities: {
    prompts: {}
  }
});

// 列出可用的 prompts
server.setRequestHandler(ListPromptsRequestSchema, async () => {
  return {
    prompts: Object.values(PROMPTS)
  };
});

// 获取特定的 prompt
server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const prompt = PROMPTS[request.params.name];
  if (!prompt) {
    throw new Error(`未找到 prompt: ${request.params.name}`);
  }

  if (request.params.name === "git-commit") {
    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `为这些更改生成简洁但描述性的 commit 消息:\n\n${request.params.arguments?.changes}`
          }
        }
      ]
    };
  }

  if (request.params.name === "explain-code") {
    const language = request.params.arguments?.language || "未知";
    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `解释这段 ${language} 代码的工作原理:\n\n${request.params.arguments?.code}`
          }
        }
      ]
    };
  }

  throw new Error("未找到 prompt 实现");
});
​
最佳实践
在实现 prompts 时：
使用清晰、描述性的 prompt 名称
为 prompts 和参数提供详细的描述
验证所有必需的参数
优雅地处理缺失的参数
考虑 prompt 模板的版本控制
在适当的时候缓存动态内容
实现错误处理
记录预期的参数格式
考虑 prompt 的可组合性
使用各种输入测试 prompts
​
UI 集成
Prompts 可以在 client UI 中呈现为：
斜杠命令
快速操作
上下文菜单项
命令面板条目
引导式工作流程
交互式表单
​
更新和更改
Servers 可以通知 clients 关于 prompt 的更改：
Server 功能：prompts.listChanged
通知：notifications/prompts/list_changed
Client 重新获取 prompt 列表
​
安全考虑
在实现 prompts 时：
验证所有参数
清理用户输入
考虑速率限制
实现访问控制
审计 prompt 使用情况
适当地处理敏感数据
验证生成的内容
实现超时
考虑 prompt 注入风险
记录安全要求

Tools
让 LLMs 通过你的 server 执行操作

Tools 是 Model Context Protocol (MCP) 中的一个强大原语，它使 servers 能够向 clients 暴露可执行功能。通过 tools，LLMs 可以与外部系统交互、执行计算并在现实世界中采取行动。
Tools 被设计为模型控制，这意味着 tools 从 servers 暴露给 clients，目的是 AI 模型能够自动调用它们（需要人工介入以授予批准）。
​
概述
MCP 中的 Tools 允许 servers 暴露可执行函数，这些函数可以被 clients 调用，并被 LLMs 用于执行操作。Tools 的关键方面包括：
Discovery (发现)：Clients 可以通过 tools/list endpoint 列出可用的 tools
Invocation (调用)：Tools 使用 tools/call endpoint 调用，其中 servers 执行请求的操作并返回结果
Flexibility (灵活性)：Tools 的范围可以从简单的计算到复杂的 API 交互
与 resources 一样，tools 通过唯一的名称进行标识，并且可以包含描述以指导其使用。但是，与 resources 不同的是，tools 代表可以修改状态或与外部系统交互的动态操作。
​
Tool 定义结构
每个 tool 都使用以下结构定义：

Copy
{
  name: string;          // Tool 的唯一标识符
  description?: string;  // 供人阅读的描述
  inputSchema: {         // Tool 参数的 JSON Schema
    type: "object",
    properties: { ... }  // Tool 特定的参数
  }
}
​
实现 tools
以下是在 MCP server 中实现一个基本 tool 的示例：
TypeScript
Python

Copy
const server = new Server({
  name: "example-server",
  version: "1.0.0"
}, {
  capabilities: {
    tools: {}
  }
});

// 定义可用的 tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [{
      name: "calculate_sum",
      description: "将两个数字加在一起",
      inputSchema: {
        type: "object",
        properties: {
          a: { type: "number" },
          b: { type: "number" }
        },
        required: ["a", "b"]
      }
    }]
  };
});

// 处理 tool 执行
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "calculate_sum") {
    const { a, b } = request.params.arguments;
    return {
      content: [
        {
          type: "text",
          text: String(a + b)
        }
      ]
    };
  }
  throw new Error("Tool not found");
});
​
示例 tool 模式
以下是 server 可以提供的 tool 类型的示例：
​
系统操作
与本地系统交互的 tools：

Copy
{
  name: "execute_command",
  description: "运行 shell 命令",
  inputSchema: {
    type: "object",
    properties: {
      command: { type: "string" },
      args: { type: "array", items: { type: "string" } }
    }
  }
}
​
API 集成
封装外部 APIs 的 tools：

Copy
{
  name: "github_create_issue",
  description: "创建 GitHub issue",
  inputSchema: {
    type: "object",
    properties: {
      title: { type: "string" },
      body: { type: "string" },
      labels: { type: "array", items: { type: "string" } }
    }
  }
}
​
数据处理
转换或分析数据的 tools：

Copy
{
  name: "analyze_csv",
  description: "分析 CSV 文件",
  inputSchema: {
    type: "object",
    properties: {
      filepath: { type: "string" },
      operations: {
        type: "array",
        items: {
          enum: ["sum", "average", "count"]
        }
      }
    }
  }
}
​
最佳实践
在实现 tools 时：
提供清晰、描述性的名称和描述
为参数使用详细的 JSON Schema 定义
在 tool 描述中包含示例，以演示模型应如何使用它们
实现适当的错误处理和验证
对长时间运行的操作使用进度报告
保持 tool 操作的 focus 和原子性
记录预期的返回值结构
实现适当的超时
考虑对资源密集型操作进行速率限制
记录 tool 使用情况以进行调试和监控
​
安全考虑
在暴露 tools 时：
​
输入验证
根据 schema 验证所有参数
清理文件路径和系统命令
验证 URL 和外部标识符
检查参数大小和范围
阻止命令注入
​
访问控制
在需要时实现身份验证
使用适当的授权检查
审计 tool 使用情况
限制请求速率
监控滥用情况
​
错误处理
不要向 clients 暴露内部错误
记录与安全相关的错误
适当地处理超时
在出错后清理资源
验证返回值
​
Tool 发现和更新
MCP 支持动态 tool 发现：
Clients 可以在任何时候列出可用的 tools
Servers 可以在 tools 更改时使用 notifications/tools/list_changed 通知 clients
可以在运行时添加或删除 tools
可以更新 tool 定义（尽管应该谨慎进行）
​
错误处理
Tool 错误应在 result 对象中报告，而不是作为 MCP 协议级别的错误。这允许 LLM 看到并可能处理错误。当 tool 遇到错误时：
在 result 中将 isError 设置为 true
在 content 数组中包含错误详细信息
以下是 tools 的正确错误处理示例：
TypeScript
Python

Copy
try {
  // Tool operation
  const result = performOperation();
  return {
    content: [
      {
        type: "text",
        text: `Operation successful: ${result}`
      }
    ]
  };
} catch (error) {
  return {
    isError: true,
    content: [
      {
        type: "text",
        text: `Error: ${error.message}`
      }
    ]
  };
}
这种方法允许 LLM 看到发生了错误，并可能采取纠正措施或请求人工干预。
​
测试 tools
MCP tools 的综合测试策略应涵盖：
功能测试：验证 tools 是否使用有效输入正确执行，并适当地处理无效输入
集成测试：使用真实和模拟的依赖项测试 tool 与外部系统的交互
安全测试：验证身份验证、授权、输入清理和速率限制
性能测试：检查负载下的行为、超时处理和资源清理
错误处理：确保 tools 通过 MCP 协议正确报告错误并清理资源


Sampling
让你的 servers 从 LLMs 请求补全

Sampling 是一个强大的 MCP 功能，它允许 servers 通过 client 请求 LLM 补全，从而实现复杂的 agentic 行为，同时保持安全性和隐私性。
Claude Desktop client 尚未支持此 MCP 功能。
​
Sampling 的工作原理
Sampling 流程遵循以下步骤：
Server 向 client 发送 sampling/createMessage 请求
Client 审查请求并可以修改它
Client 从 LLM 中 sampling
Client 审查补全结果
Client 将结果返回给 server
这种人机交互设计确保用户可以控制 LLM 看到和生成的内容。
​
消息格式
Sampling 请求使用标准化的消息格式：

Copy
{
  messages: [
    {
      role: "user" | "assistant",
      content: {
        type: "text" | "image",

        // 对于文本：
        text?: string,

        // 对于图像：
        data?: string,             // base64 编码
        mimeType?: string
      }
    }
  ],
  modelPreferences?: {
    hints?: [{
      name?: string                // 建议的模型名称/系列
    }],
    costPriority?: number,         // 0-1，最小化成本的重要性
    speedPriority?: number,        // 0-1，低延迟的重要性
    intelligencePriority?: number  // 0-1，高级功能的重要性
  },
  systemPrompt?: string,
  includeContext?: "none" | "thisServer" | "allServers",
  temperature?: number,
  maxTokens: number,
  stopSequences?: string[],
  metadata?: Record<string, unknown>
}
​
请求参数
​
Messages
messages 数组包含要发送给 LLM 的对话历史。每条消息都有：
role：“user” 或 “assistant”
content：消息内容，可以是：
带有 text 字段的文本内容
带有 data (base64) 和 mimeType 字段的图像内容
​
模型偏好
modelPreferences 对象允许 servers 指定他们的模型选择偏好：
hints：模型名称建议的数组，clients 可以使用它来选择合适的模型：
name：可以匹配完整或部分模型名称的字符串（例如 “claude-3”, “sonnet”）
Clients 可能会将提示映射到来自不同提供商的等效模型
多个提示按优先顺序评估
优先级值（0-1 归一化）：
costPriority：最小化成本的重要性
speedPriority：低延迟响应的重要性
intelligencePriority：高级模型功能的重要性
Clients 根据这些偏好及其可用模型进行最终的模型选择。
​
System prompt
可选的 systemPrompt 字段允许 servers 请求特定的 system prompt。Client 可能会修改或忽略它。
​
上下文包含
includeContext 参数指定要包含的 MCP 上下文：
"none"：不包含任何额外的上下文
"thisServer"：包含来自请求 server 的上下文
"allServers"：包含来自所有已连接 MCP servers 的上下文
Client 控制实际包含的上下文。
​
Sampling 参数
使用以下参数微调 LLM sampling：
temperature：控制随机性（0.0 到 1.0）
maxTokens：要生成的最大 tokens 数
stopSequences：停止生成的序列数组
metadata：其他特定于提供商的参数
​
响应格式
Client 返回一个补全结果：

Copy
{
  model: string,  // 使用的模型的名称
  stopReason?: "endTurn" | "stopSequence" | "maxTokens" | string,
  role: "user" | "assistant",
  content: {
    type: "text" | "image",
    text?: string,
    data?: string,
    mimeType?: string
  }
}
​
示例请求
以下是从 client 请求 sampling 的示例：

Copy
{
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "当前目录中有哪些文件？"
        }
      }
    ],
    "systemPrompt": "你是一个有用的文件系统助手。",
    "includeContext": "thisServer",
    "maxTokens": 100
  }
}
​
最佳实践
在实现 sampling 时：
始终提供清晰、结构良好的 prompts
适当地处理文本和图像内容
设置合理的 token 限制
通过 includeContext 包含相关上下文
在使用响应之前验证它们
优雅地处理错误
考虑限制 sampling 请求的速率
记录预期的 sampling 行为
使用各种模型参数进行测试
监控 sampling 成本
​
人工干预控制
Sampling 的设计考虑到了人工监督：
​
对于 prompts
Clients 应该向用户显示建议的 prompt
用户应该能够修改或拒绝 prompts
System prompts 可以被过滤或修改
上下文包含由 client 控制
​
对于补全结果
Clients 应该向用户显示补全结果
用户应该能够修改或拒绝补全结果
Clients 可以过滤或修改补全结果
用户控制使用哪个模型
​
安全考虑
在实现 sampling 时：
验证所有消息内容
清理敏感信息
实现适当的速率限制
监控 sampling 使用情况
加密传输中的数据
处理用户数据隐私
审计 sampling 请求
控制成本暴露
实现超时
优雅地处理模型错误
​
常见模式
​
Agentic 工作流
Sampling 实现了 agentic 模式，例如：
读取和分析 resources
根据上下文做出决策
生成结构化数据
处理多步任务
提供交互式帮助
​
上下文管理
上下文的最佳实践：
请求最少必要的上下文
清楚地构建上下文
处理上下文大小限制
根据需要更新上下文
清理过时的上下文
​
错误处理
强大的错误处理应：
捕获 sampling 失败
处理超时错误
管理速率限制
验证响应
提供回退行为
适当地记录错误
​
限制
请注意以下限制：
Sampling 依赖于 client 的功能
用户控制 sampling 行为
上下文大小有限制
可能会应用速率限制
应该考虑成本
模型可用性各不相同
响应时间各不相同
并非所有内容类型都受支持

Roots
了解 MCP 中的 roots

Roots 是 MCP 中的一个概念，它定义了 servers 可以操作的边界。它们为 clients 提供了一种方式，可以告知 servers 有关相关 resources 及其位置的信息。
​
什么是 Roots？
一个 root 是一个 URI，client 建议 server 应该关注它。当 client 连接到 server 时，它声明 server 应该使用哪些 roots。虽然主要用于文件系统路径，但 roots 可以是任何有效的 URI，包括 HTTP URL。
例如，roots 可以是：

Copy
file:///home/user/projects/myapp
https://api.example.com/v1
​
为什么要使用 Roots？
Roots 有几个重要的用途：
指导: 它们告知 servers 有关相关 resources 和位置的信息
清晰: Roots 明确了哪些 resources 是你的 workspace 的一部分
组织: 多个 roots 允许你同时使用不同的 resources
​
Roots 如何工作
当 client 支持 roots 时，它：
在连接期间声明 roots capability
向 server 提供建议的 roots 列表
在 roots 更改时通知 server (如果支持)
虽然 roots 是信息性的，并且不严格执行，但 servers 应该：
尊重提供的 roots
使用 root URIs 来定位和访问 resources
优先考虑 root 边界内的操作
​
常见用例
Roots 经常用于定义：
项目目录
仓库位置
API endpoints
配置位置
Resource 边界
​
最佳实践
在使用 roots 时：
仅建议必要的 resources
为 roots 使用清晰、描述性的名称
监控 root 的可访问性
优雅地处理 root 更改
​
示例
以下是一个典型的 MCP client 可能如何暴露 roots 的示例：

Copy
{
  "roots": [
    {
      "uri": "file:///home/user/projects/frontend",
      "name": "Frontend Repository"
    },
    {
      "uri": "https://api.example.com/v1",
      "name": "API Endpoint"
    }
  ]
}
此配置建议 server 关注本地 repository 和 API endpoint，同时保持它们在逻辑上分离。

传输层
了解 MCP 的通信机制

Model Context Protocol (MCP) 中的传输层为 clients 和 servers 之间的通信提供基础。传输层处理消息发送和接收的底层机制。
​
消息格式
MCP 使用 JSON-RPC 2.0 作为其传输格式。传输层负责将 MCP 协议消息转换为 JSON-RPC 格式进行传输，并将接收到的 JSON-RPC 消息转换回 MCP 协议消息。
使用的 JSON-RPC 消息有三种类型：
​
请求

Copy
{
  jsonrpc: "2.0",
  id: number | string,
  method: string,
  params?: object
}
​
响应

Copy
{
  jsonrpc: "2.0",
  id: number | string,
  result?: object,
  error?: {
    code: number,
    message: string,
    data?: unknown
  }
}
​
通知

Copy
{
  jsonrpc: "2.0",
  method: string,
  params?: object
}
​
内置传输层种类
MCP 包含两个标准传输实现：
​
标准输入输出 (stdio)
stdio 传输通过标准输入和输出流进行通信。这对于本地集成和命令行工具特别有用。
在以下情况下使用 stdio：
构建命令行工具
实现本地集成
需要简单的进程通信
使用 shell 脚本
TypeScript (Server)
TypeScript (Client)
Python (Server)
Python (Client)

Copy
const server = new Server({
  name: "example-server",
  version: "1.0.0"
}, {
  capabilities: {}
});

const transport = new StdioServerTransport();
await server.connect(transport);
​
服务器发送事件 (SSE)
SSE 传输通过 HTTP POST 请求实现服务器到客户端的流式通信。
在以下情况下使用 SSE：
仅需要 server-to-client 的流式通信
在受限网络中工作
实现简单更新
TypeScript (Server)
TypeScript (Client)
Python (Server)
Python (Client)

Copy
import express from "express";

const app = express();

const server = new Server({
  name: "example-server",
  version: "1.0.0"
}, {
  capabilities: {}
});

let transport: SSEServerTransport | null = null;

app.get("/sse", (req, res) => {
  transport = new SSEServerTransport("/messages", res);
  server.connect(transport);
});

app.post("/messages", (req, res) => {
  if (transport) {
    transport.handlePostMessage(req, res);
  }
});

app.listen(3000);
​
自定义传输层
MCP 使得为特定需求实现自定义传输层变得简单。任何传输层实现只需符合 Transport 接口：
你可以为以下情况实现自定义传输：
自定义网络协议
专用通信通道
与现有系统集成
性能优化
TypeScript
Python

Copy
interface Transport {
  // 开始处理消息
  start(): Promise<void>;

  // 发送 JSON-RPC 消息
  send(message: JSONRPCMessage): Promise<void>;

  // 关闭连接
  close(): Promise<void>;

  // 回调函数
  onclose?: () => void;
  onerror?: (error: Error) => void;
  onmessage?: (message: JSONRPCMessage) => void;
}
​
错误处理
传输实现应处理各种错误场景：
连接错误
消息解析错误
协议错误
网络超时
资源清理
错误处理示例：
TypeScript
Python

Copy
class ExampleTransport implements Transport {
  async start() {
    try {
      // 连接逻辑
    } catch (error) {
      this.onerror?.(new Error(`连接失败: ${error}`));
      throw error;
    }
  }

  async send(message: JSONRPCMessage) {
    try {
      // 发送逻辑
    } catch (error) {
      this.onerror?.(new Error(`消息发送失败: ${error}`));
      throw error;
    }
  }
}
​
最佳实践
在实现或使用 MCP 传输时：
正确处理连接生命周期
实现适当的错误处理
在连接关闭时清理资源
使用适当的超时
在发送前验证消息
记录传输事件以便调试
在适当时实现重连逻辑
处理消息队列中的背压
监控连接健康状况
实现适当的安全措施
​
安全考虑
在实现传输时：
​
认证和授权
实现适当的认证机制
验证客户端凭据
使用安全的令牌处理
实现授权检查
​
数据安全
使用 TLS 进行网络传输
加密敏感数据
验证消息完整性
实现消息大小限制
对输入数据 sanitize
​
网络安全
实现速率限制
使用适当的超时
处理拒绝服务场景
监控异常模式
实施适当的防火墙规则
​
调试传输
一些 Debug 传输层问题的提示：
启用调试日志
监控消息流
检查连接状态
验证消息格式
测试错误场景
使用网络分析工具
实现健康检查
监控资源使用
测试边界情况
使用适当的错误跟踪
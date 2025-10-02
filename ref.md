# Desmos-MCP 服务器开发文档

## 项目概述

Desmos-MCP 是一个标准的 Model Context Protocol (MCP) 服务器，专为让大语言模型 (LLM) 调用数学公式可视化功能而设计。该服务器能够接收数学公式输入，处理并返回二维数学图形可视化结果，未来将扩展支持三维图形。

## 功能特性

* **公式解析**：接收并解析各种数学公式格式
* **图形生成**：生成高质量的二维数学图形
* **双模式支持**：支持 Desmos API 在线模式和离线本地渲染
* **标准 MCP 协议**：完全兼容 MCP 规范
* **高效处理**：优化的公式处理和图形生成流程

## 技术架构

### 核心组件

```
Desmos-MCP Server
├── MCP Protocol Handler
├── Formula Parser
├── Desmos API Integration
├── Local Rendering Engine
├── Image Generator
└── Resource Manager
```

## MCP 服务器规格

### 暴露的资源 (Resources)

#### 1. 支持的数学函数库

* **资源 ID**: `math-functions`
* **类型**: `application/json`
* **描述**: 包含所有支持的数学函数、运算符和常量的完整列表
* **内容**: 函数名称、语法、参数说明、示例

#### 2. 图形样式模板

* **资源 ID**: `graph-templates`
* **类型**: `application/json`
* **描述**: 预定义的图形样式和配置模板
* **内容**: 颜色方案、坐标轴设置、网格配置等

#### 3. 示例公式集合

* **资源 ID**: `example-formulas`
* **类型**: `text/plain`
* **描述**: 常用数学公式示例和最佳实践
* **内容**: 分类的公式示例（代数、几何、微积分等）

### 提供的工具 (Tools)

#### 1. 绘制数学图形

```json
{
  "name": "plot_math_function",
  "description": "根据数学公式生成二维图形",
  "inputSchema": {
    "type": "object",
    "properties": {
      "formula": {
        "type": "string",
        "description": "数学公式，支持标准数学表示法"
      },
      "x_range": {
        "type": "array",
        "items": {"type": "number"},
        "description": "x轴范围 [min, max]",
        "default": [-10, 10]
      },
      "y_range": {
        "type": "array",
        "items": {"type": "number"},
        "description": "y轴范围 [min, max]",
        "default": [-10, 10]
      },
      "width": {
        "type": "integer",
        "description": "图像宽度（像素）",
        "default": 600
      },
      "height": {
        "type": "integer",
        "description": "图像高度（像素）",
        "default": 400
      },
      "style": {
        "type": "object",
        "description": "图形样式配置",
        "properties": {
          "color": {"type": "string", "default": "#c74440"},
          "lineWidth": {"type": "number", "default": 2},
          "showGrid": {"type": "boolean", "default": true},
          "showAxes": {"type": "boolean", "default": true}
        }
      }
    },
    "required": ["formula"]
  }
}
```

#### 2. 验证数学公式

```json
{
  "name": "validate_formula",
  "description": "验证数学公式的语法正确性",
  "inputSchema": {
    "type": "object",
    "properties": {
      "formula": {
        "type": "string",
        "description": "待验证的数学公式"
      }
    },
    "required": ["formula"]
  }
}
```

#### 3. 获取公式信息

```json
{
  "name": "analyze_formula",
  "description": "分析数学公式的特性（定义域、值域、特殊点等）",
  "inputSchema": {
    "type": "object",
    "properties": {
      "formula": {
        "type": "string",
        "description": "要分析的数学公式"
      },
      "analysis_type": {
        "type": "string",
        "enum": ["basic", "detailed", "critical_points"],
        "description": "分析类型",
        "default": "basic"
      }
    },
    "required": ["formula"]
  }
}
```

#### 4. 批量绘图

```json
{
  "name": "plot_multiple_functions",
  "description": "在同一图形中绘制多个数学函数",
  "inputSchema": {
    "type": "object",
    "properties": {
      "formulas": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "formula": {"type": "string"},
            "color": {"type": "string"},
            "label": {"type": "string"}
          },
          "required": ["formula"]
        },
        "description": "要绘制的函数列表"
      },
      "x_range": {
        "type": "array",
        "items": {"type": "number"},
        "description": "x轴范围",
        "default": [-10, 10]
      },
      "y_range": {
        "type": "array",
        "items": {"type": "number"},
        "description": "y轴范围",
        "default": [-10, 10]
      },
      "width": {"type": "integer", "default": 600},
      "height": {"type": "integer", "default": 400}
    },
    "required": ["formulas"]
  }
}
```

### 提示模板 (Prompts)

#### 1. 基础图形绘制助手

```json
{
  "name": "basic_graphing_assistant",
  "description": "协助用户绘制基本的数学函数图形",
  "arguments": [
    {
      "name": "function_type",
      "description": "函数类型（linear, quadratic, exponential, etc.）",
      "required": false
    }
  ]
}
```

#### 2. 高级数学分析

```json
{
  "name": "advanced_math_analysis",
  "description": "对复杂数学函数进行深度分析和可视化",
  "arguments": [
    {
      "name": "analysis_focus",
      "description": "分析重点（derivatives, integrals, limits, etc.）",
      "required": false
    }
  ]
}
```

#### 3. 教学辅助工具

```json
{
  "name": "educational_math_helper",
  "description": "为教学场景提供数学可视化支持",
  "arguments": [
    {
      "name": "grade_level",
      "description": "教学年级水平",
      "required": false
    },
    {
      "name": "concept",
      "description": "要可视化的数学概念",
      "required": false
    }
  ]
}
```

## 外部系统交互

### 1. Desmos API 集成

* **API 端点**: `https://www.desmos.com/api/v1.11/`
* **认证方式**: API Key
* **主要功能**:

  * 图形生成
  * 公式验证
  * 样式配置
  * 导出功能

### 2. 本地渲染引擎

* **渲染库**: matplotlib + sympy (Python) 或 canvas + math.js (JavaScript)
* **功能**:

  * 离线公式解析
  * 本地图形生成
  * 自定义样式支持

### 3. 文件系统交互

* **图像缓存**: 临时存储生成的图像文件
* **配置管理**: 读取用户配置和样式模板
* **日志记录**: 操作日志和错误记录

## 技术实现细节

### 支持的数学表达式格式

#### 基础运算符

* `+`, `-`, `*`, `/`, `^` (或 `**`)
* `sqrt()`, `abs()`, `log()`, `ln()`

#### 三角函数

* `sin()`, `cos()`, `tan()`
* `asin()`, `acos()`, `atan()`
* `sinh()`, `cosh()`, `tanh()`

#### 特殊函数

* `exp()`, `floor()`, `ceil()`
* `max()`, `min()`, `mod()`

#### 常量

* `pi`, `e`, `infinity`

### 输出格式

#### 图像输出

* **格式**: PNG, SVG, JPEG
* **分辨率**: 可配置，默认 600x400
* **压缩**: 自动优化文件大小

#### 数据输出

```json
{
  "success": true,
  "image_url": "data:image/png;base64,iVBORw0KGgo...",
  "image_format": "png",
  "dimensions": {
    "width": 600,
    "height": 400
  },
  "formula_info": {
    "original": "y = x^2 + 2x + 1",
    "parsed": "y = x² + 2x + 1",
    "domain": "(-∞, +∞)",
    "range": "[0, +∞)"
  },
  "metadata": {
    "generation_time": "0.234s",
    "mode": "desmos_api",
    "cache_hit": false
  }
}
```

## 配置选项

### 服务器配置

```json
{
  "server": {
    "name": "desmos-mcp",
    "version": "1.0.0",
    "port": 3000,
    "host": "localhost"
  },
  "desmos": {
    "api_key": "YOUR_API_KEY",
    "use_api": true,
    "fallback_to_local": true
  },
  "rendering": {
    "default_width": 600,
    "default_height": 400,
    "max_width": 1920,
    "max_height": 1080,
    "cache_enabled": true,
    "cache_ttl": 3600
  },
  "limits": {
    "max_formulas_per_request": 10,
    "timeout": 30000,
    "rate_limit": "100/hour"
  }
}
```

## 错误处理

### 错误类型和处理策略

#### 1. 公式解析错误

* **错误码**: `FORMULA_PARSE_ERROR`
* **处理**: 返回详细的语法错误信息和建议修正

#### 2. API 调用失败

* **错误码**: `DESMOS_API_ERROR`
* **处理**: 自动切换到本地渲染模式

#### 3. 渲染超时

* **错误码**: `RENDER_TIMEOUT`
* **处理**: 返回简化版本或提示用户调整参数

#### 4. 资源限制

* **错误码**: `RESOURCE_LIMIT_EXCEEDED`
* **处理**: 返回限制信息和优化建议

## 性能优化

### 缓存策略

* **公式缓存**: 相同公式和参数的结果缓存
* **图像缓存**: 生成的图像文件缓存
* **API 响应缓存**: Desmos API 调用结果缓存

### 并发处理

* **请求队列**: 管理并发绘图请求
* **资源池**: 复用渲染引擎实例
* **异步处理**: 非阻塞的图像生成

## 安全考虑

### 输入验证

* **公式安全检查**: 防止恶意代码执行
* **参数边界检查**: 限制绘图范围和分辨率
* **API 密钥保护**: 安全存储和传输 API 凭证

### 资源保护

* **内存限制**: 防止内存溢出
* **CPU 限制**: 限制渲染时间
* **磁盘空间管理**: 自动清理临时文件

## 部署指南

### 环境要求

* **运行时**: Node.js 18+ 或 Python 3.9+
* **依赖**: 根据实现语言安装相应的数学库
* **网络**: 访问 Desmos API（在线模式）

### 安装步骤

1. 克隆项目代码
2. 安装依赖包
3. 配置 API 密钥
4. 启动 MCP 服务器
5. 连接到 MCP 客户端

### Docker 部署

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

## 测试策略

### 单元测试

* **公式解析器测试**: 验证各种数学表达式的解析正确性
* **图像生成测试**: 检查生成图像的质量和准确性
* **API 集成测试**: 测试与 Desmos API 的交互

### 集成测试

* **MCP 协议测试**: 验证服务器与客户端的通信
* **端到端测试**: 完整的用户场景测试
* **性能测试**: 负载和压力测试

### 测试用例

```javascript
// 示例测试用例
describe('Formula Parsing', () => {
  test('should parse linear function', () => {
    const result = parseFormula('y = 2x + 1');
    expect(result.type).toBe('linear');
    expect(result.coefficients).toEqual([2, 1]);
  });
  
  test('should handle quadratic function', () => {
    const result = parseFormula('y = x^2 - 4x + 3');
    expect(result.type).toBe('quadratic');
  });
});
```

## 监控和日志

### 日志记录

* **访问日志**: 记录所有 API 调用
* **错误日志**: 详细的错误信息和堆栈跟踪
* **性能日志**: 渲染时间和资源使用情况

### 监控指标

* **请求量**: 每分钟/小时的请求数
* **成功率**: API 调用成功率
* **响应时间**: 平均和P99响应时间
* **错误率**: 各种错误类型的发生率

## 扩展计划

### 短期目标

* **三维图形支持**: 扩展到3D数学函数可视化
* **动画功能**: 支持参数变化的动态图形
* **更多数学函数**: 扩展支持的函数库

### 长期目标

* **机器学习集成**: 智能公式建议和优化
* **多语言支持**: 国际化的数学表达式
* **云服务集成**: 与主流云平台的集成

## API 参考文档

### MCP 消息格式

#### 工具调用请求

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "plot_math_function",
    "arguments": {
      "formula": "y = sin(x)",
      "x_range": [-6.28, 6.28],
      "y_range": [-2, 2],
      "style": {
        "color": "#2563eb",
        "showGrid": true
      }
    }
  }
}
```

#### 工具调用响应

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "content": [
      {
        "type": "image",
        "data": "data:image/png;base64,iVBORw0KGgo...",
        "mimeType": "image/png"
      },
      {
        "type": "text",
        "text": "成功生成正弦函数图形。函数域: [-6.28, 6.28], 值域: [-1, 1]"
      }
    ],
    "isError": false
  }
}
```

这份开发文档为 Desmos-MCP 服务器的完整开发提供了详细的规格说明和实现指导，涵盖了从架构设计到部署维护的各个方面，为开发团队提供了清晰的开发路线图。

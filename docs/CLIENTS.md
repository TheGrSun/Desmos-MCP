# Client setup / 客户端接入

Use an MCP client that supports local stdio servers. It launches this process and communicates via stdin/stdout.
服务器由客户端启动，使用标准输入输出通信。

## Copyable configuration

For clients accepting `mcpServers` JSON (for example Claude Desktop):

```json
{
  "mcpServers": {
    "desmos-mcp": {
      "command": "uv",
      "args": ["--directory", "/ABSOLUTE/PATH/Desmos-MCP", "run", "--locked", "desmos-mcp", "--config", "/ABSOLUTE/PATH/Desmos-MCP/config.json"]
    }
  }
}
```

Replace **both** repository paths. On Windows use an absolute path such as `C:\\Projects\\Desmos-MCP` inside JSON.
For clients using another configuration format, copy the same command and argument array into its stdio server settings.
JSON 的两个仓库路径都需要替换；使用其他配置格式的客户端时，保留相同 command 和 args 即可。

If a GUI client cannot find `uv`, use the absolute executable path from `command -v uv` (macOS/Linux)
or `where uv` (Windows). Do not rely on the GUI inheriting your terminal PATH.

## Check the connection

1. Run `uv run desmos-mcp --help` from the repository. It should print CLI help.
2. Restart/reconnect the client; inspect its tool list for the five tools in the README.
3. Call `validate_formula` with `{"formula":"y = x^2"}`; expect `valid: true`.
4. Call `plot_math_function` with `{"formula":"sin(x)"}`; expect text metadata and native image content.
5. If the client cannot display images, open the saved PNG path on the server machine.

## Troubleshooting / 常见问题

| Symptom / 现象 | Resolution / 处理 |
| --- | --- |
| Command not found | Run `uv sync --locked`; use an absolute `uv` path in the client. |
| Server waits silently in the terminal | Normal stdio behavior; use an MCP client, not interactive typing. |
| Invalid configuration | Replace the old `desmos` block; verify JSON and supported settings in README. |
| `2x`, LaTeX or an implicit equation fails offline | Use `2*x`; send Desmos LaTeX to `create_interactive_graph`. |
| Calculation timeout | Simplify the formula, use `basic` analysis, or deliberately raise the configured timeout. |
| Interactive graph shows connection screen | Enter your own Desmos API key and allow access to `www.desmos.com`. |
| Key/network error | Check the key with Desmos and inspect browser console; the page allows retrying. |
| Local file cannot be opened by remote client | Transfer it from the server; local paths are not public share links. |

Sampling and elicitation are not required. Guidance is available through resources and prompts, so clients without
those optional callbacks still receive useful syntax errors and tool results.
无需客户端支持 LLM sampling 或 elicitation，基础绘图和错误指导即可使用。

# Tool examples / 工具示例

These are MCP tool arguments, not shell commands. 以下是 MCP 工具参数，不是终端命令。

## Offline graph

`plot_math_function`:

```json
{"formula":"y = sin(x)","x_range":[-6.283185307,6.283185307],"y_range":[-1.5,1.5]}
```

Ranges are numeric: convert `pi` to a number for range arguments. Formula text can contain `pi`.
坐标范围需要数字，公式文本可使用 `pi`。

`plot_multiple_functions`:

```json
{"formulas":["x^2","2*x+1"],"x_range":[-3,3],"y_range":[-3,10]}
```

The result includes a legend, structured metadata as text, and native `image/png` content.

## Symbolic analysis

`analyze_formula`:

```json
{"formula":"x^3-3*x","analysis_type":"detailed"}
```

Expect real domain, real range, derivative `3*x**2 - 3`, and stationary points `{-1, 1}`.
Use `abs(x)` with `critical_points` to see why a corner can matter even when it is not a stationary point.
Returned warnings explain incomplete differentiability or symbolic solving.

## Interactive sliders and curves

`create_interactive_graph`:

```json
{"expressions":["a=1","y=a x^2","x^2+y^2=9"],"title":"Explore a parabola and circle","language":"en","x_range":[-6,6],"y_range":[-4,8]}
```

Use `"language":"zh-CN"` for Chinese interface guidance.
For trigonometry, Desmos LaTeX in JSON is `"y=\\sin(x)"`; JSON needs two backslashes to encode one.
The offline syntax `sin(x)` and the interactive LaTeX syntax `\\sin(x)` should not be mixed automatically.

Open `path` in a browser, supply your key, then move the `a` slider or edit expressions.
“Save state JSON” downloads Desmos's opaque state; “Import state” reloads it. “Reset” restores the original graph.
“Export PNG” saves the current view. The original HTML is unchanged by browser edits.

## Guided prompts

`basic_graphing_assistant` arguments: `{"formula":"sin(x)"}`.

`advanced_math_analysis` arguments: `{"formula":"x^3-3*x","analysis_focus":"derivatives"}`.

The assistant should explain axes and assumptions, inspect warnings, and suggest a concrete next experiment.
For missing ranges, use [-10,10] unless the user's goal requires clarification.

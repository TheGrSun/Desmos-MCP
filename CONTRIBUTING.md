# Contributing

Install dependencies with `uv sync --locked`. Run `uv run pytest`, `uv run ruff check src tests`, and `uv build` before submitting changes.
Use Node.js 22+ to run the isolated controller tests with `node --test tests/interactive.test.cjs`.

- `server.py`: MCP contracts, errors, progress, resources, prompts and worker lifecycle.
- `formulas.py`: the offline syntax whitelist and mathematical input validation.
- `worker.py`: computation and headless plotting in disposable processes.
- `config.py`: configuration discovery, defaults and validation.
- `interactive.py` / `graph.html`: HTML serialization and the official Desmos browser integration.

Keep user expressions out of Python eval/exec. Do not add `print` to the MCP process's stdout; it carries protocol messages.
Worker stdout is an internal JSON channel. Do not embed API keys in generated artifacts.

Cover changed observable behavior: valid/invalid formula inputs, native image output, symbolic edge cases, timeouts,
CLI stdio communication and packaged template availability. Test rendered pages when changing the interactive UI.
Live Desmos tests require your own key and network; deterministic tests should not depend on the external SDK.

Keep both READMEs and the migration notes consistent when changing tool arguments, defaults or return types.
Do not invent REST endpoints or hand-edit Desmos's opaque saved state. Use the documented JavaScript API.

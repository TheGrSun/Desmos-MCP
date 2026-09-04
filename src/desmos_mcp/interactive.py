"""Generate a standalone page using the documented Desmos browser SDK."""

import json
from importlib.resources import files


def make_page(expressions: list[str], title: str, x_range: list[float], y_range: list[float], language: str) -> str:
    data = json.dumps(
        {"expressions": expressions, "title": title, "xRange": x_range, "yRange": y_range, "language": language},
        ensure_ascii=True,
    )
    # Do not let an expression or title terminate the inline script element.
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return files("desmos_mcp").joinpath("graph.html").read_text(encoding="utf-8").replace("__GRAPH_DATA__", data)

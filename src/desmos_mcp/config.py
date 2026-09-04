"""Validated configuration, resolved independently of the client's directory."""

import json
import os
import tempfile
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class Rendering(BaseModel):
    model_config = ConfigDict(extra="forbid")
    default_width: int = Field(default=900, ge=200, le=2400)
    default_height: int = Field(default=600, ge=200, le=1600)
    samples: int = Field(default=1600, ge=200, le=10000)
    save_files: bool = True


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rendering: Rendering = Field(default_factory=Rendering)
    output_dir: Path = Field(default_factory=lambda: Path(tempfile.gettempdir()) / "desmos-mcp")
    timeout_seconds: float = Field(default=20, ge=1, le=120)


def load_settings(config_path: str | None = None) -> Settings:
    """Explicit argument > DESMOS_MCP_CONFIG > ./config.json > defaults."""
    selected = config_path or os.environ.get("DESMOS_MCP_CONFIG")
    path = Path(selected).expanduser() if selected else Path.cwd() / "config.json"
    if selected or path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        settings = Settings.model_validate(data)
        if not settings.output_dir.is_absolute():
            settings.output_dir = path.resolve().parent / settings.output_dir
        return settings
    return Settings()

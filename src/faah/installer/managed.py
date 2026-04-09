"""Sync bundled shell assets into the managed config directory (~/.config/faah)."""

from __future__ import annotations

import os
import shutil
import stat
from importlib.resources import as_file, files
from pathlib import Path


def default_config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME", "").strip()
    if xdg:
        return Path(xdg) / "faah"
    return Path.home() / ".config" / "faah"


def sync_managed_config(dest: Path | None = None) -> Path:
    """Copy bundled data/* into dest (default ~/.config/faah). Returns dest."""
    root = dest or default_config_dir()
    root.mkdir(parents=True, exist_ok=True)
    data_trav = files("faah").joinpath("data")
    with as_file(data_trav) as data_path:
        data_path = Path(data_path)
        for name in ("assets", "scripts", "zsh", "bash", "fzf", "init"):
            src = data_path / name
            if not src.exists():
                continue
            dst = root / name
            if dst.exists():
                if dst.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                if dst.suffix == ".sh":
                    mode = dst.stat().st_mode
                    dst.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    play = root / "scripts" / "play-faah.sh"
    if play.is_file():
        mode = play.stat().st_mode
        play.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return root


def sound_path(managed_root: Path | None = None) -> Path:
    root = managed_root or default_config_dir()
    return root / "assets" / "sounds" / "fahhh.mp3"

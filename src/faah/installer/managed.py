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


def _looks_like_faah_source_repo(path: Path) -> bool:
    """True if path looks like a faah git checkout (not the managed user config dir)."""
    try:
        p = path.resolve(strict=False)
    except OSError:
        return False
    return (p / "pyproject.toml").is_file() and (p / "src" / "faah").is_dir()


def unsafe_managed_dest_reason(dest: Path) -> str | None:
    """If ``dest`` must not be used as the managed config root, return why; else None."""
    exp = dest.expanduser()
    try:
        resolved = exp.resolve(strict=False)
    except OSError:
        resolved = exp
    if _looks_like_faah_source_repo(resolved):
        return (
            "managed config path resolves to a directory that looks like the faah "
            "source repository (pyproject.toml and src/faah/). "
            "Use ~/.config/faah or set XDG_CONFIG_HOME so that "
            "$XDG_CONFIG_HOME/faah is outside your clone; remove any symlink from "
            "~/.config/faah to the repo. See README (Troubleshooting)."
        )
    return None


def sync_managed_config(dest: Path | None = None) -> Path:
    """Copy bundled data/* into dest (default ~/.config/faah). Returns dest."""
    root = (dest or default_config_dir()).expanduser()
    why = unsafe_managed_dest_reason(root)
    if why:
        raise ValueError(why)
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

"""Play notification sound using external players (mpv, ffplay, paplay, aplay)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console


def _which(cmd: str) -> str | None:
    return shutil.which(cmd)


def resolve_sound_path_for_play() -> Path:
    """Return path to the configured sound file, syncing managed config if missing."""
    from faah.installer.managed import default_config_dir, sound_path, sync_managed_config

    managed = default_config_dir()
    sp = sound_path(managed)
    if sp.is_file():
        return sp
    sync_managed_config()
    return sound_path(managed)


def play_faah_sound(*, err_console: Console | None = None) -> int:
    """Play the faah sound once (``faah play``). Returns shell exit code."""
    try:
        sp = resolve_sound_path_for_play()
    except ValueError as e:
        if err_console is not None:
            err_console.print(f"[red]{e}[/red]")
        else:
            print(str(e), file=sys.stderr)
        return 1
    return play_sound(sp, background=False)


def play_sound(sound_file: Path, *, background: bool = True) -> int:
    """Play sound file. Returns 0 on success, 1 on failure."""
    path = Path(sound_file)
    if not path.is_file():
        return 1
    p = str(path)
    # mpv: no window — force-window=no, --no-video, --vo=null (user mpv.conf can otherwise
    # still create a VO/window on some builds).
    for exe, args in (
        (
            "mpv",
            [
                "--no-terminal",
                "--really-quiet",
                "--force-window=no",
                "--no-video",
                "--vo=null",
                p,
            ],
        ),
        ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "quiet", p]),
        ("paplay", [p]),
        ("aplay", ["-q", p]),
    ):
        bin_path = _which(exe)
        if not bin_path:
            continue
        try:
            if background:
                subprocess.Popen(  # noqa: S603
                    [bin_path, *args],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                return 0
            subprocess.run(  # noqa: S603
                [bin_path, *args],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return 0
        except OSError:
            continue
    return 1

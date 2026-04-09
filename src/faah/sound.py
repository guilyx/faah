"""Play notification sound using external players (mpv, ffplay, paplay, aplay)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _which(cmd: str) -> str | None:
    return shutil.which(cmd)


def play_sound(sound_file: Path, *, background: bool = True) -> int:
    """Play sound file. Returns 0 on success, 1 on failure."""
    path = Path(sound_file)
    if not path.is_file():
        return 1
    p = str(path)
    for exe, args in (
        ("mpv", ["--no-terminal", "--really-quiet", p]),
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
                    [bin_path, *args[1:]],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                return 0
            subprocess.run(  # noqa: S603
                [bin_path, *args[1:]],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return 0
        except OSError:
            continue
    return 1

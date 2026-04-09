"""cmatrix-style falling F/A/H/! rain for terminals (green-on-black “hacker” look)."""

from __future__ import annotations

import os
import random
import shutil
import sys
import time
from dataclasses import dataclass
from typing import TextIO

_DISABLE_ENV = "FAHH_DISABLE_MATRIX"
_SEC_ENV = "FAHH_MATRIX_SEC"
_CLI_SEC_ENV = "FAHH_MATRIX_CLI_SEC"
_HOOK_SEC_ENV = "FAHH_MATRIX_HOOK_SEC"
_FPS_ENV = "FAHH_MATRIX_FPS"
_CHARS_ENV = "FAHH_MATRIX_CHARS"

# Snappy defaults (full effect was ~3s @ 18fps — felt sluggish on hooks).
_DEFAULT_SEC = 0.85
_DEFAULT_FPS = 26.0

# ANSI: dim green base, bright green, white head (cmatrix-ish)
_DIM = "\033[32m"
_MID = "\033[92m"
_HEAD = "\033[97m"
_RESET = "\033[0m"
_HIDE_CURSOR = "\033[?25l"
_SHOW_CURSOR = "\033[?25h"


def _env_falsey_disable(raw: str | None) -> bool:
    """True when FAHH_DISABLE_MATRIX disables effects."""
    if raw is None:
        return False
    r = raw.strip().lower()
    return r in ("1", "true", "yes", "on")


def matrix_effect_enabled() -> bool:
    """False when ``FAHH_DISABLE_MATRIX`` is set (e.g. ``faah install --no-matrix``)."""
    return not _env_falsey_disable(os.environ.get(_DISABLE_ENV))


def matrix_duration(default: float | None = None) -> float:
    d = _DEFAULT_SEC if default is None else default
    try:
        return max(0.25, min(60.0, float(os.environ.get(_SEC_ENV, str(d)).strip())))
    except ValueError:
        return d


def matrix_cli_duration() -> float:
    """Shorter default for ``faah`` typo path (usage exit 2)."""
    try:
        return max(0.2, min(30.0, float(os.environ.get(_CLI_SEC_ENV, "0.6").strip())))
    except ValueError:
        return 0.6


def matrix_hook_duration() -> float:
    """Default duration when shell hooks run ``faah terminal-matrix``."""
    try:
        return max(0.2, min(30.0, float(os.environ.get(_HOOK_SEC_ENV, "0.72").strip())))
    except ValueError:
        return 0.72


def matrix_fps() -> float:
    try:
        fps = float(os.environ.get(_FPS_ENV, str(int(_DEFAULT_FPS))).strip())
        return max(8.0, min(60.0, fps))
    except ValueError:
        return _DEFAULT_FPS


def matrix_charset() -> list[str]:
    s = (os.environ.get(_CHARS_ENV) or "FAH!").strip()
    return list(s) if s else ["F", "A", "H", "!"]


def _run_plain_flood(stream: TextIO, duration: float) -> None:
    """Non-TTY: fast scrolling lines (fewer lines/frame than before — was I/O heavy)."""
    rng = random.Random()
    chars = matrix_charset()
    cols = min(96, max(48, shutil.get_terminal_size(fallback=(80, 24)).columns))
    rows_per_frame = 4
    deadline = time.monotonic() + duration
    fps = matrix_fps()
    frame_dt = max(0.022, 1.0 / fps)
    while time.monotonic() < deadline:
        for _ in range(rows_per_frame):
            line = "".join(rng.choice(chars) for _ in range(cols))
            stream.write(f"{_DIM}{line}{_RESET}\n")
        stream.flush()
        time.sleep(frame_dt)


@dataclass
class _Stream:
    col: int
    y: float
    speed: float
    length: int


def run_fah_matrix(
    *,
    stream: TextIO | None = None,
    duration: float | None = None,
) -> None:
    """Green rain of F/A/H/! for ``duration`` seconds. Plain line flood if not a TTY."""
    stream = stream or sys.stderr
    if duration is None:
        dur = matrix_duration()
    else:
        dur = max(0.2, min(60.0, float(duration)))

    if not matrix_effect_enabled():
        return

    if not stream.isatty():
        _run_plain_flood(stream, dur)
        return

    w, h = shutil.get_terminal_size(fallback=(80, 24))
    w = max(20, min(200, w))
    h = max(8, min(100, h))

    chars = matrix_charset()
    rng = random.Random()
    fps = matrix_fps()
    frame_dt = 1.0 / fps
    max_streams = min(max(24, w + w // 2), 320)

    streams: list[_Stream] = []
    for _ in range(max(8, w // 4)):
        streams.append(
            _Stream(
                col=rng.randrange(w),
                y=rng.uniform(-h, 0.0),
                speed=rng.uniform(0.35, 1.35),
                length=rng.randint(5, min(22, h + 4)),
            )
        )

    def spawn() -> None:
        if len(streams) >= max_streams:
            return
        streams.append(
            _Stream(
                col=rng.randrange(w),
                y=rng.uniform(-h * 0.5, 0.0),
                speed=rng.uniform(0.35, 1.45),
                length=rng.randint(4, min(20, h + 4)),
            )
        )

    grid_char: list[list[str]] = [[" "] * w for _ in range(h)]
    grid_tier: list[list[int]] = [[9] * w for _ in range(h)]

    stream.write(_HIDE_CURSOR + _DIM)
    stream.flush()
    deadline = time.monotonic() + dur
    tick = 0

    try:
        while time.monotonic() < deadline:
            tick += 1
            for s in streams:
                s.y += s.speed

            for r in range(h):
                for c in range(w):
                    grid_char[r][c] = " "
                    grid_tier[r][c] = 9

            dead: list[_Stream] = []
            for s in streams:
                head = int(s.y)
                for t in range(s.length):
                    row = head - t
                    if 0 <= row < h:
                        tier = 0 if t == 0 else (1 if t <= s.length // 2 else 2)
                        ch = chars[(tick + row * 3 + s.col + t * 7) % len(chars)]
                        if tier < grid_tier[row][s.col]:
                            grid_tier[row][s.col] = tier
                            grid_char[row][s.col] = ch
                if head > h + s.length + 2:
                    dead.append(s)

            if dead:
                dead_ids = {id(s) for s in dead}
                streams = [s for s in streams if id(s) not in dead_ids]
                for _ in dead:
                    if rng.random() < 0.65:
                        spawn()

            if rng.random() < 0.12 and len(streams) < max(12, w):
                spawn()

            parts: list[str] = ["\033[2J\033[H", _DIM]
            for r in range(h):
                for c in range(w):
                    ch = grid_char[r][c]
                    if ch == " ":
                        parts.append(" ")
                    else:
                        tier = grid_tier[r][c]
                        if tier == 0:
                            parts.append(f"{_HEAD}{ch}{_DIM}")
                        elif tier == 1:
                            parts.append(f"{_MID}{ch}{_DIM}")
                        else:
                            parts.append(f"{_DIM}{ch}")
                if r < h - 1:
                    parts.append("\n")
            parts.append(_RESET)
            stream.write("".join(parts))
            stream.flush()
            time.sleep(frame_dt)
    finally:
        stream.write(_SHOW_CURSOR + "\033[2J\033[H" + _RESET)
        stream.flush()

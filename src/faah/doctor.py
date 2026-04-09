"""Dependency checks (audio players, fzf, sound file)."""

from __future__ import annotations

import shutil
import subprocess


def have_cmd(name: str) -> bool:
    return shutil.which(name) is not None


def check_audio() -> dict[str, tuple[bool, str | None]]:
    out: dict[str, tuple[bool, str | None]] = {}
    for c in ("mpv", "ffplay", "paplay", "aplay"):
        p = shutil.which(c)
        out[c] = (p is not None, p)
    return out


def check_fzf() -> tuple[bool, str | None, str | None]:
    p = shutil.which("fzf")
    if not p:
        return False, None, None
    ver: str | None = None
    try:
        r = subprocess.run(  # noqa: S603
            [p, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if r.stdout:
            ver = r.stdout.strip().splitlines()[0]
    except OSError:
        pass
    return True, p, ver


def apt_fix_commands(*, want_fzf: bool) -> list[str]:
    """Suggested apt commands for Debian/Ubuntu."""
    cmds = ["sudo apt-get update"]
    pkgs: list[str] = []
    if not any(have_cmd(x) for x in ("mpv", "ffplay", "paplay", "aplay")):
        pkgs.append("mpv")
    if not have_cmd("paplay"):
        pkgs.append("pulseaudio-utils")
    if not have_cmd("aplay"):
        pkgs.append("alsa-utils")
    if want_fzf and not have_cmd("fzf"):
        pkgs.append("fzf")
    pkgs = list(dict.fromkeys(pkgs))
    if pkgs:
        cmds.append(f"sudo apt-get install -y {' '.join(pkgs)}")
    return cmds


def run_apt_fix(*, want_fzf: bool) -> int:
    """Run apt-get update && apt-get install (requires apt). Returns process return code."""
    if not shutil.which("apt-get"):
        return 127
    pkgs: list[str] = []
    if not any(have_cmd(x) for x in ("mpv", "ffplay", "paplay", "aplay")):
        pkgs.append("mpv")
    if not have_cmd("paplay"):
        pkgs.append("pulseaudio-utils")
    if not have_cmd("aplay"):
        pkgs.append("alsa-utils")
    if want_fzf and not have_cmd("fzf"):
        pkgs.append("fzf")
    pkgs = list(dict.fromkeys(pkgs))
    if not pkgs:
        return 0
    r1 = subprocess.run(["sudo", "apt-get", "update"], check=False)  # noqa: S603,S607
    if r1.returncode != 0:
        return r1.returncode
    r2 = subprocess.run(["sudo", "apt-get", "install", "-y", *pkgs], check=False)  # noqa: S603,S607
    return r2.returncode

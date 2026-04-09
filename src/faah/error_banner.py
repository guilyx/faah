"""Optional ASCII banner when the CLI exits with a usage error (exit code 2)."""

from __future__ import annotations

import os
import sys

_ENV = "FAHH_FAH_BANNER"

# Stylized terminal banner (ASCII box + long “A” scream).
FAH_BANNER = r"""
 ____________________________________________________________
/                                                            \
|  FAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH!  |
\____________________________________________________________/
""".strip(
    "\n"
)


def fah_error_banner_enabled() -> bool:
    """True unless ``FAHH_FAH_BANNER`` disables it (0/false/no/off)."""
    raw = os.environ.get(_ENV, "1").strip().lower()
    if raw in ("", "1", "true", "yes", "on"):
        return True
    if raw in ("0", "false", "no", "off"):
        return False
    return True


def print_fah_banner(*, to_stderr: bool = True) -> None:
    """Print the FAAAAAAAAAAAAH banner."""
    out = sys.stderr if to_stderr else sys.stdout
    print(FAH_BANNER, file=out)


def maybe_print_fah_banner_on_usage_error(exit_code: int | None) -> None:
    """If ``exit_code == 2`` (Click/Typer misuse), print banner when enabled."""
    if exit_code != 2:
        return
    if not fah_error_banner_enabled():
        return
    print_fah_banner(to_stderr=True)

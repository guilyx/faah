"""Usage-error exit handling: matrix effect on Typer/Click misuse (exit code 2)."""

from __future__ import annotations

import sys


def coerce_cli_exit_code(code: object | None) -> int | None:
    """Normalize ``sys.exit`` / ``SystemExit.code`` to an int, or None if unknown."""
    if code is None:
        return 0
    if isinstance(code, bool):
        return int(code)
    if isinstance(code, int):
        return code
    try:
        return int(code)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def maybe_matrix_on_usage_error(exit_code: int | None) -> None:
    """On usage error (exit 2), run terminal-matrix unless disabled."""
    if exit_code != 2:
        return
    from faah.terminal_matrix import matrix_cli_duration, matrix_effect_enabled, run_fah_matrix

    if not matrix_effect_enabled():
        return
    run_fah_matrix(stream=sys.stderr, duration=matrix_cli_duration())

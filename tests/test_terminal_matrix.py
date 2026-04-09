"""cmatrix-style terminal-matrix animation."""

import io
from pathlib import Path

import pytest
from typer.testing import CliRunner

from faah.cli import app
from faah.terminal_matrix import (
    matrix_charset,
    matrix_duration,
    matrix_effect_enabled,
    matrix_fps,
    run_fah_matrix,
)

runner = CliRunner()


def test_matrix_effect_enabled_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FAHH_DISABLE_MATRIX", raising=False)
    assert matrix_effect_enabled() is True


def test_matrix_effect_disabled_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAHH_DISABLE_MATRIX", "1")
    assert matrix_effect_enabled() is False


def test_matrix_duration_and_fps(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAHH_MATRIX_SEC", "5")
    assert matrix_duration() == 5.0
    monkeypatch.setenv("FAHH_MATRIX_FPS", "30")
    assert matrix_fps() == 30.0


def test_matrix_charset_custom(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAHH_MATRIX_CHARS", "X")
    assert matrix_charset() == ["X"]


def test_run_fah_matrix_non_tty_plain_flood() -> None:
    buf = io.StringIO()
    buf.isatty = lambda: False  # type: ignore[method-assign,assignment]
    run_fah_matrix(stream=buf, duration=0.15)
    out = buf.getvalue()
    assert any(c in out for c in ("F", "A", "H", "!"))


def test_run_fah_matrix_disabled_no_output() -> None:
    import os

    buf = io.StringIO()
    buf.isatty = lambda: False  # type: ignore[method-assign,assignment]
    old = os.environ.get("FAHH_DISABLE_MATRIX")
    os.environ["FAHH_DISABLE_MATRIX"] = "1"
    try:
        run_fah_matrix(stream=buf, duration=1.0)
        assert buf.getvalue() == ""
    finally:
        if old is None:
            del os.environ["FAHH_DISABLE_MATRIX"]
        else:
            os.environ["FAHH_DISABLE_MATRIX"] = old


def test_terminal_matrix_cli_invocation() -> None:
    r = runner.invoke(app, ["terminal-matrix", "-s", "0.01"])
    assert r.exit_code == 0


def test_run_fah_matrix_tty_no_crash_on_dead_streams(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression: dead streams used frozenset(unhashable _Stream) and crashed."""

    class FakeTTY:
        def __init__(self) -> None:
            self.parts: list[str] = []

        def write(self, s: str) -> None:
            self.parts.append(s)

        def flush(self) -> None:
            pass

        def isatty(self) -> bool:
            return True

    out = FakeTTY()
    monkeypatch.setattr(
        "shutil.get_terminal_size",
        lambda *_a, **_k: (50, 16),
    )
    monkeypatch.setattr("time.sleep", lambda _s: None)
    times: list[float] = [0.0, 100.0]

    def mono() -> float:
        return times.pop(0) if times else 999.0

    monkeypatch.setattr("time.monotonic", mono)
    run_fah_matrix(stream=out, duration=5.0)
    joined = "".join(out.parts)
    assert "\033" in joined or len(joined) > 0


def test_usage_error_with_matrix_short(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import os
    import subprocess
    import sys

    monkeypatch.setenv("FAHH_MATRIX_SEC", "0.05")
    root = Path(__file__).resolve().parents[1] / "src"
    env = {**os.environ, "PYTHONPATH": str(root)}
    proc = subprocess.run(
        [sys.executable, "-m", "faah", "typo"],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
        env=env,
    )
    assert proc.returncode == 2
    combined = proc.stderr + proc.stdout
    assert any(x in combined for x in ("F", "A", "H", "\033"))

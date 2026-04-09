"""CLI usage-error hook (exit 2) → terminal-matrix."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from faah.cli_exit import coerce_cli_exit_code, maybe_matrix_on_usage_error


def test_help_subcommand() -> None:
    from typer.testing import CliRunner

    from faah.cli import app

    runner = CliRunner()
    r = runner.invoke(app, ["help"])
    assert r.exit_code == 0
    assert "Usage:" in r.stdout
    assert "install" in r.stdout


def test_unknown_command_exit_2() -> None:
    from typer.testing import CliRunner

    from faah.cli import app

    runner = CliRunner()
    r = runner.invoke(app, ["not-a-real-command"])
    assert r.exit_code == 2


def test_coerce_cli_exit_code() -> None:
    assert coerce_cli_exit_code(None) == 0
    assert coerce_cli_exit_code(2) == 2
    assert coerce_cli_exit_code("2") == 2
    assert coerce_cli_exit_code("nope") is None


def test_maybe_matrix_on_2_plain_flood(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAHH_MATRIX_SEC", "0.05")
    maybe_matrix_on_usage_error(2)
    err = capsys.readouterr().err
    assert len(err) > 20
    assert any(c in err for c in ("F", "A", "H", "!"))


def test_maybe_matrix_skips_non_2(capsys: pytest.CaptureFixture[str]) -> None:
    maybe_matrix_on_usage_error(1)
    assert capsys.readouterr().err == ""


def test_maybe_matrix_skips_when_disabled(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAHH_DISABLE_MATRIX", "1")
    maybe_matrix_on_usage_error(2)
    assert capsys.readouterr().err == ""


def _src_on_path() -> dict[str, str]:
    root = Path(__file__).resolve().parents[1] / "src"
    return {**os.environ, "PYTHONPATH": str(root)}


def test_cli_usage_error_runs_matrix_or_flood(tmp_path: Path) -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "faah", "typo"],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
        env=_src_on_path(),
    )
    assert proc.returncode == 2
    combined = proc.stderr + proc.stdout
    assert any(x in combined for x in ("F", "A", "H", "\033"))


def test_cli_usage_error_respects_disable(tmp_path: Path) -> None:
    env = _src_on_path()
    env["FAHH_DISABLE_MATRIX"] = "1"
    proc = subprocess.run(
        [sys.executable, "-m", "faah", "typo"],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
        env=env,
    )
    assert proc.returncode == 2
    # Typer usage line is short; disabled → no multi-KB FAH flood.
    assert len(proc.stderr + proc.stdout) < 4000

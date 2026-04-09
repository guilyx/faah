"""CLI help subcommand and FAAAAAAAAAAAAH usage-error banner."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from faah.cli import app
from faah.error_banner import fah_error_banner_enabled, maybe_print_fah_banner_on_usage_error

runner = CliRunner()


def test_help_subcommand() -> None:
    r = runner.invoke(app, ["help"])
    assert r.exit_code == 0
    assert "Usage:" in r.stdout
    assert "install" in r.stdout


def test_unknown_command_exit_2() -> None:
    r = runner.invoke(app, ["not-a-real-command"])
    assert r.exit_code == 2


def test_fah_banner_enabled_default() -> None:
    assert fah_error_banner_enabled() is True


def test_fah_banner_disabled_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAHH_FAH_BANNER", "0")
    assert fah_error_banner_enabled() is False


def test_maybe_print_banner_on_2(capsys: pytest.CaptureFixture[str]) -> None:
    maybe_print_fah_banner_on_usage_error(2)
    err = capsys.readouterr().err
    assert "FAAAAAAAA" in err


def test_maybe_print_skips_when_disabled(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAHH_FAH_BANNER", "0")
    maybe_print_fah_banner_on_usage_error(2)
    assert capsys.readouterr().err == ""


def test_maybe_print_skips_non_2(capsys: pytest.CaptureFixture[str]) -> None:
    maybe_print_fah_banner_on_usage_error(1)
    assert capsys.readouterr().err == ""


def _src_on_path() -> dict[str, str]:
    root = Path(__file__).resolve().parents[1] / "src"
    return {**os.environ, "PYTHONPATH": str(root)}


def test_cli_usage_error_prints_banner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FAHH_FAH_BANNER", raising=False)
    monkeypatch.chdir(tmp_path)
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
    assert "FAAAAAAAA" in combined


def test_cli_usage_error_banner_off(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    env = _src_on_path()
    env["FAHH_FAH_BANNER"] = "0"
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
    assert "FAAAAAAAA" not in combined

"""CLI smoke tests."""

from typer.testing import CliRunner

from faah import __version__
from faah.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    out = result.stdout + result.stderr
    assert __version__ in out


def test_doctor() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0

"""faah CLI: install, uninstall, doctor, play."""

from __future__ import annotations

import os
import shlex
import shutil
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from faah import __version__
from faah.cli_exit import coerce_cli_exit_code, maybe_matrix_on_usage_error
from faah.doctor import apt_fix_commands, check_audio, check_fzf, have_cmd, run_apt_fix
from faah.installer.editor import install_editor_helpers, remove_editor_artifacts
from faah.installer.managed import (
    default_config_dir,
    sound_path,
    sync_managed_config,
    unsafe_managed_dest_reason,
)
from faah.installer.rc import ensure_block, remove_block_file
from faah.sound import play_faah_sound

app = typer.Typer(
    name="faah",
    help="Terminal sound on selected shell exit codes; manage zsh/bash/fzf hooks.",
    add_completion=False,
    invoke_without_command=True,
)
console = Console(stderr=True)


def _bootstrap_line(shell: str, managed: Path) -> str:
    # Single line, no shell function named `faah` — that shadowed the real `faah` CLI on PATH.
    # Guard with [[ -r ]] so a missing ~/.config/faah does not break every new shell.
    if shell == "zsh":
        p = managed / "init" / "faah.zsh"
        q = shlex.quote(str(p))
        return f"[[ -r {q} ]] && source {q}\n"
    if shell == "bash":
        p = managed / "init" / "faah.bash"
        q = shlex.quote(str(p))
        return f"[[ -r {q} ]] && source {q}\n"
    raise ValueError(shell)


def _fzf_export_line() -> str:
    return "export FAHH_ENABLE_FZF=1\n"


def _migrate_remove_legacy_rc_blocks(rc_path: Path) -> None:
    """Drop old banner-env / matrix-env markers from earlier faah versions."""
    for bid in ("banner-env", "matrix-env"):
        remove_block_file(rc_path, bid, backup=True)


def _sync_matrix_disable_block(rc_path: Path, want_matrix: bool) -> None:
    """matrix-disable exports FAHH_DISABLE_MATRIX=1 when user opts out of matrix effects."""
    bid = "matrix-disable"
    if want_matrix:
        r = remove_block_file(rc_path, bid, backup=True)
        if r.changed:
            console.print(f"[dim]Removed[/dim] {bid} from {rc_path} (matrix enabled)")
    else:
        body = "export FAHH_DISABLE_MATRIX=1\n"
        r = ensure_block(rc_path, bid, body, backup=True)
        if r.changed:
            console.print(f"[green]Added[/green] FAHH_DISABLE_MATRIX=1 to {rc_path}")


@app.command("help", add_help_option=False)
def help_command(ctx: typer.Context) -> None:
    """Show usage for faah — prefer this over `faah --help`."""
    parent = ctx.parent
    if parent is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)
    typer.echo(parent.get_help())


@app.callback()
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Print version and exit."),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit(0)
    if ctx.invoked_subcommand is None:
        install_command(
            yes=False,
            zsh=None,
            bash=None,
            fzf=None,
            cursor=None,
            vscode=None,
            matrix=None,
        )


@app.command("install")
def install_command(
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Non-interactive: enable all options without prompts.",
    ),
    zsh: bool | None = typer.Option(None, "--zsh/--no-zsh", help="Install zsh hook."),
    bash: bool | None = typer.Option(None, "--bash/--no-bash", help="Install bash hook."),
    fzf: bool | None = typer.Option(
        None,
        "--fzf/--no-fzf",
        help="Enable fzf integration env in rc.",
    ),
    cursor: bool | None = typer.Option(
        None,
        "--cursor/--no-cursor",
        help="Copy Cursor helper fragments to ~/.config/faah/install/cursor/.",
    ),
    vscode: bool | None = typer.Option(
        None,
        "--vscode/--no-vscode",
        help="Copy VS Code helper fragments to ~/.config/faah/install/vscode/.",
    ),
    matrix: bool | None = typer.Option(
        None,
        "--matrix/--no-matrix",
        help="Terminal-matrix on faah mistakes and shell hooks (default: on). "
        "When off, adds export FAHH_DISABLE_MATRIX=1 to installed shells.",
    ),
) -> None:
    """Sync managed config and add shell rc blocks (interactive by default)."""
    if not sys.stdin.isatty() and not yes:
        msg = "[yellow]No TTY; use [bold]faah install --yes[/bold] for non-interactive.[/yellow]"
        console.print(msg)
        raise typer.Exit(1)

    try:
        managed = sync_managed_config()
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1) from None
    console.print(f"[green]Synced[/green] bundled files to [bold]{managed}[/bold]")

    def pick(name: str, current: bool | None, default: bool) -> bool:
        if yes:
            return default if current is None else current
        if current is not None:
            return current
        return Confirm.ask(name, default=default)

    do_zsh = pick("Install zsh hook (~/.zshrc)?", zsh, True)
    do_bash = pick("Install bash hook (~/.bashrc)?", bash, False)
    do_fzf = pick("Enable fzf integration (FAHH_ENABLE_FZF)?", fzf, False)
    do_cursor = pick("Copy Cursor helper files under install/cursor?", cursor, False)
    do_vscode = pick("Copy VS Code helper files under install/vscode?", vscode, False)
    if do_zsh or do_bash:
        want_matrix = pick(
            "Enable terminal-matrix (FAH rain) on shell hooks and faah CLI mistakes?",
            matrix,
            True,
        )
    else:
        want_matrix = True if matrix is None else matrix

    home = Path.home()
    if do_zsh:
        body = _bootstrap_line("zsh", managed)
        r = ensure_block(home / ".zshrc", "zsh", body)
        if r.changed:
            console.print(f"[green]Added[/green] faah block to {r.path}")
        else:
            console.print(f"[dim]Skip[/dim] zsh block already present in {r.path}")
        if do_fzf:
            r2 = ensure_block(home / ".zshrc", "fzf-zsh", _fzf_export_line())
            if r2.changed:
                console.print("[green]Added[/green] fzf env to ~/.zshrc")
            else:
                console.print("[dim]Skip[/dim] fzf-zsh block already present")
        _migrate_remove_legacy_rc_blocks(home / ".zshrc")
        _sync_matrix_disable_block(home / ".zshrc", want_matrix)

    if do_bash:
        body = _bootstrap_line("bash", managed)
        r = ensure_block(home / ".bashrc", "bash", body)
        if r.changed:
            console.print(f"[green]Added[/green] faah block to {r.path}")
        else:
            console.print(f"[dim]Skip[/dim] bash block already present in {r.path}")
        if do_fzf:
            r2 = ensure_block(home / ".bashrc", "fzf-bash", _fzf_export_line())
            if r2.changed:
                console.print("[green]Added[/green] fzf env to ~/.bashrc")
            else:
                console.print("[dim]Skip[/dim] fzf-bash block already present")
        _migrate_remove_legacy_rc_blocks(home / ".bashrc")
        _sync_matrix_disable_block(home / ".bashrc", want_matrix)

    if do_cursor or do_vscode:
        paths = install_editor_helpers(managed, cursor=bool(do_cursor), vscode=bool(do_vscode))
        for p in paths:
            console.print(f"[green]Copied[/green] editor helpers to [bold]{p}[/bold]")

    console.print(
        "\n[bold green]Done.[/bold green] Open a new shell or "
        "[bold]source ~/.zshrc[/bold] / [bold]~/.bashrc[/bold]."
    )


@app.command("uninstall")
def uninstall_command(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Remove faah blocks from rc files and install/ artifacts."""
    if not yes and sys.stdin.isatty():
        if not Confirm.ask(
            "Remove faah blocks from ~/.zshrc and ~/.bashrc and install/ helpers?",
            default=False,
        ):
            raise typer.Exit(0)
    elif not yes:
        console.print("Use [bold]faah uninstall --yes[/bold] when not a TTY.")
        raise typer.Exit(1)

    home = Path.home()
    managed = default_config_dir()
    for path, bid in (
        (home / ".zshrc", "fzf-zsh"),
        (home / ".zshrc", "banner-env"),
        (home / ".zshrc", "matrix-env"),
        (home / ".zshrc", "matrix-disable"),
        (home / ".zshrc", "zsh"),
        (home / ".bashrc", "fzf-bash"),
        (home / ".bashrc", "banner-env"),
        (home / ".bashrc", "matrix-env"),
        (home / ".bashrc", "matrix-disable"),
        (home / ".bashrc", "bash"),
    ):
        remove_block_file(path, bid, backup=True)
    remove_editor_artifacts(managed)
    console.print("[green]Uninstall steps completed.[/green]")


@app.command("doctor")
def doctor_command(
    fix: bool = typer.Option(False, "--fix", help="Try apt install on Debian/Ubuntu (sudo)."),
    want_fzf: bool = typer.Option(
        True,
        "--fzf/--no-fzf",
        help="With --fix, also install fzf if missing.",
    ),
) -> None:
    """Show audio/fzf/sound status; optional apt fix."""
    table = Table(title="faah doctor")
    table.add_column("Check", style="cyan")
    table.add_column("Status")

    md = default_config_dir()
    bad = unsafe_managed_dest_reason(md)
    table.add_row("managed config", f"[red]unsafe[/red] {md}" if bad else f"ok {md}")

    for name, (ok, loc) in check_audio().items():
        table.add_row(name, f"{'ok' if ok else 'missing'} {loc or ''}".strip())

    ok, loc, ver = check_fzf()
    table.add_row("fzf", f"{'ok' if ok else 'missing'} {loc or ''} {ver or ''}".strip())

    sp = sound_path()
    table.add_row("sound file", "ok " + str(sp) if sp.is_file() else f"missing {sp}")

    from faah.terminal_matrix import (
        matrix_cli_duration,
        matrix_duration,
        matrix_effect_enabled,
        matrix_hook_duration,
    )

    _md = matrix_effect_enabled()
    _mv = os.environ.get("FAHH_DISABLE_MATRIX", "(unset)")
    _faah_bin = shutil.which("faah")
    _timing = (
        f"{'on' if _md else 'off'} (FAHH_DISABLE_MATRIX={_mv}); "
        f"typo≈{matrix_cli_duration():.1f}s hook≈{matrix_hook_duration():.1f}s "
        f"run≈{matrix_duration():.1f}s"
    )
    table.add_row("terminal-matrix", _timing)
    _path_hint = "[yellow]missing[/yellow] (try: python3 -m faah)"
    table.add_row("`faah` on PATH", _faah_bin or _path_hint)

    console.print(table)
    if bad:
        console.print(f"\n[yellow]{bad}[/yellow]")

    if fix:
        if not shutil.which("apt-get"):
            console.print("[red]No apt-get; install mpv/ffplay manually.[/red]")
            raise typer.Exit(1)
        code = run_apt_fix(want_fzf=want_fzf)
        raise typer.Exit(code)

    if not any(have_cmd(x) for x in ("mpv", "ffplay", "paplay", "aplay")):
        console.print("\n[yellow]Hint:[/yellow] install a player, e.g.:")
        for line in apt_fix_commands(want_fzf=want_fzf):
            console.print(f"  {line}")


@app.command("play")
def play_command() -> None:
    """Play the configured sound once (test audio)."""
    raise typer.Exit(play_faah_sound(err_console=console))


@app.command("terminal-matrix")
def terminal_matrix_command(
    seconds: float | None = typer.Option(
        None,
        "--seconds",
        "-s",
        help="Seconds to run (default: FAHH_MATRIX_SEC or ~0.85).",
    ),
) -> None:
    """cmatrix-style F/A/H/! rain on stderr (plain flood if not a TTY)."""
    from faah.terminal_matrix import matrix_duration, run_fah_matrix

    dur = matrix_duration() if seconds is None else max(0.4, min(60.0, seconds))
    run_fah_matrix(stream=sys.stderr, duration=dur)
    raise typer.Exit(0)


def main() -> None:
    # Click handles usage errors with sys.exit(2); wrapping sys.exit is reliable across
    # environments (some runners only observe the builtin, not a caught SystemExit).
    real_exit = sys.exit

    def _exit_hook(code: object | None = None) -> None:
        maybe_matrix_on_usage_error(coerce_cli_exit_code(code))
        real_exit(code)

    sys.exit = _exit_hook  # type: ignore[method-assign,assignment]
    try:
        app()
    finally:
        sys.exit = real_exit  # type: ignore[method-assign,assignment]

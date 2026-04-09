# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [2.1.0] - 2026-04-09

### Added

- **`faah help`** subcommand for usage (documented as preferred over **`faah --help`**).
- **Terminal-matrix only** (no ASCII banner): **`faah terminal-matrix`** and automatic runs on **`faah`** usage mistakes (exit **2**) and zsh/bash hooks. Full-screen rain on a TTY; **plain scrolling F/A/H/! flood** when stderr is not a TTY so output always appears.
- **`FAHH_DISABLE_MATRIX`**: opt out via **`faah install --no-matrix`** (**`matrix-disable`** rc block) or env.
- **`faah install`**: single prompt / **`--matrix` / `--no-matrix`** (default **on**); removes legacy **`banner-env`** / **`matrix-env`** blocks from older versions.
- **`FAHH_REPLACE_NOT_FOUND`**: zsh **`command_not_found_handler`** / bash **`command_not_found_handle`** — matrix + sound without the default **`command not found`** line (bash **4+**).
- **`faah doctor`**: reports **`FAHH_DISABLE_MATRIX`** / terminal-matrix status.

### Removed

- Static / typewriter **FAAAAH** banner module and **`FAHH_FAH_BANNER`**, **`FAHH_SHELL_FAH_BANNER`**, animation env vars.

### Changed

- **Terminal-matrix performance**: lower default durations (**~0.85** s manual, **~0.6** s CLI typo, **~0.72** s shell hooks via **`FAHH_MATRIX_*_SEC`**), higher default **FPS**, lighter **plain flood** (fewer lines per frame). Shell hooks pass **`-s`** and fall back to **`python3 -m faah`** only when **`import faah`** succeeds (avoids **`No module named faah`** from bare **`/usr/bin/python3`**). Optional **`FAHH_PYTHON`**. **`faah doctor`** shows timings and **`faah`** on **`PATH`**.

### Fixed

- **`terminal-matrix`**: removing finished rain streams no longer uses **`frozenset`** on mutable **`_Stream`** dataclass instances (unhashable → **`TypeError`**).
- Usage-error hook: wrap **`sys.exit`** around **`app()`** so Click/Typer’s **`sys.exit(2)`** path runs **terminal-matrix** reliably. **`coerce_cli_exit_code`** lives in **`cli_exit.py`**.
- **`faah play` / `play_sound`**: player argv accidentally used **`args[1:]`**, dropping **`--no-terminal`** for **mpv**, **`-nodisp`** for **ffplay**, and the sound path for **paplay**. Fixed to pass full arg lists; **mpv** also gets **`--vo=null`** (with **`play-faah.sh`**) so a GUI window should not open even with aggressive **`mpv.conf`**.

## [2.0.1] - 2026-04-09

### Fixed

- **mpv** / **`play-faah.sh`**: pass **`--force-window=no`** and **`--no-video`** so **`faah play`** and shell hooks do not open a video window when playing MP3 on some desktops.

## [2.0.0] - 2026-04-09

Stable **2.x** release: Python/Typer CLI, managed **`~/.config/faah`**, PyPI packaging, installer hardening, and shared **`faah play`** implementation. Supersedes pre-release **`2.0.0rc1`** (same feature set plus GA polish).

### Fixed

- Packaging integration tests: set **`XDG_CONFIG_HOME`** alongside **`HOME`** so installs sync under the temp directory when CI defines `XDG_CONFIG_HOME`.
- Shell rc bootstrap line uses **`[[ -r ... ]] && source ...`** so a missing **`~/.config/faah`** does not error on every shell startup.
- Rc bootstrap **no longer defines a shell function named `faah`**, which had **shadowed the real `faah` CLI** so commands like **`faah install`** never reached Python. **`faah install`** now **replaces** an existing faah block when the bootstrap line changes, so one run can fix old rc files (use **`command faah install --yes`** once if the shadowing function is still present).
- **Managed config path**: refuse to sync into a directory that **looks like the faah source tree** (`pyproject.toml` + **`src/faah/`**), avoiding accidental writes into a git clone (e.g. **`~/.config/faah` → symlink** to the repo, or bad **`XDG_CONFIG_HOME`**). **`faah doctor`** reports **unsafe** when this applies. README documents **`XDG_CONFIG_HOME`** and cleanup when **`XDG_CONFIG_HOME` is unset** but files still landed in the clone.

### Added

- **`faah.sound.play_faah_sound`**: shared implementation for **`faah play`** (no separate **`faah.play`** module or **`faah-play`** script).
- Integration tests that **build a wheel**, **install into an isolated venv**, and run **`faah --version`**, **`doctor`**, **`install --yes`**, and **`play`** with a temporary `HOME`.
- **Python package `faah` on PyPI**: `pyproject.toml`, `src/faah/` CLI (`faah`, `faah install|uninstall|doctor|play`), bundled shell assets under `src/faah/data/`, managed install into `~/.config/faah/`.
- **uv** workflow: `uv.lock`; run tests with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest`, lint with `uv run ruff check`, build with `uv run python -m build`.
- **GitHub Actions**: Python CI (`ruff`, `pytest`, `build`) + optional shell checks; **Publish to PyPI** workflow (Trusted Publishing / OIDC).

### Changed

- **README**: Troubleshooting clarifies that the rc bootstrap guard applies only to the **main** `init/faah.{zsh,bash}` file; errors from **inside** managed scripts are not suppressed.
- **Install/update path**: primary flow is `pip install faah` / `uv tool install faah` then `faah install`.
- **Repository layout**: removed duplicate top-level `assets/`, `bash/`, `zsh/`, `fzf/`, `init/`, `scripts/`, `cursor/`, `vscode/`, legacy `.setup/`, and root `VERSION`. Bundled shell assets live only under **`src/faah/data/`**; version only in **`src/faah/__init__.py`**.
- **Dev workflow**: no `Makefile`; use the `uv run` commands documented in `README.md` and `CONTRIBUTING.md`.
- **PyPI classifiers**: **Development Status** set to **Production/Stable** for the published package.

## [1.0.0] - 2026-04-09

### Fixed

- `zsh/faah.zsh` and `bash/faah.bash`: removed `unset` of the play-script path so `precmd` / `PROMPT_COMMAND` can still invoke `play-faah.sh` (previously hooks always skipped audio).

### Changed

- Default sound trigger is **exit 127** (command not found) and **126** (not executable), not every non-zero exit. Use **`FAHH_PLAY_EXIT_CODES=all`** for the previous “any failure” behavior.
- Merged `check-deps.sh` into `install.sh` (`check_deps`, `--check-deps`, `--skip-deps` / `FAHH_SKIP_DEPS`).
- `install.sh --help`: compact CLI help (no README dump); clearer errors and shorter default hint output.
- `install.sh` output uses ANSI colors (bold/dim/green/yellow/magenta/cyan) when connected to a TTY; honors **`NO_COLOR`** and **`FORCE_COLOR`**. Plain text for **`print_snippet`** / rc file appends (no escapes in `source` lines).
- `install.sh`: added `--uninstall` (removes marked rc blocks, artifacts, and repo symlink when safe) and `--yes` for non-interactive confirmation skipping.
- `install.sh`: can install missing dependencies on Ubuntu/Debian via `apt` (`--install-deps`) and offers to do so interactively when missing tools are detected.
- Installer now prefers a **single-line bootstrap** in `~/.zshrc` / `~/.bashrc` that sources `~/.config/faah/init/faah.{zsh,bash}`, keeping global config changes minimal.

### Added

- `.setup/update.sh` to update the repo (`git pull --ff-only`) and rerun the dependency report.
- Repository layout: `assets/sounds/`, `scripts/play-faah.sh`, `zsh/faah.zsh`, `bash/faah.bash`, `fzf/` (defaults + official `fzf --zsh` / `fzf --bash` integration), `cursor/` and `vscode/` docs and optional settings fragments.
- Interactive shell hooks: play `fahhh.mp3` on selected exit codes (default **127/126**) via zsh `precmd` and bash `PROMPT_COMMAND`, with `FAHH_DISABLED`, `FAHH_PLAY_EXIT_CODES`, `FAHH_SOUND` / `FAHH_ROOT`.
- `FAHH_PLAY_ON_NONZERO` opt-in to play sound on any non-zero exit without changing `FAHH_PLAY_EXIT_CODES`.
- `vscode/extensions.json` with optional editor recommendations (shell/formatting); not required for faah.
- `.setup/install.sh` for `chmod`, **dependency report**, optional `~/.config/faah` symlink (`FAHH_CONFIG_LINK`), snippet printing, and **`--interactive`** wizard (zsh/bash/fzf, Cursor/VS Code helper copies under `FAHH_INSTALL_DEST`, idempotent marked blocks in rc files); `.setup/README.md`.
- `.gitignore`, `CONTRIBUTING.md`, and `LICENSE` (MIT with `SPDX-License-Identifier: MIT`); README layout rows and License section; contributing guide links licensing to MIT.

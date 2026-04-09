# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

- Packaging integration tests: set **`XDG_CONFIG_HOME`** alongside **`HOME`** so installs sync under the temp directory when CI defines `XDG_CONFIG_HOME`.

### Added

- Integration tests that **build a wheel**, **install into an isolated venv**, and run **`faah --version`**, **`doctor`**, **`install --yes`**, and **`play`** with a temporary `HOME`.
- **Python package `faah` on PyPI**: `pyproject.toml`, `src/faah/` CLI (`faah`, `faah install|uninstall|doctor|play`), bundled shell assets under `src/faah/data/`, managed install into `~/.config/faah/`.
- **uv** workflow: `uv.lock`; run tests with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest`, lint with `uv run ruff check`, build with `uv run python -m build`.
- **GitHub Actions**: Python CI (`ruff`, `pytest`, `build`) + optional shell checks; **Publish to PyPI** workflow (Trusted Publishing / OIDC).

### Changed

- **Install/update path**: primary flow is `pip install faah` / `uv tool install faah` then `faah install`.
- **Repository layout**: removed duplicate top-level `assets/`, `bash/`, `zsh/`, `fzf/`, `init/`, `scripts/`, `cursor/`, `vscode/`, legacy `.setup/`, and root `VERSION`. Bundled shell assets live only under **`src/faah/data/`**; version only in **`src/faah/__init__.py`**.
- **Dev workflow**: no `Makefile`; use the `uv run` commands documented in `README.md` and `CONTRIBUTING.md`.

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

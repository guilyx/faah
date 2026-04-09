# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

- `zsh/faah.zsh` and `bash/faah.bash`: removed `unset` of the play-script path so `precmd` / `PROMPT_COMMAND` can still invoke `play-faah.sh` (previously hooks always skipped audio).

### Changed

- Merged `check-deps.sh` into `install.sh` (`check_deps`, `--check-deps`, `--skip-deps` / `FAHH_SKIP_DEPS`).
- `install.sh --help`: compact CLI help (no README dump); clearer errors and shorter default hint output.
- `install.sh` output uses ANSI colors (bold/dim/green/yellow/magenta/cyan) when connected to a TTY; honors **`NO_COLOR`** and **`FORCE_COLOR`**. Plain text for **`print_snippet`** / rc file appends (no escapes in `source` lines).
- `install.sh`: added `--uninstall` (removes marked rc blocks, artifacts, and repo symlink when safe) and `--yes` for non-interactive confirmation skipping.
- Installer now prefers a **single-line bootstrap** in `~/.zshrc` / `~/.bashrc` that sources `~/.config/faah/init/faah.{zsh,bash}`, keeping global config changes minimal.

### Added

- Repository layout: `assets/sounds/`, `scripts/play-faah.sh`, `zsh/faah.zsh`, `bash/faah.bash`, `fzf/` (defaults + official `fzf --zsh` / `fzf --bash` integration), `cursor/` and `vscode/` docs and optional settings fragments.
- Interactive shell hooks: play `fahhh.mp3` after non-zero exit via zsh `precmd` and bash `PROMPT_COMMAND`, with `FAHH_DISABLED`, `FAHH_IGNORE_EXIT` (default `130`), and `FAHH_SOUND` / `FAHH_ROOT`.
- `vscode/extensions.json` with optional editor recommendations (shell/formatting); not required for faah.
- `.setup/install.sh` for `chmod`, **dependency report**, optional `~/.config/faah` symlink (`FAHH_CONFIG_LINK`), snippet printing, and **`--interactive`** wizard (zsh/bash/fzf, Cursor/VS Code helper copies under `FAHH_INSTALL_DEST`, idempotent marked blocks in rc files); `.setup/README.md`.
- `.gitignore`, `CONTRIBUTING.md`, and `LICENSE` (MIT with `SPDX-License-Identifier: MIT`); README layout rows and License section; contributing guide links licensing to MIT.

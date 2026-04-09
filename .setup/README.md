# Setup scripts

Run from the **repository root** (paths resolve from the script location). **CLI reference:** `./.setup/install.sh --help`

| Script | Purpose |
|--------|---------|
| [install.sh](install.sh) | `chmod +x` the player, **dependency report** (audio, fzf, sound file), optional symlink, printed snippets, or **interactive** setup |

Dependency checking is part of every normal `install.sh` run (use **`--skip-deps`** to suppress, or **`FAHH_SKIP_DEPS=1`**).

## Quick start

**Recommended (interactive):** choose zsh, bash, optional fzf, Cursor/VS Code helper copies, and optional config symlink. Dependencies are listed first.

```bash
cd /path/to/faah
./.setup/install.sh --interactive
```

**Non-interactive:** fixes permissions, prints the dependency report, then prints `source` lines to paste manually:

```bash
./.setup/install.sh
```

**Dependencies only** (same report as above, no `chmod`):

```bash
./.setup/install.sh --check-deps
```

## install.sh options

| Flag | Effect |
|------|--------|
| `--interactive` / `-i` | Prompt for zsh/bash/fzf, Cursor & VS Code helper files, and optional `~/.config/faah` symlink (requires a TTY). Runs dependency report after `chmod`. |
| `--uninstall` | Remove `faah` marked blocks from `~/.zshrc` / `~/.bashrc`, remove `FAHH_INSTALL_DEST` artifacts, and remove `FAHH_CONFIG_LINK` symlink if it points at this repo |
| `--yes` | For `--uninstall`: skip the confirmation prompt |
| `--check-deps` | Print dependency report only (mpv/ffplay/paplay/aplay, fzf, default sound path), then exit |
| `--skip-deps` | Do not print the dependency report (also respects env `FAHH_SKIP_DEPS`) |
| `--symlink-config` | `ln -sfn <repo> ~/.config/faah` (override target with `FAHH_CONFIG_LINK`) |
| `--print-snippet zsh` | Print a line to add to `~/.zshrc` |
| `--print-snippet bash` | Print a line to add to `~/.bashrc` |
| `--print-snippet fzf-zsh` | Print optional fzf line for zsh |
| `--print-snippet fzf-bash` | Print optional fzf line for bash |

### Interactive mode details

- **Shell:** appends marked blocks to `~/.zshrc` / `~/.bashrc` (creates the file if missing). Each run is **idempotent**: existing `faah` blocks are skipped. A **timestamped backup** (`.faahbak.*`) is made before the first change to an existing file.
- **Cursor / VS Code:** copies `settings.json.fragment`, `README.md`, and (VS Code only) `extensions.json` into **`~/.config/faah/install/cursor/`** or **`.../vscode/`** (override root with **`FAHH_INSTALL_DEST`**). You still **merge** editor JSON into your User settings by hand (see each `README.md` in those folders).
- **Not supported:** auto-merging into Cursor/VS Code `settings.json` (too risky without your editor’s merge rules).

Environment:

- **`FAHH_CONFIG_LINK`**: symlink path (default `~/.config/faah`).
- **`FAHH_INSTALL_DEST`**: where interactive mode drops Cursor/VS Code copies (default `~/.config/faah/install`).
- **`FAHH_SKIP_DEPS`**: set to non-empty to skip printing the dependency section (same as `--skip-deps`).
- **`NO_COLOR`** / **`FORCE_COLOR`**: control ANSI styling for `install.sh` (see `--help`).

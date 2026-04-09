# faah

Small dotfiles-style snippets that play a short sound when the last command hits **“command not found” (127)** or **“not executable” (126)** by default — not for normal failing commands (`grep` miss, `false`, etc.). Optional **fzf** defaults and notes for **Cursor** / **VS Code** integrated terminals.

## Layout

| Path | Role |
|------|------|
| [assets/sounds/fahhh.mp3](assets/sounds/fahhh.mp3) | Default sound file |
| [scripts/play-faah.sh](scripts/play-faah.sh) | Plays the sound (mpv → ffplay → paplay → aplay) |
| [zsh/faah.zsh](zsh/faah.zsh) | zsh `precmd` hook |
| [bash/faah.bash](bash/faah.bash) | bash `PROMPT_COMMAND` hook |
| [fzf/](fzf/) | `FZF_DEFAULT_OPTS` + `eval "$(fzf --zsh)"` or `eval "$(fzf --bash)"` |
| [cursor/](cursor/) | Cursor terminal / settings notes |
| [vscode/](vscode/) | VS Code terminal / settings notes + optional `extensions.json` |
| [.setup/](.setup/) | Install and dependency checks ([.setup/README.md](.setup/README.md)) |
| [.setup/update.sh](.setup/update.sh) | Update this repo via `git pull` + rerun dependency report |
| [VERSION](VERSION) | Project version (SemVer) |
| [RELEASING.md](RELEASING.md) | How to cut a release + tag |
| [LICENSE](LICENSE) | MIT (scripts and documentation) |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |

## Install

**CLI:** `./.setup/install.sh --help` lists all options.

1. Clone or copy this repo (example: `~/dev/faah`).
2. **Interactive (recommended):** run **`./.setup/install.sh --interactive`** and choose zsh and/or bash, optional fzf, optional copies for Cursor/VS Code under `~/.config/faah/install/`, and an optional symlink **`~/.config/faah`** → this repo. Requires a terminal (TTY). See [.setup/README.md](.setup/README.md) for behavior and env vars.
3. **Manual:** run **`./.setup/install.sh`** — it **`chmod +x`** the player, prints a **dependency report** (audio tools, `fzf`, sound file), then prints `source` lines. Use **`./.setup/install.sh --check-deps`** for the report only.
   - If you want the installer to also install missing dependencies on Ubuntu/Debian, run: **`./.setup/install.sh --install-deps`** (uses `apt`, prompts for `sudo`).
4. Optional CLI: **`./.setup/install.sh --symlink-config`** creates **`~/.config/faah`** → this repo (override with **`FAHH_CONFIG_LINK`**). Then you can `source ~/.config/faah/zsh/faah.zsh` if you prefer a stable path.
5. If you did not use `--interactive`, add to **`~/.zshrc`** (interactive shells only):

   ```zsh
   faah(){ source ~/.config/faah/init/faah.zsh; }; faah
   ```

   Or **`~/.bashrc`**:

   ```bash
   faah(){ source ~/.config/faah/init/faah.bash; }; faah
   ```

6. Optional: set `FAHH_ROOT` if the repo lives somewhere non-standard:

   ```sh
   export FAHH_ROOT="$HOME/dev/faah"
   ```

   If unset, it is inferred from the path of the file you source.

7. Optional fzf: set `export FAHH_ENABLE_FZF=1` before the `faah(){ ... }; faah` line (or enable via `--interactive`).

## Environment variables

| Variable | Meaning |
|----------|---------|
| `FAHH_ROOT` | Root of this repo (auto-detected if unset) |
| `FAHH_SOUND` | Path to sound file (default: `$FAHH_ROOT/assets/sounds/fahhh.mp3`) |
| `FAHH_DISABLED` | If non-empty, hooks do nothing |
| `FAHH_PLAY_ON_NONZERO` | If set and `FAHH_PLAY_EXIT_CODES` is unset: play on any non-zero exit (includes “normal failing commands”) |
| `FAHH_PLAY_EXIT_CODES` | Space-separated exit codes that **do** trigger sound (default: `127 126`). Set to `all` to play on any non-zero exit (old behavior). |
| `FAHH_IGNORE_EXIT` | When `FAHH_PLAY_EXIT_CODES=all`: codes that **never** trigger sound (default: `130` Ctrl-C). Ignored in default 127/126 mode. |
| `FAHH_INSTALL_DEST` | Base dir for interactive installer copies of Cursor/VS Code fragments (default: `~/.config/faah/install`) |
| `FAHH_CONFIG_LINK` | Symlink path for `./.setup/install.sh --symlink-config` (default: `~/.config/faah`) |
| `FAHH_SKIP_DEPS` | If set, `./.setup/install.sh` skips printing the dependency section (same as `--skip-deps`) |
| `NO_COLOR` | If set, install output has no ANSI colors ([no-color.org](https://no-color.org/)) |
| `FORCE_COLOR` | If set, install uses colors even when stdout/stderr is not a TTY |

## Uninstall

Run:

```bash
./.setup/install.sh --uninstall
```

This removes the `faah` marked blocks from `~/.zshrc` / `~/.bashrc`, deletes `~/.config/faah/install/*` (or whatever `FAHH_INSTALL_DEST` points to), and removes the `~/.config/faah` symlink **only if** it points to this repository.

## Update

From the repo root, run:

```bash
./.setup/update.sh
```

## Troubleshooting

- **No sound**: Install **mpv** or **ffplay** (ffmpeg) for reliable MP3 playback; `paplay`/`aplay` may not decode MP3 on all systems.
- **Sound in editors**: The integrated terminal must run an interactive shell that sources `faah.zsh` / `faah.bash`. See [cursor/README.md](cursor/README.md) and [vscode/README.md](vscode/README.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project’s **shell scripts, setup scripts, and documentation** are released under the [MIT License](LICENSE) (`SPDX-License-Identifier: MIT`).

The bundled sound under `assets/sounds/` may be subject to separate rights; replace it with your own file if you need different terms.

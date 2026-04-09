# fzf

This repo sets conservative defaults and loads the **official** fzf shell integration (key bindings and `**` fuzzy completion) only when `fzf` is on `PATH`.

## Usage

From `~/.zshrc` (after `faah` if you use it):

```zsh
source /path/to/faah/fzf/fzf.zsh
```

From `~/.bashrc`:

```bash
source /path/to/faah/fzf/fzf.bash
```

Override defaults by exporting `FZF_DEFAULT_OPTS` **before** sourcing these files.

## Installing fzf

- **Package manager** (e.g. `apt install fzf`, `dnf install fzf`): ensure the binary is on `PATH`.
- **Git install** (see [junegunn/fzf](https://github.com/junegunn/fzf)): run the install script or add the `bin` directory to `PATH`. Newer fzf releases can generate shell integration via `eval "$(fzf --zsh)"` / `eval "$(fzf --bash)"`. Older distro builds (e.g. fzf 0.29) do not support these flags; this repo falls back to sourcing `~/.fzf.zsh` / `~/.fzf.bash` or common `/usr/share/...` paths.

## Relation to faah

Non-zero exit codes from fzf (e.g. cancel with no selection) return to the shell; your zsh `precmd` / bash `PROMPT_COMMAND` (from `zsh/faah.zsh`, `bash/faah.bash`) can play the sound. Use `FAHH_IGNORE_EXIT` if you want to suppress sound for specific exit codes.

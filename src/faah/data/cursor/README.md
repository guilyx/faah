# Cursor

Faah plays the sound from your **shell** when the last command exits non-zero. Cursor’s integrated terminal uses your normal shell (`zsh` / `bash`), so you only need this repo sourced from `~/.zshrc` or `~/.bashrc` as in the root [README](../README.md).

## Terminal profile

- If you put faah/fzf in `~/.zshrc`, ensure the integrated terminal starts an **interactive** shell (default on Linux/macOS).
- If you rely on login-only files (`~/.zprofile`), either move the `source` lines to `~/.zshrc` or configure the terminal profile to run a **login** shell (e.g. `zsh -l`).

## Optional settings fragment

Merge [settings.json.fragment](settings.json.fragment) into **Cursor → Settings → Open User Settings (JSON)** if you want explicit Linux terminal defaults. Adjust profile names to match your machine.

## Extensions

Cursor is VS Code–compatible; optional extension IDs are listed in [vscode/extensions.json](../vscode/extensions.json). Install manually or copy that file into a workspace `.vscode/` folder if you want “recommended extensions” prompts in a project.

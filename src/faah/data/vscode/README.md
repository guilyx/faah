# Visual Studio Code

Faah plays the sound from your **shell** when the last command exits non-zero. The integrated terminal uses your normal shell, so configure faah in `~/.zshrc` / `~/.bashrc` (see root [README](../README.md)); no separate “error sound” API is required.

## Terminal profile

- Prefer sourcing `zsh/faah.zsh` or `bash/faah.bash` from `~/.zshrc` / `~/.bashrc` so **non-login** interactive shells in VS Code load them.
- If you only configure faah in `~/.zprofile` / `~/.bash_profile`, set the integrated terminal to use a **login** shell or duplicate the `source` lines into `~/.zshrc` / `~/.bashrc`.

## Optional settings fragment

Merge [settings.json.fragment](settings.json.fragment) into **File → Preferences → Settings → Open User Settings (JSON)** if you want explicit Linux terminal defaults.

## Recommended extensions

Copy [extensions.json](extensions.json) to a project’s `.vscode/extensions.json` to get workspace recommendations, or install the listed extensions manually. None are required for faah audio.

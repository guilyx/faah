# Contributing

Thanks for improving faah. This repo is small shell snippets and docs; keep changes focused and easy to review.

By contributing, you agree your contributions are licensed under the same terms as the project: **[MIT](LICENSE)** (`SPDX-License-Identifier: MIT`).

## How to contribute

1. **Fork or branch** from `main` (or the default branch).
2. **Change the smallest surface** needed: one concern per pull request when practical.
3. **Test interactively** after editing hooks:
   - zsh: `zsh -ic 'source ./zsh/faah.zsh; false; echo exit=$?'`
   - bash: `bash -ic 'source ./bash/faah.bash; false; echo exit=$?'`
4. **Run setup checks** from the repo root (use `./.setup/install.sh --interactive` only when you intend to modify your shell rc or install helper copies):

   ```bash
   ./.setup/install.sh
   ```

5. **Update [CHANGELOG.md](CHANGELOG.md)** under `[Unreleased]` with a short note under Added/Changed/Fixed as appropriate.

## Style

- **Shell**: POSIX where reasonable; zsh-specific code only in `zsh/`. Prefer `[[` in bash/zsh. Quote expansions. Avoid echoing secrets.
- **Docs**: Clear, imperative install steps; mention env vars in [README.md](README.md) when behavior changes.
- **Do not** edit generated or local-only paths in examples to match only one machine—use placeholders like `~/dev/faah` or `$HOME/.config/faah`.

## What we will not merge without discussion

- Auto-editing `~/.zshrc` / `~/.bashrc` without explicit user action (install scripts may print snippets only).
- Large unrelated refactors or new dependencies for the core hooks.

## Code of conduct

Be respectful and assume good intent. For serious issues, use your platform’s reporting tools.

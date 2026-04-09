# fzf defaults and key bindings (zsh). Source after interactive check; requires fzf on PATH.
# See fzf/README.md for install options.

[[ -o interactive ]] || return 0

if [[ -z ${FZF_DEFAULT_OPTS:-} ]]; then
  export FZF_DEFAULT_OPTS="--height 40% --layout=reverse --border --info=inline --prompt='  '"
fi

if command -v fzf >/dev/null 2>&1; then
  if fzf --help 2>&1 | command grep -q -- '--zsh'; then
    eval "$(fzf --zsh)"
  else
    # Compatibility for older fzf versions (e.g. 0.29) that don't support `--zsh`.
    # Try user install first, then common distro locations.
    local p
    for p in \
      "${HOME}/.fzf.zsh" \
      "/usr/share/fzf/key-bindings.zsh" \
      "/usr/share/fzf/completion.zsh" \
      "/usr/share/doc/fzf/examples/key-bindings.zsh" \
      "/usr/share/doc/fzf/examples/completion.zsh"; do
      [[ -r "$p" ]] && source "$p"
    done
  fi
fi

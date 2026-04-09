# fzf defaults and key bindings (bash). Source after interactive check; requires fzf on PATH.
# See fzf/README.md for install options.

[[ $- == *i* ]] || return 0

if [[ -z ${FZF_DEFAULT_OPTS:-} ]]; then
  export FZF_DEFAULT_OPTS="--height 40% --layout=reverse --border --info=inline --prompt='  '"
fi

if command -v fzf >/dev/null 2>&1; then
  if fzf --help 2>&1 | command grep -q -- '--bash'; then
    eval "$(fzf --bash)"
  else
    # Compatibility for older fzf versions that don't support `--bash`.
    # Try user install first, then common distro locations.
    for p in \
      "${HOME}/.fzf.bash" \
      "/usr/share/fzf/key-bindings.bash" \
      "/usr/share/fzf/completion.bash" \
      "/usr/share/doc/fzf/examples/key-bindings.bash" \
      "/usr/share/doc/fzf/examples/completion.bash"; do
      # shellcheck disable=SC1090,SC1091
      [[ -r "$p" ]] && source "$p"
    done
  fi
fi

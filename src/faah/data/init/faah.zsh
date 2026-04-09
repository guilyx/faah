# faah bootstrap (zsh)
#
# Intended usage in ~/.zshrc (inside # >> faah:zsh … # << faah:zsh), single line:
#   [[ -r ~/.config/faah/init/faah.zsh ]] && source ~/.config/faah/init/faah.zsh

[[ -o interactive ]] || return 0

FAHH_ROOT=${FAHH_ROOT:-${0:A:h:h}}
export FAHH_ROOT

source "${FAHH_ROOT}/zsh/faah.zsh"

# Optional: fzf integration if installed/enabled by the user.
[[ -n ${FAHH_ENABLE_FZF:-} ]] && source "${FAHH_ROOT}/fzf/fzf.zsh"


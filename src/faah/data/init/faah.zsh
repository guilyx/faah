# faah bootstrap (zsh)
#
# Intended usage in ~/.zshrc (single command):
#   faah(){ source ~/.config/faah/init/faah.zsh; }; faah

[[ -o interactive ]] || return 0

FAHH_ROOT=${FAHH_ROOT:-${0:A:h:h}}
export FAHH_ROOT

source "${FAHH_ROOT}/zsh/faah.zsh"

# Optional: fzf integration if installed/enabled by the user.
[[ -n ${FAHH_ENABLE_FZF:-} ]] && source "${FAHH_ROOT}/fzf/fzf.zsh"


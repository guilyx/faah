# faah bootstrap (bash)
#
# Intended usage in ~/.bashrc (single command):
#   faah(){ source ~/.config/faah/init/faah.bash; }; faah

[[ $- == *i* ]] || return 0

if [[ -z ${FAHH_ROOT:-} ]]; then
  FAHH_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
export FAHH_ROOT

source "${FAHH_ROOT}/bash/faah.bash"

# Optional: fzf integration if installed/enabled by the user.
[[ -n ${FAHH_ENABLE_FZF:-} ]] && source "${FAHH_ROOT}/fzf/fzf.bash"


# faah bootstrap (bash)
#
# Intended usage in ~/.bashrc (inside # >> faah:bash … # << faah:bash), single line:
#   [[ -r ~/.config/faah/init/faah.bash ]] && source ~/.config/faah/init/faah.bash

[[ $- == *i* ]] || return 0

if [[ -z ${FAHH_ROOT:-} ]]; then
  FAHH_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
export FAHH_ROOT

# shellcheck source=../bash/faah.bash
# shellcheck disable=SC1091
source "${FAHH_ROOT}/bash/faah.bash"

# Optional: fzf integration if installed/enabled by the user.
# shellcheck source=../fzf/fzf.bash
# shellcheck disable=SC1091
[[ -n ${FAHH_ENABLE_FZF:-} ]] && source "${FAHH_ROOT}/fzf/fzf.bash"


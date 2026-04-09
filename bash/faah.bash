# faah: play sound on non-zero exit (interactive bash). Source from ~/.bashrc after [[ $- == *i* ]].
# Env: FAHH_ROOT, FAHH_DISABLED, FAHH_IGNORE_EXIT (space-separated codes, default: 130), FAHH_SOUND

[[ $- == *i* ]] || return 0

if [[ -z ${FAHH_ROOT:-} ]]; then
  FAHH_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
export FAHH_ROOT

# Keep path for PROMPT_COMMAND (do not unset — hooks run later and need this).
_FAAH_PLAY="${FAHH_ROOT}/scripts/play-faah.sh"
[[ -x "$_FAAH_PLAY" ]] || _FAAH_PLAY=

faah_prompt() {
  local ec=$?
  [[ -n ${FAHH_DISABLED:-} ]] && return 0
  [[ -z $_FAAH_PLAY ]] && return 0

  local _faah_ignore=${FAHH_IGNORE_EXIT:-130}
  local _tok
  IFS=' ' read -r -a _faah_codes <<< "$_faah_ignore"
  for _tok in "${_faah_codes[@]}"; do
    [[ "$ec" -eq "$_tok" ]] && return 0
  done

  "$_FAAH_PLAY" &>/dev/null
}

if [[ ":${PROMPT_COMMAND:-}:" != *:faah_prompt:* ]]; then
  PROMPT_COMMAND="faah_prompt${PROMPT_COMMAND:+;$PROMPT_COMMAND}"
fi

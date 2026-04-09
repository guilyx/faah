# faah: optional sound on selected exit codes (interactive bash).
# Env: FAHH_ROOT, FAHH_DISABLED, FAHH_SOUND, FAHH_PLAY_ON_NONZERO,
#      FAHH_PLAY_EXIT_CODES, FAHH_IGNORE_EXIT (only when mode is "all")

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

  local pec
  if [[ -n ${FAHH_PLAY_EXIT_CODES:-} ]]; then
    pec=${FAHH_PLAY_EXIT_CODES}
  elif [[ -n ${FAHH_PLAY_ON_NONZERO:-} ]]; then
    pec=all
  else
    pec='127 126'
  fi
  if [[ "$pec" == all ]]; then
    local _faah_ignore=${FAHH_IGNORE_EXIT:-130}
    local _tok
    IFS=' ' read -r -a _faah_codes <<< "$_faah_ignore"
    for _tok in "${_faah_codes[@]}"; do
      [[ "$ec" -eq "$_tok" ]] && return 0
    done
    [[ "$ec" -eq 0 ]] && return 0
  else
    local _c _match=0
    IFS=' ' read -r -a _faah_play_codes <<< "$pec"
    for _c in "${_faah_play_codes[@]}"; do
      [[ "$ec" -eq "$_c" ]] && _match=1 && break
    done
    [[ "$_match" -eq 1 ]] || return 0
  fi

  "$_FAAH_PLAY" &>/dev/null
}

if [[ ":${PROMPT_COMMAND:-}:" != *:faah_prompt:* ]]; then
  PROMPT_COMMAND="faah_prompt${PROMPT_COMMAND:+;$PROMPT_COMMAND}"
fi

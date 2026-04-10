# faah: optional sound on selected exit codes (interactive zsh).
# Env: FAHH_ROOT, FAHH_DISABLED, FAHH_SOUND, FAHH_PLAY_ON_NONZERO,
#      FAHH_PLAY_EXIT_CODES, FAHH_IGNORE_EXIT (only when mode is "all"),
#      FAHH_REPLACE_NOT_FOUND (1/true: zsh command_not_found_handler — no default msg),
#      FAHH_DISABLE_MATRIX (1/true: skip terminal-matrix visuals)
#      FAHH_MATRIX_HOOK_SEC (duration for hook-invoked matrix; default 1.44)
#      FAHH_PYTHON (override for python3 -m faah fallback when faah is not on PATH)

[[ -o interactive ]] || return 0

if [[ -z ${FAHH_ROOT:-} ]]; then
  FAHH_ROOT="${${(%):-%x}:A:h:h}"
fi
export FAHH_ROOT

_FAAH_PLAY="${FAHH_ROOT}/scripts/play-faah.sh"
[[ -x "$_FAAH_PLAY" ]] || _FAAH_PLAY=

_faah_truthy() {
  [[ -z "$1" ]] && return 1
  local r="${(L)1}"
  [[ "$r" == "0" || "$r" == "false" || "$r" == "no" || "$r" == "off" ]] && return 1
  return 0
}

_faah_matrix_disabled() {
  _faah_truthy "${FAHH_DISABLE_MATRIX:-}"
}

_faah_run_matrix() {
  _faah_matrix_disabled && return 0
  local sec="${FAHH_MATRIX_HOOK_SEC:-1.44}"
  local py="${FAHH_PYTHON:-python3}"
  if command -v faah >/dev/null 2>&1; then
    command faah terminal-matrix -s "$sec" 2>&2
    return 0
  fi
  # Only if this interpreter has faah installed (avoid "No module named faah" noise).
  if command -v "$py" >/dev/null 2>&1 && command "$py" -c "import faah" >/dev/null 2>&1; then
    command "$py" -m faah terminal-matrix -s "$sec" 2>&2
  fi
}

_faah_replace_not_found_wanted() {
  _faah_truthy "${FAHH_REPLACE_NOT_FOUND:-}"
}

if _faah_replace_not_found_wanted; then
  command_not_found_handler() {
    [[ -n ${FAHH_DISABLED:-} ]] && return 127
    _faah_run_matrix
    [[ -n $_FAAH_PLAY ]] && "$_FAAH_PLAY" &>/dev/null
    return 127
  }
fi

faah_precmd() {
  local ec=$?
  [[ -n ${FAHH_DISABLED:-} ]] && return 0

  if [[ "$ec" -eq 127 ]] && _faah_replace_not_found_wanted; then
    return 0
  fi

  local pec
  if [[ -n ${FAHH_PLAY_EXIT_CODES:-} ]]; then
    pec=${FAHH_PLAY_EXIT_CODES}
  elif [[ -n ${FAHH_PLAY_ON_NONZERO:-} ]]; then
    pec=all
  else
    pec='127 126'
  fi
  if [[ "$pec" == all ]]; then
    local code
    for code in ${=FAHH_IGNORE_EXIT:-130}; do
      [[ "$ec" -eq "$code" ]] && return 0
    done
    [[ "$ec" -eq 0 ]] && return 0
  else
    local c match=0
    for c in ${=pec}; do
      [[ "$ec" -eq "$c" ]] && match=1 && break
    done
    [[ "$match" -eq 1 ]] || return 0
  fi

  _faah_run_matrix

  [[ -z $_FAAH_PLAY ]] && return 0
  "$_FAAH_PLAY" &>/dev/null
}

precmd_functions=(${precmd_functions:#faah_precmd})
precmd_functions+=(faah_precmd)

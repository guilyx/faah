# faah: optional sound on selected exit codes (interactive zsh).
# Env: FAHH_ROOT, FAHH_DISABLED, FAHH_SOUND, FAHH_PLAY_ON_NONZERO,
#      FAHH_PLAY_EXIT_CODES, FAHH_IGNORE_EXIT (only when mode is "all")

[[ -o interactive ]] || return 0

if [[ -z ${FAHH_ROOT:-} ]]; then
  FAHH_ROOT="${${(%):-%x}:A:h:h}"
fi
export FAHH_ROOT

# Keep path for precmd (do not unset — hooks run later and need this).
_FAAH_PLAY="${FAHH_ROOT}/scripts/play-faah.sh"
[[ -x "$_FAAH_PLAY" ]] || _FAAH_PLAY=

faah_precmd() {
  local ec=$?
  [[ -n ${FAHH_DISABLED:-} ]] && return 0
  [[ -z $_FAAH_PLAY ]] && return 0

  # Default: only "command not found" (127) and "not executable" (126), like POSIX shells.
  # Set FAHH_PLAY_EXIT_CODES=all to play on any non-zero exit (except FAHH_IGNORE_EXIT, default 130).
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

  "$_FAAH_PLAY" &>/dev/null
}

precmd_functions=(${precmd_functions:#faah_precmd})
precmd_functions+=(faah_precmd)

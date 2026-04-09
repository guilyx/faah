# faah: play sound on non-zero exit (interactive zsh). Source from ~/.zshrc after [[ $- == *i* ]].
# Env: FAHH_ROOT, FAHH_DISABLED, FAHH_IGNORE_EXIT (space-separated codes, default: 130), FAHH_SOUND

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

  local code
  for code in ${=FAHH_IGNORE_EXIT:-130}; do
    [[ "$ec" -eq "$code" ]] && return 0
  done

  "$_FAAH_PLAY" &>/dev/null
}

precmd_functions=(${precmd_functions:#faah_precmd})
precmd_functions+=(faah_precmd)

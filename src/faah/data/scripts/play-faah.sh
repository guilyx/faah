#!/usr/bin/env bash
# Play the faah notification sound (async). Used by zsh/bash hooks.
set -euo pipefail

_script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
_repo_root=$(cd "$_script_dir/.." && pwd)
_sound=${FAHH_SOUND:-"$_repo_root/assets/sounds/fahhh.mp3"}

if [[ ! -f "$_sound" ]]; then
  printf 'faah: sound file not found: %s\n' "$_sound" >&2
  exit 1
fi

_play() {
  if command -v mpv >/dev/null 2>&1; then
    exec mpv --no-terminal --really-quiet --force-window=no --no-video "$_sound"
  fi
  if command -v ffplay >/dev/null 2>&1; then
    exec ffplay -nodisp -autoexit -loglevel quiet "$_sound"
  fi
  if command -v paplay >/dev/null 2>&1; then
    exec paplay "$_sound" 2>/dev/null
  fi
  if command -v aplay >/dev/null 2>&1; then
    exec aplay -q "$_sound" 2>/dev/null
  fi
  printf 'faah: no player found (mpv, ffplay, paplay, aplay)\n' >&2
  exit 1
}

_play &
exit 0

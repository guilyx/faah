#!/usr/bin/env bash
# Install helper: permissions, optional ~/.config/faah symlink, snippet hints,
# and --interactive wizard (zsh, bash, fzf, Cursor, VS Code helpers).
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PLAY="${ROOT}/scripts/play-faah.sh"
LINK_TARGET="${FAHH_CONFIG_LINK:-${HOME}/.config/faah}"
INSTALL_DEST="${FAHH_INSTALL_DEST:-${XDG_CONFIG_HOME:-$HOME/.config}/faah/install}"

# ANSI styling: respects NO_COLOR; FORCE_COLOR=1 enables even when not a TTY.
_faah_init_style() {
  B= D= R= G= Y= C= M= K= Z=
  BE= DE= RE= YE= ZE=
  [[ -n "${NO_COLOR:-}" ]] && return
  local co=0 ce=0
  [[ -n "${FORCE_COLOR:-}" || -t 1 ]] && co=1
  [[ -n "${FORCE_COLOR:-}" || -t 2 ]] && ce=1
  if [[ "$co" -eq 1 ]]; then
    B=$'\033[1m'
    D=$'\033[2m'
    R=$'\033[31m'
    G=$'\033[32m'
    Y=$'\033[33m'
    C=$'\033[36m'
    M=$'\033[35m'
    K=$'\033[90m'
    Z=$'\033[0m'
  fi
  if [[ "$ce" -eq 1 ]]; then
    BE=$'\033[1m'
    DE=$'\033[2m'
    RE=$'\033[31m'
    YE=$'\033[33m'
    ZE=$'\033[0m'
  fi
}

usage() {
  _faah_init_style
  local me
  me=$(basename "$0")
  printf '\n'
  printf '%bfaah install%b\n\n' "$B" "$Z"
  printf '%bUsage:%b\n' "$B" "$Z"
  printf '  %s%b%s%b [options]\n\n' "$D" "$Z" "$me" "$Z"

  printf '%bOptions:%b\n' "$B" "$Z"
  printf '  %b-h, --help%b              %bShow this help and exit%b\n' "$C" "$Z" "$D" "$Z"
  printf '  %b-i, --interactive%b       %bInteractive setup (shell rc, fzf, editor copies, symlink)%b\n' "$C" "$Z" "$D" "$Z"
  printf '  %b    --uninstall%b         %bRemove installed blocks/artifacts (see below)%b\n' "$C" "$Z" "$D" "$Z"
  printf '  %b    --yes%b               %bAssume yes for uninstall confirmation prompts%b\n' "$C" "$Z" "$D" "$Z"
  printf '  %b    --check-deps%b        %bPrint dependency report only, then exit (no chmod)%b\n' "$C" "$Z" "$D" "$Z"
  printf '  %b    --install-deps%b      %bInstall missing deps via system package manager (Ubuntu/Debian: apt)%b\n' "$C" "$Z" "$D" "$Z"
  printf '  %b    --skip-deps%b         %bSkip the dependency report (also env FAHH_SKIP_DEPS)%b\n' "$C" "$Z" "$D" "$Z"
  printf '  %b    --symlink-config%b    %bCreate symlink: ~/.config/faah -> repository (see FAHH_CONFIG_LINK)%b\n' "$C" "$Z" "$D" "$Z"
  printf '  %b    --print-snippet K%b   %bPrint one source line; K is zsh | bash | fzf-zsh | fzf-bash%b\n' "$C" "$Z" "$D" "$Z"

  printf '\n%bDefault%b (no %b-i%b)%b:%b\n' "$B" "$Z" "$C" "$Z" "$B" "$Z"
  printf '  %bchmod +x%b scripts/play-faah.sh, %bdependency report%b unless %b--skip-deps%b, then %bsuggested source lines%b.\n' \
    "$G" "$Z" "$Y" "$Z" "$C" "$Z" "$M" "$Z"

  printf '\n%bUninstall:%b\n' "$B" "$Z"
  printf '  Removes blocks between %b# >> faah:<id>%b and %b# << faah:<id>%b in:\n' "$M" "$Z" "$M" "$Z"
  printf '    - ~/.zshrc  (ids: zsh, fzf-zsh)\n'
  printf '    - ~/.bashrc (ids: bash, fzf-bash)\n'
  printf '  Also removes install artifact folders under %bFAHH_INSTALL_DEST%b, and removes %bFAHH_CONFIG_LINK%b\n' "$M" "$Z" "$M" "$Z"
  printf '  symlink if it points to this repository.\n'

  printf '\n%bEnvironment:%b\n' "$B" "$Z"
  printf '  %bFAHH_CONFIG_LINK%b    %bSymlink path for --symlink-config (default: ~/.config/faah)%b\n' "$M" "$Z" "$D" "$Z"
  printf '  %bFAHH_INSTALL_DEST%b   %bBase dir for -i Cursor/VS Code copies (default: ~/.config/faah/install)%b\n' "$M" "$Z" "$D" "$Z"
  printf '  %bFAHH_SOUND%b          %bSound file path for dependency check (optional)%b\n' "$M" "$Z" "$D" "$Z"
  printf '  %bNO_COLOR%b            %bSet to disable ANSI colors%b\n' "$M" "$Z" "$D" "$Z"
  printf '  %bFORCE_COLOR%b         %bSet to enable colors when stdout/stderr is not a TTY%b\n' "$M" "$Z" "$D" "$Z"

  printf '\n%bRepository root:%b %s\n' "$K" "$Z" "$ROOT"
}

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

# Missing-deps detection.
missing_deps() {
  local missing=()

  # Need at least one audio player.
  if ! have_cmd mpv && ! have_cmd ffplay && ! have_cmd paplay && ! have_cmd aplay; then
    missing+=(audio)
  fi

  # Optional, but commonly desired when enabling fzf integration.
  if ! have_cmd fzf; then
    missing+=(fzf)
  fi

  printf '%s\n' "${missing[*]:-}"
}

install_deps_apt() {
  local want_fzf=${1:-0}
  local pkgs=()

  # Ensure we can play MP3 reliably: mpv is the best single dependency on Ubuntu/Debian.
  if ! have_cmd mpv && ! have_cmd ffplay && ! have_cmd paplay && ! have_cmd aplay; then
    pkgs+=(mpv)
  fi

  # Provide fallbacks / common setups. (paplay/aplay won't decode MP3, but are useful if user swaps sound format.)
  have_cmd paplay || pkgs+=(pulseaudio-utils)
  have_cmd aplay || pkgs+=(alsa-utils)

  if [[ "$want_fzf" -eq 1 ]]; then
    have_cmd fzf || pkgs+=(fzf)
  fi

  if [[ "${#pkgs[@]}" -eq 0 ]]; then
    printf '%bok%b  %bdeps%b already satisfied (nothing to install)\n' "$G" "$Z" "$D" "$Z"
    return 0
  fi

  if [[ $EUID -ne 0 ]] && ! have_cmd sudo; then
    printf '%b%s:%b need %bsudo%b to install deps (or run as root)\n' \
      "$BE" "$(basename "$0")" "$ZE" "$YE" "$ZE" >&2
    return 1
  fi

  printf '\n%bInstall dependencies (apt)%b\n' "$B" "$Z"
  printf '%bWill install:%b %s\n' "$D" "$Z" "${pkgs[*]}"

  if [[ -z ${FAHH_YES:-} ]]; then
    if ! prompt_yn "Proceed with apt install (requires sudo)?" n; then
      printf '%bskip%b  dependency install cancelled\n' "$Y" "$Z"
      return 0
    fi
  fi

  if [[ $EUID -eq 0 ]]; then
    apt-get update
    apt-get install -y "${pkgs[@]}"
  else
    sudo apt-get update
    sudo apt-get install -y "${pkgs[@]}"
  fi

  printf '%bok%b  %bdeps%b installed\n' "$G" "$Z" "$D" "$Z"
}

install_missing_deps() {
  # For now, we implement Ubuntu/Debian apt only (selected by user).
  # If you need other distros, we can extend with dnf/pacman.
  local want_fzf=${1:-0}

  if have_cmd apt-get; then
    install_deps_apt "$want_fzf"
    return 0
  fi

  printf '%b%s:%b automatic dependency install not supported on this system (no apt-get)\n' \
    "$BE" "$(basename "$0")" "$ZE" "$YE" "$ZE" >&2
  printf '%bHint:%b install one of: mpv or ffmpeg (ffplay), and optionally fzf.\n' "$DE" "$ZE" >&2
  return 1
}

# Report audio players, fzf, and default sound file (merged from former check-deps.sh).
check_deps() {
  local c fzf_ver
  printf '\n%bDependencies%b\n' "${B}${C}" "$Z"
  printf '%bAudio%b (need one for MP3; %bmpv%b/%bffplay%b recommended)\n' "$D" "$Z" "$B" "$Z" "$B" "$Z"
  for c in mpv ffplay paplay aplay; do
    if have_cmd "$c"; then
      printf '  %bok%b   %s %b(%s)%b\n' "$G" "$Z" "$c" "$D" "$(command -v "$c")" "$Z"
    else
      printf '  %bmiss%b %s\n' "$Y" "$Z" "$c"
    fi
  done

  printf '\n%bfzf%b %b(optional)%b\n' "$B" "$Z" "$D" "$Z"
  if have_cmd fzf; then
    printf '  %bok%b   fzf %b(%s)%b\n' "$G" "$Z" "$D" "$(command -v fzf)" "$Z"
    fzf_ver=$(fzf --version 2>/dev/null | head -n1) || true
    [[ -n "$fzf_ver" ]] && printf '        %b%s%b\n' "$D" "$fzf_ver" "$Z"
  else
    printf '  %bmiss%b fzf\n' "$Y" "$Z"
  fi

  local sound=${FAHH_SOUND:-"$ROOT/assets/sounds/fahhh.mp3"}
  printf '\n%bDefault sound file%b\n' "$B" "$Z"
  if [[ -f "$sound" ]]; then
    printf '  %bok%b   %s\n' "$G" "$Z" "$sound"
  else
    printf '  %bmiss%b %s\n' "$R" "$Z" "$sound"
  fi
  printf '%b%s%b\n' "$K" '────────────────────────────' "$Z"
}

chmod_play() {
  if [[ ! -f "$PLAY" ]]; then
    printf '%b%s:%b %bmissing%b %s\n' "$BE" "$(basename "$0")" "$ZE" "$RE" "$ZE" "$PLAY" >&2
    exit 1
  fi
  chmod +x "$PLAY"
  printf '%bok%b  %bchmod +x%b %s\n' "$G" "$Z" "$D" "$Z" "$PLAY"
}

symlink_config() {
  mkdir -p "$(dirname "$LINK_TARGET")"
  ln -sfn "$ROOT" "$LINK_TARGET"
  printf '%bok%b  %bsymlink%b %s %b->%b %s\n' "$G" "$Z" "$B" "$Z" "$LINK_TARGET" "$C" "$Z" "$ROOT"
  printf '    %bexample:%b faah(){ source %q/init/faah.zsh; }; faah\n' "$K" "$Z" "$LINK_TARGET"
}

print_snippet() {
  local kind=${1:-}
  case "$kind" in
    zsh)
      # Minimal rc change: define+call a tiny bootstrap function that sources from ~/.config/faah.
      # Requires --symlink-config (or an equivalent manual symlink).
      printf "faah(){ source %q/init/faah.zsh; }; faah\n" "${LINK_TARGET}"
      ;;
    bash)
      printf "faah(){ source %q/init/faah.bash; }; faah\n" "${LINK_TARGET}"
      ;;
    fzf-zsh)
      # Prefer enabling via env so rc stays one-liner.
      printf 'export FAHH_ENABLE_FZF=1\n'
      ;;
    fzf-bash)
      printf 'export FAHH_ENABLE_FZF=1\n'
      ;;
    *)
      printf '%b%s:%b unknown snippet %b%q%b (use zsh, bash, fzf-zsh, fzf-bash)\n' \
        "$BE" "$(basename "$0")" "$ZE" "$YE" "$kind" "$ZE" >&2
      exit 1
      ;;
  esac
}

# --- Block markers (grep-safe): do not edit between markers by hand if you use the installer again

block_begin() { printf '# >> faah:%s\n' "$1"; }
block_end() { printf '# << faah:%s\n' "$1"; }

has_block() {
  local file=$1
  local id=$2
  [[ -f "$file" ]] && grep -qF "# >> faah:${id}" "$file"
}

remove_block() {
  local target=$1
  local id=$2
  local begin="# >> faah:${id}"
  local end="# << faah:${id}"

  if [[ ! -f "$target" ]]; then
    printf '%bskip%b  %s missing\n' "$Y" "$Z" "$target"
    return 0
  fi
  if ! grep -qF "$begin" "$target"; then
    printf '%bskip%b  block %bfaah:%s%b not in %s\n' "$Y" "$Z" "$M" "$id" "$Z" "$target"
    return 0
  fi

  backup_file "$target"

  local tmp
  tmp=$(mktemp)
  awk -v b="$begin" -v e="$end" '
    $0 == b {skip=1; next}
    $0 == e {skip=0; next}
    skip != 1 {print}
  ' "$target" >"$tmp"
  mv "$tmp" "$target"
  printf '%bok%b  removed %bfaah:%s%b -> %s\n' "$G" "$Z" "$M" "$id" "$Z" "$target"
}

backup_file() {
  local f=$1
  [[ -f "$f" ]] || return 0
  local b
  b="${f}.faahbak.$(date +%Y%m%d%H%M%S)"
  cp -a "$f" "$b"
  printf '%bok%b  %bbackup%b %s %b->%b %s\n' "$G" "$Z" "$D" "$Z" "$f" "$C" "$Z" "$b"
}

append_block() {
  local target=$1
  local id=$2
  shift 2
  if has_block "$target" "$id"; then
    printf '%bskip%b  block %bfaah:%s%b already in %s\n' "$Y" "$Z" "$M" "$id" "$Z" "$target"
    return 0
  fi
  backup_file "$target"
  {
    printf '\n'
    block_begin "$id"
    print_snippet "$@"
    block_end "$id"
  } >>"$target"
  printf '%bok%b  appended %bfaah:%s%b -> %s\n' "$G" "$Z" "$M" "$id" "$Z" "$target"
}

ensure_file() {
  local f=$1
  if [[ ! -f "$f" ]]; then
    mkdir -p "$(dirname "$f")"
    : >>"$f"
    printf '%bok%b  %bcreated%b %s\n' "$G" "$Z" "$D" "$Z" "$f"
  fi
}

# shellcheck disable=SC2162
prompt_yn() {
  local msg=$1
  local def=${2:-n}
  local line
  if [[ "$def" == "y" ]]; then
    printf '%b%s%b %b[Y/n]:%b ' "$B" "$msg" "$Z" "$D" "$Z"
  else
    printf '%b%s%b %b[y/N]:%b ' "$B" "$msg" "$Z" "$D" "$Z"
  fi
  if ! read -r line; then
    line=""
  fi
  line=${line:-}
  line=$(printf '%s' "$line" | tr '[:upper:]' '[:lower:]')
  if [[ -z "$line" ]]; then
    [[ "$def" == "y" ]]
    return
  fi
  [[ "$line" == y* ]]
}

install_cursor_helpers() {
  local d="${INSTALL_DEST}/cursor"
  mkdir -p "$d"
  cp -a "${ROOT}/cursor/settings.json.fragment" "${d}/settings.json.fragment"
  cp -a "${ROOT}/cursor/README.md" "${d}/README.md"
  printf '%bok%b  %bCursor%b helpers %b->%b %s\n' "$G" "$Z" "$C" "$Z" "$C" "$Z" "$d"
  printf '    %bNote:%b merge %bsettings.json.fragment%b into Cursor User settings (drop %b//%b JSON comments if needed).\n' \
    "$Y" "$Z" "$M" "$Z" "$K" "$Z"
}

install_vscode_helpers() {
  local d="${INSTALL_DEST}/vscode"
  mkdir -p "$d"
  cp -a "${ROOT}/vscode/settings.json.fragment" "${d}/settings.json.fragment"
  cp -a "${ROOT}/vscode/extensions.json" "${d}/extensions.json"
  cp -a "${ROOT}/vscode/README.md" "${d}/README.md"
  printf '%bok%b  %bVS Code%b helpers %b->%b %s\n' "$G" "$Z" "$C" "$Z" "$C" "$Z" "$d"
  printf '    %bNote:%b merge %bsettings.json.fragment%b into User settings; %bextensions.json%b optional per-workspace.\n' \
    "$Y" "$Z" "$M" "$Z" "$M" "$Z"
}

run_interactive() {
  if [[ ! -t 0 ]]; then
    printf '%b%s:%b %b--interactive%b needs a TTY (stdin is not interactive)\n' \
      "$BE" "$(basename "$0")" "$ZE" "$RE" "$ZE" >&2
    exit 1
  fi

  chmod_play
  if [[ -z ${FAHH_SKIP_DEPS:-} ]]; then
    check_deps
  fi
  # Offer to install missing deps in interactive mode.
  local md
  md=$(missing_deps)
  if [[ -n "$md" ]]; then
    printf '\n%bMissing deps detected:%b %s\n' "$Y" "$Z" "$md"
    if prompt_yn "Install missing dependencies now?" y; then
      # If user is in interactive mode, assume fzf could be desired.
      install_missing_deps 1 || true
      check_deps
    fi
  fi
  printf '\n%b==== faah interactive setup ====%b\n' "${B}${C}" "$Z"
  printf '%bRepo:%b %s\n\n' "$B" "$Z" "$ROOT"

  if prompt_yn "Create symlink ${LINK_TARGET} -> repo (stable path for minimal rc line)?" y; then
    symlink_config
  fi

  if prompt_yn "Add faah to ~/.zshrc (sound on non-zero exit)?" y; then
    ensure_file "${HOME}/.zshrc"
    append_block "${HOME}/.zshrc" "zsh" zsh
    if prompt_yn "  Also add fzf integration for zsh?" n; then
      append_block "${HOME}/.zshrc" "fzf-zsh" fzf-zsh
    fi
  fi

  if prompt_yn "Add faah to ~/.bashrc?" n; then
    ensure_file "${HOME}/.bashrc"
    append_block "${HOME}/.bashrc" "bash" bash
    if prompt_yn "  Also add fzf integration for bash?" n; then
      append_block "${HOME}/.bashrc" "fzf-bash" fzf-bash
    fi
  fi

  if prompt_yn "Copy Cursor settings fragments and README into ~/.config/faah/install/cursor/?" n; then
    install_cursor_helpers
  fi

  if prompt_yn "Copy VS Code settings fragments + extensions list into ~/.config/faah/install/vscode/?" n; then
    install_vscode_helpers
  fi

  printf '\n%b==== done ====%b\n' "${G}${B}" "$Z"
  printf '%bInstall artifacts:%b %s\n' "$D" "$Z" "$INSTALL_DEST"
}

uninstall_all() {
  local me
  me=$(basename "$0")

  if [[ ! -t 0 && -z ${FAHH_YES:-} ]]; then
    printf '%b%s:%b %b--uninstall%b needs a TTY (or set %b--yes%b / %bFAHH_YES=1%b)\n' \
      "$BE" "$me" "$ZE" "$RE" "$ZE" "$YE" "$ZE" "$YE" "$ZE" >&2
    exit 1
  fi

  printf '\n%bUninstall%b\n' "$B" "$Z"
  printf '%bTarget repo:%b %s\n' "$D" "$Z" "$ROOT"
  printf '%bWill modify:%b %s, %s\n' "$D" "$Z" "${HOME}/.zshrc" "${HOME}/.bashrc"
  printf '%bWill remove:%b %s (artifacts) and %s (symlink if points here)\n' "$D" "$Z" "$INSTALL_DEST" "$LINK_TARGET"

  if [[ -z ${FAHH_YES:-} ]]; then
    if ! prompt_yn "Proceed with uninstall?" n; then
      printf '%bskip%b  uninstall cancelled\n' "$Y" "$Z"
      return 0
    fi
  fi

  printf '\n%bShell rc cleanup%b\n' "$B" "$Z"
  remove_block "${HOME}/.zshrc" "fzf-zsh"
  remove_block "${HOME}/.zshrc" "zsh"
  remove_block "${HOME}/.bashrc" "fzf-bash"
  remove_block "${HOME}/.bashrc" "bash"

  printf '\n%bArtifacts cleanup%b\n' "$B" "$Z"
  if [[ -d "$INSTALL_DEST" ]]; then
    rm -rf "${INSTALL_DEST}/cursor" "${INSTALL_DEST}/vscode" 2>/dev/null || true
    # Remove the install dir if it becomes empty.
    rmdir "$INSTALL_DEST" 2>/dev/null || true
    printf '%bok%b  removed artifacts under %s\n' "$G" "$Z" "$INSTALL_DEST"
  else
    printf '%bskip%b  no artifacts dir %s\n' "$Y" "$Z" "$INSTALL_DEST"
  fi

  printf '\n%bSymlink cleanup%b\n' "$B" "$Z"
  if [[ -L "$LINK_TARGET" ]]; then
    local link
    link=$(readlink "$LINK_TARGET" || true)
    if [[ "$link" == "$ROOT" ]]; then
      rm -f "$LINK_TARGET"
      printf '%bok%b  removed symlink %s\n' "$G" "$Z" "$LINK_TARGET"
    else
      printf '%bskip%b  symlink %s points elsewhere (%s)\n' "$Y" "$Z" "$LINK_TARGET" "$link"
    fi
  else
    printf '%bskip%b  no symlink %s\n' "$Y" "$Z" "$LINK_TARGET"
  fi

  printf '\n%b==== uninstall complete ====%b\n' "${G}${B}" "$Z"
}

print_default_hints() {
  printf '\n%bSuggested shell rc lines%b (or %b%s -i%b):\n' "$B" "$Z" "$C" "$(basename "$0")" "$Z"
  printf '  %bzsh%b   ' "$M" "$Z"
  print_snippet zsh
  printf '  %bbash%b  ' "$M" "$Z"
  print_snippet bash
  printf '%bOptional fzf:%b\n' "$B" "$Z"
  printf '  %bzsh%b   ' "$M" "$Z"
  print_snippet fzf-zsh
  printf '  %bbash%b  ' "$M" "$Z"
  print_snippet fzf-bash
}

main() {
  local do_link=0
  local snippet=""
  local do_interactive=0
  local deps_only=0
  local do_install_deps=0
  local do_uninstall=0

  _faah_init_style

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h | --help)
        usage
        exit 0
        ;;
      --interactive | -i)
        do_interactive=1
        shift
        ;;
      --uninstall)
        do_uninstall=1
        shift
        ;;
      --yes)
        export FAHH_YES=1
        shift
        ;;
      --check-deps)
        deps_only=1
        shift
        ;;
      --install-deps)
        do_install_deps=1
        shift
        ;;
      --skip-deps)
        export FAHH_SKIP_DEPS=1
        shift
        ;;
      --symlink-config)
        do_link=1
        shift
        ;;
      --print-snippet)
        snippet=${2:-}
        if [[ -z "$snippet" ]]; then
          printf '%b%s:%b %b--print-snippet%b needs zsh, bash, fzf-zsh, or fzf-bash\n' \
            "$BE" "$(basename "$0")" "$ZE" "$YE" "$ZE" >&2
          printf '%bTry:%b %s --help\n' "$DE" "$ZE" "$(basename "$0")" >&2
          exit 1
        fi
        shift 2
        ;;
      *)
        printf '%b%s:%b unknown option %b%q%b\n' \
          "$BE" "$(basename "$0")" "$ZE" "$YE" "$1" "$ZE" >&2
        printf '%bTry:%b %s --help\n' "$DE" "$ZE" "$(basename "$0")" >&2
        exit 1
        ;;
    esac
  done

  if [[ "$deps_only" -eq 1 && "$do_interactive" -eq 0 ]]; then
    check_deps
    exit 0
  fi

  if [[ "$do_install_deps" -eq 1 ]]; then
    # Install missing deps (audio required; fzf optional but included in this mode).
    install_missing_deps 1
    check_deps
    exit 0
  fi

  if [[ "$do_uninstall" -eq 1 ]]; then
    uninstall_all
    exit 0
  fi

  if [[ "$do_interactive" -eq 1 ]]; then
    run_interactive
    exit 0
  fi

  chmod_play
  if [[ -z ${FAHH_SKIP_DEPS:-} ]]; then
    check_deps
  fi
  # Offer to install missing deps in normal (non-interactive) runs when attached to a TTY.
  # This keeps default behavior safe (no sudo unless the user confirms).
  if [[ -t 0 ]]; then
    local md
    md=$(missing_deps)
    if [[ -n "$md" ]]; then
      printf '\n%bMissing deps detected:%b %s\n' "$Y" "$Z" "$md"
      if prompt_yn "Install missing dependencies now?" n; then
        install_missing_deps 0 || true
        check_deps
      fi
    fi
  fi
  [[ "$do_link" -eq 1 ]] && symlink_config
  if [[ -n "$snippet" ]]; then
    print_snippet "$snippet"
    exit 0
  fi

  print_default_hints
}

main "$@"

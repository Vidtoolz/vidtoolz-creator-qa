#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ $# -lt 1 ]]; then
  echo "Error: missing input Markdown file." >&2
  echo "Usage: $0 INPUT.md [--profile PROFILE] [--json|--hermes-report|--linear-report|--report PATH]" >&2
  exit 2
fi

INPUT="$1"
shift

if [[ ! -f "$INPUT" ]]; then
  echo "Error: input Markdown file not found: $INPUT" >&2
  exit 2
fi

if [[ -f "${REPO_ROOT}/.venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "${REPO_ROOT}/.venv/bin/activate"
fi

ARGS=("check" "$INPUT")
HAS_PROFILE=0
HAS_OUTPUT_MODE=0

for arg in "$@"; do
  case "$arg" in
    --profile)
      HAS_PROFILE=1
      ;;
    --json|--hermes-report|--linear-report|--report)
      HAS_OUTPUT_MODE=1
      ;;
  esac
done

if [[ "$HAS_PROFILE" -eq 0 ]]; then
  ARGS+=("--profile" "resolve_tutorial")
fi

ARGS+=("$@")

if [[ "$HAS_OUTPUT_MODE" -eq 0 ]]; then
  ARGS+=("--hermes-report")
fi

exec env PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}" python -m creator_qa.cli "${ARGS[@]}"

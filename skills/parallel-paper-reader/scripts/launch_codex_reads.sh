#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <paper-input> [more paper inputs...]" >&2
  exit 1
fi


for paper in "$@"; do
  echo "Launching codex for: $paper"
  codex --dangerously-bypass-approvals-and-sandbox --search exec "帮我阅读这篇论文：${paper}"&
done

wait

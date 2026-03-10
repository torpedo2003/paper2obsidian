#!/usr/bin/env bash
set -euo pipefail

MAX_BATCH_SIZE=5
SLEEP_SECONDS=30

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <paper-input> [more paper inputs...]" >&2
  exit 1
fi

papers=("$@")
total=${#papers[@]}
index=0
batch=1

while [ "$index" -lt "$total" ]; do
  remaining=$((total - index))
  current_batch_size=$MAX_BATCH_SIZE
  if [ "$remaining" -lt "$current_batch_size" ]; then
    current_batch_size=$remaining
  fi

  echo "Starting batch ${batch}: ${current_batch_size} paper(s)"

  pids=()
  for ((offset = 0; offset < current_batch_size; offset++)); do
    paper=${papers[index + offset]}
    echo "Launching codex for: ${paper}"
    codex --dangerously-bypass-approvals-and-sandbox --search exec "帮我阅读这篇论文：${paper}" &
    pids+=("$!")
  done

  for pid in "${pids[@]}"; do
    wait "$pid"
  done

  index=$((index + current_batch_size))

  if [ "$index" -lt "$total" ]; then
    echo "Batch ${batch} completed. Waiting ${SLEEP_SECONDS}s before next batch..."
    sleep "$SLEEP_SECONDS"
  fi

  batch=$((batch + 1))
done

echo "All paper tasks completed."

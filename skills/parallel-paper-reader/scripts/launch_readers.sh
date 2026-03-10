#!/usr/bin/env bash
set -euo pipefail

MAX_BATCH_SIZE=5
SLEEP_SECONDS=30
AGENT="codex"
PROMPT_TEMPLATE="帮我阅读这篇论文："

usage() {
  echo "Usage: $0 [--agent <codex|claude>] <paper-input> [more paper inputs...]" >&2
  echo "  --agent, -a: 选择使用的 agent CLI (默认: codex)" >&2
  echo "  支持的 agent: codex, claude" >&2
  exit 1
}

# 解析参数
while [ "$#" -gt 0 ]; do
  case "$1" in
    --agent|-a)
      AGENT="$2"
      shift 2
      ;;
    -*)
      usage
      ;;
    *)
      break
      ;;
  esac
done

if [ "$#" -eq 0 ]; then
  usage
fi

# 根据 agent 选择命令
case "$AGENT" in
  codex)
    AGENT_CMD="codex --dangerously-bypass-approvals-and-sandbox --search exec"
    ;;
  claude|claudecode)
    AGENT_CMD="claude --allow-dangerously-skip-permissions -p"
    ;;
  *)
    echo "Error: 不支持的 agent: $AGENT" >&2
    echo "支持的 agent: codex, claude" >&2
    exit 1
    ;;
esac

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

  for ((offset = 0; offset < current_batch_size; offset++)); do
    paper=${papers[index + offset]}
    echo "Launching ${AGENT} for: ${paper}"
    $AGENT_CMD "${PROMPT_TEMPLATE}${paper}" &
  done

  index=$((index + current_batch_size))

  if [ "$index" -lt "$total" ]; then
    echo "Batch ${batch} started. Waiting ${SLEEP_SECONDS}s before next batch..."
    sleep "$SLEEP_SECONDS"
  fi

  batch=$((batch + 1))
done

echo "All batches launched. Waiting for all tasks to complete..."
wait
echo "All paper tasks completed."
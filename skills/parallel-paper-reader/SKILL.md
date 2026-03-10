---
name: parallel-paper-reader
description: Use when the user wants to read multiple papers in parallel through Codex or Codex CLI, especially when they provide several arXiv IDs, arXiv URLs, PDF links, or other paper URLs and want one thread/process per paper. Launch one `codex exec` command per paper concurrently instead of reading papers serially.
---

# Parallel Paper Reader

Launch one Codex task per paper in parallel.

## Workflow

1. Treat each user-provided paper reference as an opaque input. Do not require an arXiv ID.
2. Accept raw arXiv IDs, arXiv URLs, PDF links, and other paper URLs, or even the paper title.
3. Start one background task per paper with:

```bash
codex --dangerously-bypass-approvals-and-sandbox --search exec "帮我阅读这篇论文：<paper_input>"
```

4. Launch all tasks before waiting for completion. Do not run papers serially.
5. Prefer `scripts/launch_codex_reads.sh` when many papers are provided.

## Commands

Run the bundled script:

```bash
scripts/launch_codex_reads.sh "2503.15457" "https://arxiv.org/abs/2603.04379" "Helios: Real Real-Time Long Video Generation Model" "https://example.com/paper.pdf"
```

## Output Rules

- Echo each paper before launching it.
- Keep one paper per process.
- Preserve the user-provided order when printing launch logs.
- Pass the original input through unchanged.

---
name: parallel-paper-reader
description: 当用户要并行阅读多篇论文，且给出多个 arXiv ID、arXiv 链接、PDF 链接、论文页面链接或标题时使用。
---

# 并行读论文

多篇论文时，直接运行脚本，不要手动逐篇启动。

## 用法

把用户给的每篇论文作为一个参数（arXiv ID or PDF URL or full title）传给脚本：

```bash
skills/parallel-paper-reader/scripts/launch_readers.sh \
  "2503.15457" \
  "https://arxiv.org/abs/2603.04379" \
  "Helios: Real Real-Time Long Video Generation Model" \
  "https://example.com/paper.pdf"
```

### 指定 Agent

默认使用 `codex`，可通过 `--agent` 或 `-a` 指定：

```bash
# 使用 claude code
skills/parallel-paper-reader/scripts/launch_readers.sh --agent claude "2503.15457"

# 使用 codex（默认）
skills/parallel-paper-reader/scripts/launch_readers.sh -a codex "2503.15457"
```

### 不支持的 Agent

当前支持的 agent：`codex`, `claude`

如果用户指定了其他不在此列表中的 agent，**直接终止并告知用户**：
- 告诉用户当前支持的 agent 列表
- 告诉用户该功能尚未支持，建议用户更换为支持的 agent

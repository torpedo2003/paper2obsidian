---
name: parallel-paper-reader
description: 当用户要并行阅读多篇论文，且给出多个 arXiv ID、arXiv 链接、PDF 链接、论文页面链接或标题时使用。
---

# 并行读论文

多篇论文时，直接运行脚本，不要手动逐篇启动。

## 用法

把用户给的每篇论文原样作为一个参数传给脚本：

```bash
skills/parallel-paper-reader/scripts/launch_readers.sh \
  "2503.15457" \
  "https://arxiv.org/abs/2603.04379" \
  "Helios: Real Real-Time Long Video Generation Model" \
  "https://example.com/paper.pdf"
```

## 规则

- 不要求必须是 arXiv ID，标题、URL、PDF 链接都可以。
- 输入保持原样传入，不要改写。
- 每篇论文单独启动一个 `codex exec` 进程。
- 并行和分批规则全部交给脚本处理。
- 按用户提供顺序输出启动日志。

## 提示词

脚本内部固定使用：

```text
帮我阅读这篇论文：<paper_input>
```

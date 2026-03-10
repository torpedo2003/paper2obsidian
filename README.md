# paper2obsidian

`paper2obsidian` is a skill collection for turning papers into well-structured notes, summaries, and indexes inside an Obsidian vault.

It is designed for research-heavy workflows: reading a single paper deeply, summarizing a group of papers, rebuilding local paper indexes, and scaling multi-paper reading with parallel Codex tasks.

中文简介：`paper2obsidian` 是一组面向 Obsidian 论文工作流的 skills，用于把单篇论文阅读、多篇论文综述、论文索引整理与并行阅读整合到同一个本地知识库流程中。

## Highlights

- **Single-paper reading**: download a paper PDF, extract content with MinerU when possible, and generate a detailed Obsidian note.
- **Multi-paper summary**: turn a set of papers or a topic cluster into a focused literature summary.
- **Paper index maintenance**: rebuild paper metadata indexes and category `.base` files for Obsidian Bases.
- **Parallel reading**: launch one Codex task per paper when batch-reading several papers.
- **Vault-first workflow**: outputs are intended to land in your local Obsidian vault instead of staying in chat.

## 功能亮点

- **单篇精读**：自动围绕单篇论文生成结构化 Obsidian 笔记。
- **多篇综述**：按主题、方向或给定论文集合输出综述内容。
- **索引重建**：维护论文库索引、分类和 `.base` 文件。
- **并行读论文**：针对多篇论文并发启动独立 Codex 任务。
- **本地知识库优先**：核心产物默认写入 Obsidian vault，而不是停留在聊天窗口。

## Repository Structure

```text
skills/
├── paper-reading/          # Read one paper and generate a detailed note
├── paper-summary/          # Summarize multiple papers into a survey-style note
├── paper-index/            # Rebuild paper indexes and Obsidian Bases files
└── parallel-paper-reader/  # Launch one Codex job per paper in parallel
```

## 仓库结构

```text
skills/
├── paper-reading/          # 单篇论文阅读与笔记生成
├── paper-summary/          # 多篇论文总结与综述
├── paper-index/            # 论文索引整理与 .base 生成
└── parallel-paper-reader/  # 多篇论文并行阅读调度
```

## Included Skills

### 1. `paper-reading`

Use this skill when you want to read, interpret, summarize, or import **one paper** into Obsidian.

What it is good at:
- accepts arXiv IDs, arXiv URLs, PDF links, landing pages, and local PDFs
- prefers PDF extraction with MinerU
- writes a detailed note into the Obsidian vault
- keeps the workflow note-centric instead of chat-centric

适用场景：当你想“读这篇论文”“帮我理解这篇 paper”“把这篇论文导入 Obsidian”时使用。

### 2. `paper-summary`

Use this skill when you want a **literature review / survey** over multiple papers, a topic area, or a paper category.

What it is good at:
- organizing papers around research questions and methodology
- turning scattered notes into review-style outputs
- producing material that can also be used for interview prep or topic review

适用场景：当你想“总结这些论文”“做个 survey”“梳理某个方向”时使用。

### 3. `paper-index`

Use this skill when you want to **rebuild or clean up** an existing paper vault.

What it is good at:
- generating or updating `.base` index files for Obsidian Bases
- checking note metadata consistency
- rebuilding category views for an existing paper library
- auditing explicit links and paper relationships inside the vault

适用场景：当你想“更新索引”“重建索引”“重新分类”“整理当前 vault 的 papers”时使用。

### 4. `parallel-paper-reader`

Use this skill when you want to read **multiple papers in parallel** through Codex / Codex CLI.

What it is good at:
- launching one process per paper
- preserving the original paper input format
- speeding up batch reading compared with serial processing

适用场景：当你一次要处理多篇 arXiv 链接、PDF 链接或论文标题时使用。

## How It Fits Into a Workflow

A typical workflow looks like this:

1. Use `paper-reading` to create detailed notes for important papers.
2. Use `paper-summary` to synthesize several papers into a topic-level overview.
3. Use `paper-index` to keep your vault organized and queryable.
4. Use `parallel-paper-reader` when you need throughput on a batch of papers.

## 工作流建议

一个典型流程通常是：

1. 先用 `paper-reading` 精读核心论文并生成笔记。
2. 再用 `paper-summary` 把多篇论文整理为某个主题的综述。
3. 用 `paper-index` 维护索引、分类和 `.base` 视图。
4. 如果一次处理很多论文，用 `parallel-paper-reader` 并行提速。

## Design Principles

- **Obsidian-first**: notes should live in the vault and remain useful after the chat ends.
- **Research-oriented**: optimized for ML / AI paper reading and review workflows.
- **Composable**: each skill handles a clear stage of the paper workflow.
- **Non-invasive**: documentation and workflow guidance are separated from core logic.

## 设计原则

- **以 Obsidian 为中心**：结果应沉淀到本地知识库中。
- **面向研究工作流**：更适合 ML / AI 论文阅读、总结和整理。
- **可组合**：不同 skill 负责不同阶段，可单独用，也可串联用。
- **不侵入核心功能**：文档说明与核心实现解耦。

## Example Use Cases

- Read one newly released paper and save a structured note.
- Build a topic summary for a group of diffusion or LLM papers.
- Reorganize an existing Obsidian paper vault with category indexes.
- Batch-process several papers in parallel before a paper reading meeting.

## 示例场景

- 精读一篇新论文并保存成结构化笔记。
- 针对某个方向生成文献综述，例如 Diffusion 或 LLM。
- 整理已有的 Obsidian 论文库并重建分类索引。
- 在组会前并行处理多篇论文，提高预读效率。

## Who This Is For

This repository is a good fit for:
- ML / AI researchers
- graduate students building a paper knowledge base
- anyone maintaining papers in Obsidian
- users who prefer local, reusable research artifacts over chat-only summaries

## 适合谁使用

这个仓库适合：
- 机器学习 / 人工智能研究者
- 需要系统读论文的学生
- 用 Obsidian 管理论文知识库的用户
- 希望把输出沉淀为可复用本地资产的人

## Notes

- This repository is primarily a **skill repository**, not a standalone end-user application.
- The exact runtime behavior depends on the agent environment where these skills are loaded.
- The README intentionally documents the current capabilities without changing core functionality.

## 说明

- 这个仓库目前主要是一个 **skills 仓库**，不是独立的终端应用。
- 实际运行方式取决于这些 skills 被加载到什么 agent / CLI 环境中。
- 本 README 以梳理现有能力为目标，不改动核心功能。

## License

Add a license here if you want to open-source the repository more formally.

中文说明：如果你准备长期公开维护，建议后续补充 `LICENSE`。

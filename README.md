# paper2obsidian

[English](#paper2obsidian) | [中文](#中文说明)

`paper2obsidian` is a skill collection for turning papers into well-structured notes, summaries, and indexes inside an Obsidian vault.

It is designed for research-heavy workflows: reading a single paper deeply, summarizing a group of papers, rebuilding local paper indexes, and scaling multi-paper reading with parallel Codex tasks.

## Highlights

- **Single-paper reading**: download a paper PDF, extract content with MinerU when possible, and generate a detailed Obsidian note.
- **Multi-paper summary**: turn a set of papers or a topic cluster into a focused literature summary.
- **Paper index maintenance**: rebuild paper metadata indexes and category `.base` files for Obsidian Bases.
- **Parallel reading**: launch one Codex task per paper when batch-reading several papers.
- **Vault-first workflow**: outputs are intended to land in your local Obsidian vault instead of staying in chat.

## Repository Structure

```text
skills/
├── paper-reading/          # Read one paper and generate a detailed note
├── paper-summary/          # Summarize multiple papers into a survey-style note
├── paper-index/            # Rebuild paper indexes and Obsidian Bases files
└── parallel-paper-reader/  # Launch one Codex job per paper in parallel
```

## Included Skills

### 1. `paper-reading`

Use this skill when you want to read, interpret, summarize, or import **one paper** into Obsidian.

What it is good at:
- accepts arXiv IDs, arXiv URLs, PDF links, landing pages, and local PDFs
- prefers PDF extraction with MinerU
- writes a detailed note into the Obsidian vault
- keeps the workflow note-centric instead of chat-centric

### 2. `paper-summary`

Use this skill when you want a **literature review / survey** over multiple papers, a topic area, or a paper category.

What it is good at:
- organizing papers around research questions and methodology
- turning scattered notes into review-style outputs
- producing material that can also be used for interview prep or topic review

### 3. `paper-index`

Use this skill when you want to **rebuild or clean up** an existing paper vault.

What it is good at:
- generating or updating `.base` index files for Obsidian Bases
- checking note metadata consistency
- rebuilding category views for an existing paper library
- auditing explicit links and paper relationships inside the vault

### 4. `parallel-paper-reader`

Use this skill when you want to read **multiple papers in parallel** through Codex / Codex CLI.

What it is good at:
- launching one process per paper
- preserving the original paper input format
- speeding up batch reading compared with serial processing

## How It Fits Into a Workflow

A typical workflow looks like this:

1. Use `paper-reading` to create detailed notes for important papers.
2. Use `paper-summary` to synthesize several papers into a topic-level overview.
3. Use `paper-index` to keep your vault organized and queryable.
4. Use `parallel-paper-reader` when you need throughput on a batch of papers.

## Design Principles

- **Obsidian-first**: notes should live in the vault and remain useful after the chat ends.
- **Research-oriented**: optimized for ML / AI paper reading and review workflows.
- **Composable**: each skill handles a clear stage of the paper workflow.
- **Non-invasive**: documentation and workflow guidance are separated from core logic.

## Example Use Cases

- Read one newly released paper and save a structured note.
- Build a topic summary for a group of diffusion or LLM papers.
- Reorganize an existing Obsidian paper vault with category indexes.
- Batch-process several papers in parallel before a paper reading meeting.

## Who This Is For

This repository is a good fit for:
- ML / AI researchers
- graduate students building a paper knowledge base
- anyone maintaining papers in Obsidian
- users who prefer local, reusable research artifacts over chat-only summaries

## Notes

- This repository is primarily a **skill repository**, not a standalone end-user application.
- The exact runtime behavior depends on the agent environment where these skills are loaded.
- The README intentionally documents the current capabilities without changing core functionality.

## License

Add a license here if you want to open-source the repository more formally.

## 中文说明

[返回英文](#paper2obsidian)

`paper2obsidian` 是一组面向 Obsidian 论文工作流的 skills，用于把单篇论文阅读、多篇论文综述、论文索引整理与并行阅读整合到同一个本地知识库流程中。

它适合研究型工作流：精读单篇论文、总结一组论文、重建本地论文索引，以及通过并行 Codex 任务提升批量读论文效率。

## 功能亮点

- **单篇精读**：自动围绕单篇论文生成结构化 Obsidian 笔记。
- **多篇综述**：按主题、方向或给定论文集合输出综述内容。
- **索引重建**：维护论文库索引、分类和 `.base` 文件。
- **并行读论文**：针对多篇论文并发启动独立 Codex 任务。
- **本地知识库优先**：核心产物默认写入 Obsidian vault，而不是停留在聊天窗口。

## 仓库结构

```text
skills/
├── paper-reading/          # 单篇论文阅读与笔记生成
├── paper-summary/          # 多篇论文总结与综述
├── paper-index/            # 论文索引整理与 .base 生成
└── parallel-paper-reader/  # 多篇论文并行阅读调度
```

## 包含的 Skills

### 1. `paper-reading`

当你想阅读、解读、总结或导入 **单篇论文** 到 Obsidian 时，使用这个 skill。

它擅长：
- 接收 arXiv ID、arXiv URL、PDF 链接、论文落地页和本地 PDF
- 优先使用 MinerU 做 PDF 提取
- 将详细笔记写入 Obsidian vault
- 让工作流以笔记沉淀为中心，而不是停留在聊天里

### 2. `paper-summary`

当你想围绕多篇论文、一个研究方向或某个论文分类生成 **综述 / survey** 时，使用这个 skill。

它擅长：
- 按研究问题和方法脉络组织论文
- 把零散论文整理成综述式输出
- 生成可用于面试复习和方向梳理的材料

### 3. `paper-index`

当你想 **重建或整理** 现有论文 vault 时，使用这个 skill。

它擅长：
- 为 Obsidian Bases 生成或更新 `.base` 索引文件
- 检查笔记元数据一致性
- 重建现有论文库的分类视图
- 审计 vault 中显式论文链接和关系字段

### 4. `parallel-paper-reader`

当你想通过 Codex / Codex CLI **并行阅读多篇论文** 时，使用这个 skill。

它擅长：
- 每篇论文启动一个独立进程
- 保留用户原始输入格式
- 相比串行处理更适合批量阅读

## 工作流建议

一个典型流程通常是：

1. 先用 `paper-reading` 精读核心论文并生成笔记。
2. 再用 `paper-summary` 把多篇论文整理为某个主题的综述。
3. 用 `paper-index` 维护索引、分类和 `.base` 视图。
4. 如果一次处理很多论文，用 `parallel-paper-reader` 并行提速。

## 设计原则

- **以 Obsidian 为中心**：结果应沉淀到本地知识库中。
- **面向研究工作流**：更适合 ML / AI 论文阅读、总结和整理。
- **可组合**：不同 skill 负责不同阶段，可单独用，也可串联用。
- **不侵入核心功能**：文档说明与核心实现解耦。

## 示例场景

- 精读一篇新论文并保存成结构化笔记。
- 针对某个方向生成文献综述，例如 Diffusion 或 LLM。
- 整理已有的 Obsidian 论文库并重建分类索引。
- 在组会前并行处理多篇论文，提高预读效率。

## 适合谁使用

这个仓库适合：
- 机器学习 / 人工智能研究者
- 需要系统读论文的学生
- 用 Obsidian 管理论文知识库的用户
- 希望把输出沉淀为可复用本地资产的人

## 说明

- 这个仓库目前主要是一个 **skills 仓库**，不是独立的终端应用。
- 实际运行方式取决于这些 skills 被加载到什么 agent / CLI 环境中。
- 本 README 以梳理现有能力为目标，不改动核心功能。

## 许可证

如果你准备长期公开维护，建议后续补充 `LICENSE`。

---
name: paper-index
description: 使用 Obsidian Bases 维护论文数据库，自动生成和更新 `.base` 文件、重建分类索引、校验论文之间的链接关系。当用户要求“更新索引”、“重建索引”、“重新分类”、“梳理论文库”、“整理当前 vault 的 papers”、“检查论文之间的引用/关联是否正确”、“生成论文列表”时都应加载此 skill。即使用户没有要求导入新论文，只是想重整现有论文库，也优先使用此 skill。
---

# Paper Index

使用 Obsidian Bases（`.base` 文件）维护论文数据库索引。这个 skill 的目标不是导入新论文，而是**快速扫描当前 vault 中已有的论文笔记，重建索引、细化分类，并校验显式的论文关联关系**。

默认优先走“快速重索引”路径：尽量基于 frontmatter、文件名、tags 和显式 wikilinks 工作，避免逐篇深读正文，以免拖慢速度。

## 前置要求

- Obsidian 1.9+（内置 Bases 功能）
- 论文笔记位于 `$OBSIDIAN_VAULT/papers/notes/`
- 论文笔记 frontmatter 至少应包含以下字段：`paper_id`, `title`, `title_zh`, `authors`, `year`, `src_type`, `src_url`, `pdf`, `tags`, `tldr`, `date_added`
- `arxiv` 字段仅在 arXiv 论文中填写；非 arXiv 论文可省略
- 如果笔记里额外维护了 `references`, `related`, `cites`, `cited_by`, `predecessors`, `successors` 等字段，可在重索引时一并校验；没有这些字段也可以正常工作

## 目录结构

```text
vault/
├── papers/
│   ├── index/
│   │   ├── 01-All-Papers.base
│   │   ├── Video-Generation.base
│   │   ├── Multimodal.base
│   │   ├── Reasoning.base
│   │   ├── ...
│   │   └── 00-Index-Audit.md        # 可选：重索引/关系校验摘要
│   └── notes/
│       ├── 2402.03300.md
│       ├── 2503.01234.md
│       └── ...
```

## 工作流程

### Step 1: 扫描并规范化现有论文库

扫描 `$OBSIDIAN_VAULT/papers/notes/` 下所有 `.md` 文件，优先读取 frontmatter 与文件名，建立当前 vault 的论文注册表。

在这一步做**轻量规范化**，不要进入慢速逐篇解读模式：

- 读取 `paper_id`、`title`、`year`、`tags`、`src_type`、`src_url`
- 如果文件名与 `paper_id` 不一致，以 `paper_id` 为主标识理解该论文
- 检查是否存在重复 `paper_id`
- 检查缺失关键字段的笔记，并在最终摘要中报告
- 统一 tags 的基本格式：不含空格，多个单词优先用连字符 `-` 或下划线 `_`
- 不要在此步骤下载、导入或解析新论文；目标是整理**当前已有**的 vault

### Step 2: 重新分类并生成更完整的 AI taxonomy

基于论文 tags 做多标签分类。一篇论文可以命中多个分类；优先保留细分类，不要只给过于宽泛的大类。

当用户的论文主要集中在生成式 AI、图像、视频、多模态方向时，优先确保这些分类足够细；同时也要覆盖更广泛的 AI 研究方向，便于长期维护整个论文库。

使用以下分类映射作为默认 taxonomy；若遇到稳定出现的新主题，可新增合理英文分类名，但不要无节制地碎片化。

### 核心生成式 AI / 多模态方向

- `image-generation`, `text-to-image`, `image-synthesis`, `image-editing` → **Image-Generation**
- `video`, `video-generation`, `text-to-video`, `image-to-video`, `long-video`, `video-editing`, `video-prediction` → **Video-Generation**
- `diffusion`, `diffusion-model`, `latent-diffusion`, `rectified-flow`, `flow-matching`, `consistency-model` → **Diffusion**
- `autoregressive`, `next-token-prediction`, `masked-diffusion`, `discrete-diffusion` → **Autoregressive-Generation**
- `world-model`, `world-models`, `generative-simulation`, `predictive-modeling` → **World-Models**
- `multimodal`, `vision-language`, `vlm`, `mllm`, `vision-language-model` → **Multimodal**
- `text-to-3d`, `3d-generation`, `neural-rendering`, `gaussian-splatting`, `4d-generation` → **3D-Generation**
- `audio-generation`, `music-generation`, `speech-synthesis`, `text-to-speech`, `voice-generation`, `sound-generation` → **Audio-Speech**
- `image-understanding`, `video-understanding`, `visual-question-answering`, `captioning` → **Vision-Understanding**

### 大模型 / 推理 / 智能体方向

- `llm`, `language-model`, `foundation-model`, `instruction-tuning` → **Large-Language-Models**
- `reasoning`, `math-reasoning`, `chain-of-thought`, `verifier`, `search`, `deliberation` → **Reasoning**
- `agent`, `agents`, `tool-use`, `planning`, `web-agent`, `computer-use` → **Agents**
- `rag`, `retrieval`, `retrieval-augmented-generation`, `memory`, `knowledge-base` → **RAG-and-Memory**
- `alignment`, `dpo`, `preference`, `rlhf`, `constitutional-ai`, `reward-model` → **Alignment**
- `safety`, `guardrails`, `jailbreak`, `red-teaming`, `moderation` → **Safety**
- `evaluation`, `benchmark`, `judge`, `arena`, `eval` → **Evaluation**
- `interpretability`, `mechanistic-interpretability`, `sae`, `probing`, `activation-patching` → **Interpretability**

### 视觉 / 感知 / 机器人方向

- `vision`, `computer-vision`, `image-classification`, `detection`, `segmentation`, `tracking` → **Computer-Vision**
- `video-understanding`, `action-recognition`, `temporal-modeling` → **Video-Understanding**
- `robotics`, `robot-learning`, `policy-learning`, `manipulation`, `navigation` → **Robotics**
- `embodied-ai`, `embodied-agent`, `embodied-reasoning` → **Embodied-AI**

### 学习范式 / 训练 / 系统方向

- `reinforcement-learning`, `grpo`, `ppo`, `dapo`, `dr-grpo`, `rloo` → **Reinforcement-Learning**
- `pretraining`, `continued-pretraining`, `scaling`, `data`, `curriculum` → **Pretraining-and-Data**
- `post-training`, `sft`, `distillation`, `knowledge-distillation`, `model-merging` → **Post-Training-and-Distillation**
- `attention`, `transformer`, `architecture`, `mamba`, `moe`, `rwkv` → **Architecture**
- `compression`, `quantization`, `pruning`, `speculative-decoding`, `efficient-inference` → **Efficiency-and-Inference**
- `serving`, `vllm`, `systems`, `inference-engine`, `deployment` → **Serving-and-Systems**
- `optimization`, `optimizer`, `training-stability`, `flash-attention` → **Optimization**

### 其他常见 AI 方向

- `nlp`, `information-extraction`, `summarization`, `translation` → **NLP**
- `speech-recognition`, `asr`, `audio-understanding` → **Speech-and-Audio-Understanding**
- `recommendation`, `ranking`, `ctr` → **Recommendation**
- `graph-learning`, `gnn`, `knowledge-graph` → **Graph-Learning**
- `scientific-ai`, `science`, `biology`, `chemistry`, `protein` → **AI-for-Science**

分类原则：

- 一篇论文允许属于多个分类
- 优先保留高信息量细分类，例如 `Video-Generation`、`Diffusion`、`World-Models`，不要只落到 `Multimodal` 或 `Architecture`
- 如果一篇论文同时属于“方法”和“应用”，两类都保留
- 遇到新 tag 时，先判断是否可归入已有分类；只有在明显形成稳定主题时才新增分类

### Step 3: 重建 `.base` 索引并校验显式关联关系

检查 `$OBSIDIAN_VAULT/papers/index/` 下已有的 `.base` 文件，并执行以下操作：

- 如果 `01-All-Papers.base` 不存在则创建；存在则不覆盖
- 对新分类创建对应 `.base` 文件；已有分类 `.base` 不覆盖
- 如果用户明确要求“重新索引当前 vault”，除了 `.base` 外，还可以额外生成或更新一个简短的 `00-Index-Audit.md`，汇总：
  - 新增了哪些分类
  - 哪些论文缺失关键字段
  - 哪些 `paper_id` 重复或疑似冲突
  - 哪些显式 wikilinks / 关系字段无法解析

关联关系校验只做**显式、可确定**的检查，不要臆造文献关系：

- 检查正文中直接出现的论文 wikilinks（例如 `[[2402.03300]]`、`[[papers/notes/2402.03300]]`）是否能解析到现有文件
- 如果存在 `references`, `related`, `cites`, `cited_by`, `predecessors`, `successors` 等字段，检查其中引用的 `paper_id` / note link 是否在当前 vault 中存在
- 对于能**确定性修复**的链接格式问题，可以直接统一
- 对于歧义情况，只在 `00-Index-Audit.md` 中报告，不要擅自改写
- 不要为了补全关系而去在线检索论文；此 skill 的目标是整理本地库，而不是做外部文献发现

## `.base` 模板

**总库（`01-All-Papers.base`）：** 如果不存在则创建，已存在则不覆盖。

```yaml
filters:
  and:
    - file.inFolder("papers/notes")
    - 'file.ext == "md"'

formulas:
  paper_link: 'file.asLink(paper_id)'

properties:
  formula.paper_link:
    displayName: "Paper ID"
  title:
    displayName: "Title"
  title_zh:
    displayName: "中文名"
  tldr:
    displayName: "TLDR"
  tags:
    displayName: "标签"

views:
  - type: table
    name: "All Papers"
    order:
      - formula.paper_link
      - title_zh
      - title
      - tldr
      - tags
    groupBy:
      property: year
      direction: DESC
```

这里不要直接把 `paper_id` 作为普通文本列展示；应在 `formulas:` 中定义 `paper_link: 'file.asLink(paper_id)'`，再在表格中显示 `formula.paper_link`，这样列中显示的是 `paper_id`，点击后能打开对应笔记。

**分类库（`{Category-Name}.base`）：** 对每个分类，如果对应的 `.base` 文件不存在则创建。filter 条件使用 `tags.contains("tag-name")` 匹配。如果一个分类对应多个 tag，用 `or` 组合：

```yaml
filters:
  and:
    - file.inFolder("papers/notes")
    - 'file.ext == "md"'
    - or:
        - 'tags.contains("video-generation")'
        - 'tags.contains("text-to-video")'
        - 'tags.contains("image-to-video")'

formulas:
  paper_link: 'file.asLink(paper_id)'

properties:
  formula.paper_link:
    displayName: "Paper ID"
  title:
    displayName: "Title"
  title_zh:
    displayName: "中文名"
  tldr:
    displayName: "TLDR"
  tags:
    displayName: "标签"

views:
  - type: table
    name: "Category-Name"
    order:
      - formula.paper_link
      - title_zh
      - title
      - tldr
      - tags
    groupBy:
      property: year
      direction: DESC
```

## 重要规则

- `.base` 文件使用 YAML 格式，不是 Markdown
- 已存在的 `.base` 文件不要覆盖（用户可能手动调整过视图配置）
- 只创建新分类对应的 `.base` 文件
- 分类名使用稳定英文名，如 `Video-Generation`、`World-Models`、`Reasoning`
- filter 中的 tag 必须与论文 frontmatter 中的 tags 完全匹配（区分大小写）
- 不要假设所有论文都来自 arXiv；索引必须同样适用于非 arXiv 论文
- 快速重索引时，优先基于 frontmatter、文件名、tags、显式 links 工作，不要默认进入慢速全文阅读
- 用户如果要求“只整理当前库”，不要下载、导入或生成新的论文笔记
- 对关系修复只做确定性修改；不确定的情况报告即可

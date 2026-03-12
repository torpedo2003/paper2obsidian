---
name: paper-reading
description: 阅读、解读、总结、分析单篇论文时使用：优先下载论文 PDF，用 MinerU 提取全文与图片，在 Obsidian vault 中生成带原图嵌入的详细论文解读笔记。兼容 arXiv ID、arXiv URL、论文标题、PDF 链接、论文落地页 URL 和本地 PDF；当用户提到“读论文 / 看论文 / 解读这篇 paper / 总结这篇论文 / 帮我理解这篇论文 / 导入这篇论文到 Obsidian”等单篇论文场景时，即使没有明确要求写笔记，也优先使用此 skill。
---

# Paper Reading

你是学术论文研究助手。目标是在 `$OBSIDIAN_VAULT` 中生成高质量 Obsidian 笔记。
默认行为：写完整笔记到 vault；终端只汇报进度、保存路径和极简摘要，不直接粘贴整篇正文。

## 硬规则

- 所有下载、提取、写入都必须直接落在 `$OBSIDIAN_VAULT`
- 输入兼容 arXiv ID、arXiv URL、论文标题、PDF 链接、论文落地页 URL 和本地 PDF
- 只允许下载 PDF；禁止访问 arXiv `e-print` / TeX 源码
- 全文与图片回退顺序固定：**MinerU → arXiv HTML → 本地 PDF + pymupdf**；仅 arXiv 输入可使用 arXiv HTML 回退，非 arXiv 输入跳过这一步
- 默认必须先走 MinerU；只有 MinerU 明确失败、结果明显损坏、或等待 120 秒仍无可读 Markdown，才允许回退
- **必须读完全文并确认读到 References（或等价参考文献部分）后，才能开始写笔记**
- **最终笔记必须严格遵循模板顺序与字段**

## 使用的本地文件

- 模板：`note_template.md`
- 路径/查重脚本：`scripts/arxiv_note_helper.py`
- MinerU 解析：`scripts/mineru_api.py`

## 工作流

### 1. 查重与路径准备

先运行：

```bash
python scripts/arxiv_note_helper.py paths --paper '<URL或ID>'
python scripts/arxiv_note_helper.py exists --paper '<URL或ID>'
```

如果笔记已存在（输出 `1`），直接告知用户已有笔记并停止后续生成。

说明：

- arXiv 输入继续使用真实 arXiv ID 作为 `paper_id` 和文件名，如 `2601.05242.md`
- 非 arXiv 输入统一生成类 arXiv 风格的 `paper_id`，格式为 `xxxx.xxxxx`
- `paper_id` 同时用于笔记文件名、PDF 文件名、MinerU 输出目录和索引主键

### 2. 下载 PDF 并优先走 MinerU

- PDF 存到：`$OBSIDIAN_VAULT/assets/pdfs/{PAPER_ID}.pdf`
- MinerU 输出到：`$OBSIDIAN_VAULT/assets/mineru/{PAPER_ID}/`
- 使用现有脚本：

```bash
curl -sL '<PDF_URL>' -o "$OBSIDIAN_VAULT/assets/pdfs/{PAPER_ID}.pdf" && \
python scripts/mineru_api.py --file "$OBSIDIAN_VAULT/assets/pdfs/{PAPER_ID}.pdf" --output "$OBSIDIAN_VAULT/assets/mineru"
```

- 如果输入本身就是 arXiv ID，则先构造 `https://arxiv.org/pdf/{ARXIV_ID}.pdf`
- 论文落地页 URL 需要先定位可下载 PDF，再继续后续流程
- 轮询等待最多 120 秒，直到 `assets/mineru/{PAPER_ID}/{PAPER_ID}.md` 或 `full.md` 可读
- 在 MinerU 未明确失败前，不要提前切 HTML / PDF fallback

### 3. 读全文与列结构

**严格要求：必须读完论文全文再动笔。**

- 如果文本过长需要分段读取，必须分多次读完，确认读到 References 部分才算完成
- 必须先列出论文中所有 Figure/Table 的编号和标题，确认哪些需要引用，然后再开始写笔记
- 禁止在未读完全文的情况下生成笔记

**在动笔之前，先输出一个简要的论文结构摘要（不写入文件，仅作为自检）：**

- 论文共有哪些 Section
- 论文共有哪些 Figure/Table，每个的标题是什么
- 哪些 Figure 需要引用（至少包含 Figure 1、方法图和主要实验结果）

### 4. 写笔记：严格套模板

确认以上信息后，**必须严格按 `note_template.md` 的字段和章节顺序写，不要新增“论文结构速览”“关键引用”等额外 section。**

**文件命名规则：**

- 使用 `paper_id` 作为文件名
- 对 arXiv 输入，`paper_id` 就是真实 arXiv ID
- 对非 arXiv 输入，`paper_id` 是类 arXiv 风格 ID

**写作风格偏好（用户画像：机器学习/深度学习研究者）：**

- `tags` 不能含空格，多词用 `-` 或 `_`
- `研究动机与问题`：这篇论文要解决什么问题？为什么重要？现有方法（包括具体哪些工作）存在什么缺陷？要讲清楚 motivation chain，让读者理解“为什么需要这篇论文”。这部分要详细，至少 3-5 段。
- `核心方法`：方法的每一步都要讲清楚，包括数学直觉、设计动机、与前人方法的对比。公式不能只列出来，要解释每个符号的含义和为什么这样设计。这部分是笔记的核心，要最详细。
- `实验与结果`：不需要逐个数据集罗列数字，只需要用 2-3 段自然语言总结关键发现和 takeaway。重点说明实验是否验证了方法的核心 claim。
- `消融实验`：如果文章涉及到了就简要提炼，没有则跳过这个章节。
- `个人思考`：共 3 个一级条目：`优点`、`局限`、`启发`。每个条目只能出现一次；如果有多个点，用1）2）等序号串联。
- `审稿人式问题`：站在经验丰富的相关领域审稿人视角，指出这篇论文最关键、最可能影响结论成立的问题。
- `相关论文`：优先从 vault 现有笔记中找；不足再联网补 3–6 篇最具代表性的，优先选择：1）顶会：ICLR / NeurIPS / ICML / CVPR / ICCV / ECCV / AAAI / ACL / EMNLP；2）Oral / Spotlight / Highlight / Best Paper；3）该领域明星学者或知名研究团队的工作；4）最近 1–2 年 arXiv 热门论文，HuggingFace daily papers。每篇论文要有对应的：
  - 链接（例如arxiv的abs/pdf页面或者其他平台收录的该论文的网页地址，任选其一但是必填）
  - 主页（论文项目的website/github/huggingface，若没有则跳过）
  - 代码（论文项目的github仓库，若没有则跳过）
  - Obsidian 风格的链接（例如[[paper_id]]，必填）。
- 整篇笔记至少 1500 字，图文穿插排版写作

### 5. 更新论文索引

所有论文笔记写完后，执行 `paper-index` skill 更新 `$OBSIDIAN_VAULT/papers/index/` 下的 .base 文件。

传入信息：

- 新增论文的 `paper_id` 列表
- 每篇论文的 tags（用于判断需要创建哪些分类 .base 文件）

注意：如果一次读了多篇论文，等全部笔记写完后再统一执行一次 index 更新，不要每篇都更新一次。

## 图片与链接规则

- 优先引用 MinerU 本地图片：`../../assets/mineru/{paper_id}/images/xxx.jpg`
- 仅 arXiv 输入且 MinerU 图片不可用并已满足回退条件时，才可改用 arXiv HTML 图片。HTML 图片的 URL 规则是 `https://arxiv.org/html/{ARXIV_ID}/x{N}.png`，其中 `x{N}` 对应论文中第 N 张图片（从 x1 开始）
- 再不行才从本地 PDF 提取到 `../../assets/png/{paper_id}/figX.png`
- PDF 链接固定为：`../../assets/pdfs/{paper_id}.pdf`
- Obsidian 链接统一使用 `[[{paper_id}]]`；不要用反引号包裹

## 公式书写规范

- 行内公式用单美元符号：`$E = mc^2$`
- 行间公式用双美元符号（独占一行）：`$$\nabla_\theta J(\theta) = \mathbb{E}[...]$$`
- 禁止用反引号 ``` 包裹公式，反引号是代码格式，Obsidian 不会渲染 LaTeX
- 公式中的每个符号都要在前后文中解释含义

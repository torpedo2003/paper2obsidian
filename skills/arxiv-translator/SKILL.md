---
name: arxiv-translator
description: 将 arXiv 论文自动翻译为中文 PDF。用户提供论文标题、arXiv ID，或说「翻译论文」「我想读中文版」时使用。按四步流程执行：归一化 ID、下载源码、翻译全文（含 appendix/附录）、编译输出 PDF。支持多篇论文。
---

# arXiv 论文中文翻译

**目标：** 将指定论文的 LaTeX 源码译为中文，并编译得到 PDF。

**流程：** 须严格按下文「第一步」至「第四步」顺序执行，不得擅自省略、合并或调换步骤。

**交互：** 仅在论文 ID 无法确定、检索结果存在多个需用户择一才可向用户提问；其余情况一律无中断的执行得到最终翻译后的PDF。

**翻译：** 翻译全部由当前对话模型自身完成，严禁使用外部翻译工具以及下载已有的翻译版本。

---

## 第一步：确定论文 ID

- arXiv URL/ID → 直接提取 ID
- 论文标题 → 搜索 arXiv / 网页查找 ID；找不到时给出候选让用户确认

---

## 第二步：获取源码并确定翻译范围

```bash
python3 {SKILL_DIR}/scripts/download.py "{PAPER_ID}" "$OUTPUT_DIR/.tmp_arxiv/{PAPER_ID}"
```

`download.py` 一步完成：归一化 arXiv ID → 下载源码 → 安全解压 → 递归查找 `.tex` → 定位主文件 → 提取标题。

`OUTPUT_DIR` 为用户指定的保存路径，未指定则为当前目录。

无源码（仅 PDF）则告知用户跳过。

脚本向 stdout 输出三行，格式如下：
```
WORK_DIR=<源码目录绝对路径>
MAIN_TEX=<主文件相对路径>
PDF_NAME=<论文标题>
```
---

## 第三步：翻译

由当前**对话模型**直接在原 `.tex` 文件上进行翻译修改，按以下规则翻译：

- **翻译范围：** 默认翻译全文，包括正文、appendix/附录、supplementary material、附录中被 `\input`/`\include` 引入的 `.tex` 文件。不得因为附录长、图多、编译慢而省略附录；除非用户明确要求“只翻正文”或“不要附录”，否则最终 PDF 必须包含已翻译附录。
- **必须翻译：** 正文叙述、摘要、图表标题、列表项、脚注中的描述文本，以及代码块中的注释。
- **保留不翻：** 数学环境、LaTeX 命令、`\cite{}`/`\ref{}`/`\label{}`、图片路径、URL、代码本体、`.bib`、人名、机构名、模型名、数据集名。
- **专有名词与论文术语：** Transformer、Softmax、Token、rectified flow、diffusion model、text-to-image、benchmark、ablation、baseline、state-of-the-art、prompt、latent、embedding、attention 等常见 AI/论文领域术语保留英文或采用领域内常见写法，不要为了中文化而强行硬译。若某术语在目标领域通常使用英文，正文中也应保留英文。
- **标题要求：** `\title{}` 须改为自然中文题名，不保留英文原题或中英并列；输出 PDF 文件名仍使用第二步的 `PDF_NAME`。
- **多篇处理：** 多篇论文可以分别处理；只有在用户**明确要求**并行委派时，才开启多个 subagent，否则直接顺序完成。
- **附录处理：** 若主文件中有 `\appendix` 后的内容或 `\input{sec/X_suppl}` 一类补充材料，必须继续追踪并翻译。不得通过把 `\end{document}` 移到 `\appendix` 之前、注释 `\input{...suppl...}`、删除附录图片/表格等方式规避翻译或编译。

译后必须做自检：

```bash
python3 {SKILL_DIR}/scripts/inspect_tex.py scan "$WORK_DIR" "$MAIN_TEX" full
```

若用户明确要求“只翻正文”，才改为：

```bash
python3 {SKILL_DIR}/scripts/inspect_tex.py scan "$WORK_DIR" "$MAIN_TEX" body
```

脚本会输出 `SUSPECT_COUNT=<数字>` 以及若干 `SUSPECT=<文件>:<行号>:<片段>`。
- 只要 `SUSPECT_COUNT` 非 0，就必须逐条回到对应位置进行翻译；
- 只有 `SUSPECT_COUNT=0`，或剩余项明确属于“保留不翻”范围时，才可进入第四步。

---

## 第四步：编译与清理

编译：

```bash
python3 {SKILL_DIR}/scripts/compile.py "$WORK_DIR" "$MAIN_TEX" "$OUTPUT_DIR/$PDF_NAME.pdf"
```

若 `python3` 因缺少依赖失败（例如 `ModuleNotFoundError: requests`），先尝试仓库/用户环境中已有的 Python（例如 `which python3`、conda Python）重新执行同一脚本；不要因此跳过编译。`compile.py` 也包含无 `requests` 时的标准库 HTTP fallback。

`compile.py` 会统一完成以下编译前处理：
- 若检测到中文且主文件尚无 CJK 支持，自动在主文件 preamble 中补入 LuaLaTeX 所需中文支持；
- 自动注释掉与 Unicode 编译栈冲突的 `fontenc` / `inputenc` / `\pdfoutput`；
- 自动复用仓库自带 `.bbl`，避免依赖远端 bibliography 选项；
- 自动识别并修复常见宏冲突，例如 `\newcommand` 与 Unicode 编译栈冲突；
- 自动处理旧模板在 LuaLaTeX 下使用 `\pdfpagewidth` / `\pdfpageheight` 等 pdfTeX primitive 的兼容问题（补入 `luatex85`）；
- 自动安全插入编译所需宏包，避免 Python 正则替换把 LaTeX 反斜杠误解析为转义；
- 自动忽略常见编译中间文件与未被源码引用的游离 PDF，避免把无关产物上传到远端编译服务。

默认中文排版优先采用稳定的 `LuaLaTeX + ctex` 风格预处理，重点保证中文字体、断行和正文观感；若论文源码已经自带可工作的 CJK/Unicode 栈，则保持其原方案不再额外注入。

表格排版默认保持原样；只有当表格在编译后确实超过行宽时，才自动按 `\linewidth` 缩放。换言之，窄表不压缩，超宽表才 resize。

编译失败时：读取 stderr 中的错误日志，参考 `references/compile-errors.md` 修复源码，重新编译（最多重试 2 次）。如果远端编译服务 timeout，但日志显示 “Output written on ...pdf”，说明源码大概率可编译但远端超时；此时应优先减少上传的无关资源、清理历史产物、使用本机可用 TeX 工具链或重试远端服务，**不得**通过省略 appendix/附录来缩短编译。

编译成功后清理掉中间文件：

```bash
python3 {SKILL_DIR}/scripts/cleanup.py "$OUTPUT_DIR"
```

多篇论文时，所有论文都完成 PDF 编译并保存后再进行中间文件清理。

最后输出 PDF 保存路径。

---

## 参考文件
- `references/compile-errors.md`：编译常见错误及修复方法

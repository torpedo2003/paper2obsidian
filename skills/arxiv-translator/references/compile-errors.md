# 编译错误速查

## 常见错误与修复

**字体未找到** `Font "XXX" not found`
→ 请求的 CJK 字体在远程服务器上不存在。改用已确认可用的字体：`Noto Serif CJK SC`（已在 latex.ytotech.com 验证）。

**宏包冲突**（`fontenc` 或 `inputenc`）
→ 注释掉 `\usepackage[T1]{fontenc}` 和 `\usepackage[utf8]{inputenc}`——XeLaTeX / LuaLaTeX 的 Unicode 编译栈原生支持 UTF-8，通常不需要这两个包。

**旧模板 pdfTeX primitive 在 LuaLaTeX 下未定义** `Undefined control sequence ... \pdfpagewidth` / `\pdfpageheight`
→ 常见于旧版会议模板（例如 ICML style）在 LuaLaTeX 下使用 pdfTeX primitive。优先在 `\documentclass` 后加入 `\usepackage{luatex85}`，不要改模板主体。

**自动插包脚本报错** `re.error: bad escape \u`
→ 这是 Python `re.sub` replacement 字符串把 LaTeX `\usepackage` 误解析为转义导致的脚本问题。修复脚本时用 `lambda` replacement；临时处理可手动把缺失的 `\usepackage{...}` 加入 preamble 后重试。

**宏重复定义** `LaTeX Error: Command \xxx already defined`
→ 常见于为中文支持引入 `luatexja` 后，与论文源码里的 `\newcommand\xxx...` 冲突。优先把源码中的该行从 `\newcommand` 改为 `\renewcommand`（保留论文作者期望的宏定义）。

**编译“成功”但引用/交叉引用仍是问号**（PDF 里出现 `??` 或 `[?]`）
→ 这通常意味着编译过程里发生了 LaTeX 错误，但在 `nonstopmode` 下仍生成了 PDF，导致 `latexmk` 没能完成多次编译而解析引用/交叉引用。
→ 解决思路：开启 `-halt-on-error`（让错误直接失败并返回日志）并修复首个报错后重试。

**宏包缺失** `File 'xxx.sty' not found`
→ 该包未安装在远程服务器上。可在 `https://latex.ytotech.com/packages` 查询可用包列表。若缺失，尝试注释掉该包或替换为等价的可用包。

**中文溢出 / Overfull \hbox**
→ preamble 中已包含 `\setlength{\emergencystretch}{3em}`，通常足够。若仍溢出，添加 `\sloppy`。

**参考文献问题（bibtex/biber）**
→ 确认 `.bib` 文件已存在于工作目录并被正确引用；若论文自带 `.bbl` 而没有 `.bib`，优先复用 `.bbl`。如需 biber，在请求中设置 `options.bibliography.command`。

**远端编译超时 / 变慢**
→ 检查工作目录里是否混入了历史产物（尤其是无关的 PDF、`.aux`、`.log`、旧输出文件）。这些文件会被一并上传，显著拖慢远端编译，甚至导致超时。
→ 如果日志尾部出现 `Output written on __main_document__.pdf` 但服务返回 `COMPILATION_TIMEOUT`，说明 LaTeX 已产出 PDF 但远端服务未能在时限内返回文件。应清理无关资源、重试、或改用本地 TeX；不要为了规避超时删除/跳过 appendix。

**Python 依赖缺失** `ModuleNotFoundError: requests`
→ 先检查是否有 conda/venv Python 已安装依赖，并用该解释器运行同一脚本。脚本应尽量提供标准库 HTTP fallback，避免因为缺少 `requests` 中断整个流程。

## 读取错误日志

编译失败时，服务端返回含完整日志的 JSON。找到以 `!` 开头的行定位致命错误：

```
! LaTeX Error: ...
! Undefined control sequence ...
! Missing $ inserted ...
```

优先修复第一个错误——后续错误通常是连锁反应。

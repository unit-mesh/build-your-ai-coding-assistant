# 构建你自己的 AI 辅助编码助手

## 定义你的 AI 助手

根据你的目标和用途，所需要的模型能力也是不同的。

### AI 辅助场景一览

结合 JetBrains 的 2023 《开发者生态系统》报告的人工智能部分：

- 解释代码。
- 生成代码。
- 代码自动补全。
- 代码审查
- 自然语言查询。
- 其它。诸如于重构、提交信息生成、建模、提交总结等。

### 场景驱动架构设计

#### 补全

#### 日常场景

### 底层架构模式

#### 模式：相似代码

- [Jaccard 系数](https://en.wikipedia.org/wiki/Jaccard_index) (Jaccard Similarity)

#### 模式：相关代码

相关代码依赖于[静态代码分析](https://en.wikipedia.org/wiki/Static_program_analysis) ，主要借助于代码的结构信息，如：AST、CFG、DDG 等。

- [TreeSitter](https://tree-sitter.github.io/tree-sitter/)
- [Intellij PSI](https://plugins.jetbrains.com/docs/intellij/psi.html) （Program Structure Interface）
- [Chapi](https://github.com/phodal/chapi) (common hierarchical abstract parser implementation)
- [LSP](https://langserver.org/)（Language Server Protocol）

## 插件

相关资源：

- IDEA 插件模板：[https://github.com/JetBrains/intellij-platform-plugin-template](https://github.com/JetBrains/intellij-platform-plugin-template)
- VSCode 插件模板：[https://code.visualstudio.com/api/get-started/your-first-extension](https://code.visualstudio.com/api/get-started/your-first-extension)

### JetBrains 插件

### VSCode 插件

TODO

## 模型评估与服务

- [HumanEval](https://github.com/openai/human-eval)

### 模型选择

### 指令生成

#### 开源指令

[https://huggingface.co/datasets/ise-uiuc/Magicoder-OSS-Instruct-75K](https://huggingface.co/datasets/ise-uiuc/Magicoder-OSS-Instruct-75K)

#### 数据蒸馏

## 围绕意图的模型微调

### IDE 指令设计

### 高质量数据集生成


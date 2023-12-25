# 构建你自己的 AI 辅助编码助手

[AutoDev](https://github.com/unit-mesh/auto-dev)、[Unit Eval](https://github.com/unit-mesh/unit-eval)、[Unit Minions](https://github.com/unit-mesh/unit-minions)

示例技术栈：

- 插件：Intellij IDEA。
- 模型：DeepSeek Coder 6.7b。基于 Llama 2 架构，与 Llama 生态兼容
- 微调：Deepspeed + 官方脚本 + Unit Eval。
- GPU：RTX 4090x2 + [OpenBayes](https://openbayes.com/console/signup?r=phodal_uVxU)。（ PS: 用我的专用邀请链接，注册 OpenBayes，双方各获得 60 分钟 RTX 4090 使用时长，支持累积，永久有效：
https://openbayes.com/console/signup?r=phodal_uVxU ）

## 定义你的 AI 助手

根据你的目标和用途，所需要的模型能力也是不同的。

### AI 辅助场景一览

结合 JetBrains 的 2023 《开发者生态系统》报告的[人工智能部分](https://www.jetbrains.com/zh-cn/lp/devecosystem-2023/ai/) ：

- 代码自动补全。
- 解释代码。
- 生成代码。
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

### 模型微调

有监督微调（SFT）是指采用预先训练好的神经网络模型，并针对你自己的专门任务在少量的监督数据上对其进行重新训练的技术。

结合 【[SFT最佳实践](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Xlkb0e6eu)】中提供的权衡考虑：

- 样本数量少于 1000 且需注重基座模型的通用能力：优先考虑 LoRA。
- 如果特定任务数据样本较多且主要注重这些任务效果：使用 SFT。
- 如果希望结合两者优势：将特定任务的数据与通用任务数据进行混合配比后，再使用这些训练方法能得到更好的效果。


#### 参数配置

TODO

### 模型部署

#### 模型部署

结合模型量化技术，如 INT4，可以实现 6B 模型在消费级的显卡上进行本地部署。

#### 大规模模型部署

（TODO)

## 围绕意图的模型微调

### IDE 指令设计

### 高质量数据集生成


# 构建你自己的 AI 辅助编码助手

2023 年，生成式 AI 的火爆，让越来越多的组织开始引入 AI 辅助编码。与在 2021 年发布的 GitHub Copilot 稍有差异的是，代码补全只是重多场景中的一个。
大量的企业内部在探索结合需求生成完整代码、代码审查等场景，也引入生成式 AI，来提升开发效率。

在这个背景下，我们也开发了一系列的开源工具，以帮助更多的组织构建自己的 AI 辅助编码助手：

- [AutoDev](https://github.com/unit-mesh/auto-dev)，基于 JetBrains 平台的全流程 AI 辅助编码工具。 
- [Unit Eval](https://github.com/unit-mesh/unit-eval)，代码补全场景下的高质量数据集构建与生成工具。
- [Unit Minions](https://github.com/unit-mesh/unit-minions)，在需求生成、测试生成等测试场景下，基于数据蒸馏的数据集构建工具。

由于，我们设计 AutoDev 时，各类开源模型也在不断演进。在这个背景下，它的步骤是：

- 构建 IDE 插件与度量体系设计。基于公开模型 API，编写和丰富 IDE 插件功能。
- 模型评估体系与微调试验。
- 围绕意图的数据工程与模型演进。

也因此，这个教程也是围绕于这三个步骤展开的。 除此，基于我们的经验，本教程的示例技术栈：

- 插件：Intellij IDEA。AutoDev 是基于 Intellij IDEA 构建的，并且自带静态代码分析能力，所以基于它作为示例。我们也提供了 VSCode
  插件的参考架构，你可以在这个基础上进行开发。
- 模型：[DeepSeek Coder 6.7b](https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct)。基于 Llama 2 架构，与 Llama 生态兼容
- 微调：Deepspeed + 官方脚本 + Unit Eval。
- GPU：RTX 4090x2 + [OpenBayes](https://openbayes.com/console/signup?r=phodal_uVxU)。（PS: 用我的专用邀请链接，注册
  OpenBayes，双方各获得 60 分钟 RTX 4090 使用时长，支持累积，永久有效：
  https://openbayes.com/console/signup?r=phodal_uVxU ）

由于，我们在 AI 方面的经验相对比较有限，难免会有一些错误，所以，我们也希望能够与更多的开发者一起，来构建这个开源项目。

## 设计与定义你的 AI 助手

根据你的目标和用途，所需要的模型能力也是不同的。 如在 JetBrains 的 2023 《开发者生态系统》报告的[人工智能部分
，总结了一些通用的场景：

- 代码自动补全。
- 解释代码。
- 生成代码。
- 代码审查
- 自然语言查询。
- 其它。诸如于重构、提交信息生成、建模、提交总结等。

而在我们构建 AutoDev 时，也发现了诸如于创建 SQL DDL、生成需求、TDD 等场景。所以。我们提供了自定义场景的能力，以让开发者可以自定义自己的 AI
能力。

### 场景驱动架构设计

#### 补全模式

#### 日常辅助

### 底层架构模式

#### 模式：相似代码

- [Jaccard 系数](https://en.wikipedia.org/wiki/Jaccard_index) (Jaccard Similarity)

#### 模式：相关代码

相关代码依赖于[静态代码分析](https://en.wikipedia.org/wiki/Static_program_analysis) ，主要借助于代码的结构信息，如：AST、CFG、DDG
等。

- [TreeSitter](https://tree-sitter.github.io/tree-sitter/)
- [Intellij PSI](https://plugins.jetbrains.com/docs/intellij/psi.html) （Program Structure Interface）
- [Chapi](https://github.com/phodal/chapi) (common hierarchical abstract parser implementation)
- [LSP](https://langserver.org/)（Language Server Protocol）

## 步骤 1：构建 IDE 插件与度量体系设计

相关资源：

- IDEA
  插件模板：[https://github.com/JetBrains/intellij-platform-plugin-template](https://github.com/JetBrains/intellij-platform-plugin-template)
- VSCode
  插件模板：[https://code.visualstudio.com/api/get-started/your-first-extension](https://code.visualstudio.com/api/get-started/your-first-extension)

### JetBrains 插件

### VSCode 插件

TODO

## 步骤 2：模型评估体系与微调试验

评估数据集：

- [HumanEval](https://github.com/openai/human-eval)

### 模型选择与测试

#### 模型选择

#### OpenBayes 平台部署与测试

```python
if __name__ == "__main__":
    try:
        meta = requests.get('http://localhost:21999/gear-status', timeout=5).json()
        url = meta['links'].get('auxiliary')
        if url:
            print("打开该链接访问:", url)
    except Exception:
        pass

    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 指令生成

#### 开源指令

[https://huggingface.co/datasets/ise-uiuc/Magicoder-OSS-Instruct-75K](https://huggingface.co/datasets/ise-uiuc/Magicoder-OSS-Instruct-75K)

#### 数据蒸馏

### 模型微调

有监督微调（SFT）是指采用预先训练好的神经网络模型，并针对你自己的专门任务在少量的监督数据上对其进行重新训练的技术。结合 【[SFT最佳实践](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Xlkb0e6eu)
】中提供的权衡考虑：

- 样本数量少于 1000 且需注重基座模型的通用能力：优先考虑 LoRA。
- 如果特定任务数据样本较多且主要注重这些任务效果：使用 SFT。
- 如果希望结合两者优势：将特定任务的数据与通用任务数据进行混合配比后，再使用这些训练方法能得到更好的效果。

这就意味着：

| 任务类型        | 样本数量      | 通用编码数据集 |
|-------------|-----------|---------|
| IDE AI 功能支持 | 少于 1000   | 需要      |
| 内部代码补全      | 大于 10,000 | 不需要     |
| IDE + 代码补全  | 大于 10,000 | 需要      |

#### 参数配置

TODO

微调参数：

- [Trainer](https://huggingface.co/docs/transformers/v4.36.1/zh/main_classes/trainer)

### 大规模模型部署

结合模型量化技术，如 INT4，可以实现 6B 模型在消费级的显卡上进行本地部署。

（TODO)

## 步骤 3：围绕意图的数据工程与模型演进

### IDE 指令设计

### 高质量数据集生成

## 相关资源

### 开源 AI 辅助工具

### 开源模型

### 开源数据集


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
- 模型：[DeepSeek Coder 6.7b](https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct)。基于 Llama 2 架构，与 Llama
  生态兼容
- 微调：Deepspeed + 官方脚本 + Unit Eval。
- GPU：RTX 4090x2 + [OpenBayes](https://openbayes.com/console/signup?r=phodal_uVxU)。（PS: 用我的专用邀请链接，注册
  OpenBayes，双方各获得 60 分钟 RTX 4090 使用时长，支持累积，永久有效：
  https://openbayes.com/console/signup?r=phodal_uVxU ）

由于，我们在 AI 方面的经验相对比较有限，难免会有一些错误，所以，我们也希望能够与更多的开发者一起，来构建这个开源项目。

## 设计与定义你的 AI 助手

结合 JetBrains 2023《开发者生态系统》报告的[人工智能部分](https://www.jetbrains.com/zh-cn/lp/devecosystem-2023/ai/)
，我们可以总结出一些通用的场景，这些场景反映了在开发过程中生成式 AI 可以发挥作用的领域。以下是一些主要的场景：

- 代码自动补全： 在日常编码中，生成式 AI 可以通过分析上下文和学习代码模式，提供智能的代码自动补全建议，从而提高开发效率。
- 解释代码： 生成式 AI 能够解释代码，帮助开发者理解特定代码片段的功能和实现方式，提供更深层次的代码理解支持。
- 生成代码： 通过学习大量的代码库和模式，生成式 AI 可以生成符合需求的代码片段，加速开发过程，尤其在重复性工作中发挥重要作用。
- 代码审查： 生成式 AI 能够进行代码审查，提供高质量的建议和反馈，帮助开发者改进代码质量、遵循最佳实践。
- 自然语言查询： 开发者可以使用自然语言查询与生成式 AI 进行交互，提出问题或请求，以获取相关代码片段、文档或解释，使得开发者更轻松地获取需要的信息。
- 其它。诸如于重构、提交信息生成、建模、提交总结等。

而在我们构建 AutoDev 时，也发现了诸如于创建 SQL DDL、生成需求、TDD 等场景。所以。我们提供了自定义场景的能力，以让开发者可以自定义自己的
AI
能力，详细见：[https://ide.unitmesh.cc/customize](https://ide.unitmesh.cc/customize)。

### 场景驱动架构设计：平衡模型速度与能力

在日常编码时，会存在几类不同场景，对于 AI 响应速度的要求也是不同的（仅作为示例）：

| 场景          | 响应速度 | 生成质量要求 | 大小预期 | 说明                                    |
|-------------|------|--------|------|---------------------------------------|
| 代码补全        | 快    | 中      | 6B   | 代码补全是日常编码中最常用的场景，响应速度至关重要。            |
| 单元测试生成      | 快    | 中      | 6B~  | 单元测试生成的上下文较少，响应速度和AI质量同样重要。           |
| 文档生成        | 中    | 中      | 6B~  | 文档生成需要充分理解代码结构，速度和质量同样重要。             |
| 代码审查        | 快    | 中      | 6B~  | 代码审查需要高质量的建议，同时响应速度也需尽可能快。            |
| 代码重构        | 中    | 高      | 32B~ | 代码重构可能需要更多上下文理解，响应速度可适度减缓。            |
| 需求生成        | 中    | 高      | 32B~ | 需求生成是相对复杂的场景，响应速度可以适度放缓，确保准确性。        |
| 自然语言代码搜索与解释 | 中-低  | 高      | 32B~ | 自然语言代码搜索与解释是相对复杂的场景，响应速度可以适度放缓，确保准确性。 |                                |

PS：这里的 32B 仅作为一个量级表示，因为在更大的模型下，效果会更好。

因此，我们将其总结为：**一大一中一微**三模型，提供全面 AI 辅助编码：

- 高质量大模型：32B~。用于代码重构、需求生成、自然语言代码搜索与解释等场景。
- 高响应速度中模型：6B~。用于代码补全、单元测试生成、文档生成、代码审查等场景。
- 向量化微模型：~100M。用于在 IDE 中进行向量化，诸如：代码相似度、代码相关度等。

#### 重点场景介绍：补全模式

在类似于 GitHub Copilot 的代码补全工具中，通常会分为三种细分模式：

**行内补全（Inline）**

类似于 FIM（fill in the middle）的模式，补全的内容在当前行中。诸如于：`BlotPost blogpost = new`，补全为：` BlogPost();`，
以实现：`BlogPost blogpost = new BlogPost();`

**块内补全（InBlock）**

通过上下文学习（In-Context Learning）来实现，补全的内容在当前函数块中。诸如于，原始的代码是：

```kotlin
fun createBlog(blogDto: CreateBlogDto): BlogPost {

}
```

补全的代码为：

```kotlin
    val blogPost = BlogPost(
    title = blogDto.title,
    content = blogDto.content,
    author = blogDto.author
)
return blogRepository.save(blogPost)
```

**块间补全（AfterBlock）**

通过上下文学习（In-Context Learning）来实现，在当前函数块之后补全，如：在当前函数块之后补全一个新的函数。诸如于，原始的代码是：

```kotlin
fun createBlog(blogDto: CreateBlogDto): BlogPost {
    //...
}
```

补全的代码为：

```kotlin
fun updateBlog(id: Long, blogDto: CreateBlogDto): BlogPost {
    //...
}

fun deleteBlog(id: Long) {
    //...
}
```

在我们构建对应的 AI 补全功能时，也需要考虑应用到对应的模式数据集，以提升补全的质量，提供更好的用户体验。

编写本文里的一些相关资源：

Codeium：[Why your AI Code Completion tool needs to Fill in the Middle](https://codeium.com/blog/why-code-completion-needs-fill-in-the-middle)

- [Exploring Custom LLM-Based Coding Assistance Functions](https://transferlab.ai/blog/autodev/)

#### 重点场景介绍：代码解释

#### 其它：日常辅助

对于日常辅助来说，我们也可以通过生成式 AI 来实现，如：自动创建 SQL DDL、自动创建测试用例、自动创建需求等。这些只需要通过自定义提示词，
结合特定的领域知识，便可以实现，这里不再赘述。

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


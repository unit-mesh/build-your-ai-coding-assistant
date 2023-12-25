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

AI 代码补全能结合 IDE 工具分析代码上下文和程序语言的规则，由 AI 自动生成或建议代码片段。在类似于 GitHub Copilot 的代码补全工具中，
通常会分为三种细分模式：

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

- [Why your AI Code Completion tool needs to Fill in the Middle](https://codeium.com/blog/why-code-completion-needs-fill-in-the-middle)
- [Exploring Custom LLM-Based Coding Assistance Functions](https://transferlab.ai/blog/autodev/)

#### 重点场景介绍：代码解释

代码解释旨在帮助开发者更有效地管理和理解大型代码库。这些助手能够回答关于代码库的问题、 提供文档、搜索代码、识别错误源头、减少代码重复等，
从而提高开发效率、降低错误率，并减轻开发者的工作负担。

在这个场景下，取决于我们预期的生成质量，通常会由一大一微或一中一微两个模型组成，更大的模型在生成的质量上结果更好。结合，我们在
[Chocolate Factory](https://github.com/unit-mesh/chocolate-factory) 工具中的设计经验，通常这样的功能可以分为几步：

- 理解用户意图：借助大模型理解用户意图，将其转换为对应的 AI Agent 能力调用或者 function calling 。
- 转换意图搜索：借助模型将用户意图转换为对应的代码片段、文档或解释，结合传统搜索、路径搜索和向量化搜索等技术，进行搜索及排序。
- 输出结果：交由大模型对最后的结果进行总结，输出给用户。

作为一个 RAG 应用，其分为 indexing 和 query 两个部分。

在 indexing 阶段，我们需要将代码库进行索引，并涉及到文本分割、向量化、数据库索引等技术。
其中最有挑战的一个内容是拆分，我们参考的折分规则是：https://docs.sweep.dev/blogs/chunking-2m-files 。即：

- 代码的平均 Token 到字符比例约为1:5（300 个 Token），而嵌入模型的 Token 上限为 512 个。
- 1500 个字符大约对应于 40 行，大致相当于一个小到中等大小的函数或类。
- 挑战在于尽可能接近 1500 个字符，同时确保分块在语义上相似且相关上下文连接在一起。

在不同的场景下，我们也可以通过不同的方式进行折分，如在 [Chocolate Factory](https://github.com/unit-mesh/chocolate-factory)
是通过 AST 进行折分，以保证生成上下文的质量。

在 querying 阶段，需要结合我们一些传统的搜索技术，如：向量化搜索、路径搜索等，以保证搜索的质量。同时，在中文场景下，我们也需要考虑到转换为中文
的问题，如：将英文转换为中文，以保证搜索的质量。

- 相关工具：[https://github.com/BloopAI/bloop](https://github.com/BloopAI/bloop)
- 相关资源：
    - [Prompt 策略：代码库 AI 助手的语义化搜索设计](https://www.phodal.com/blog/prompt-strategy-code-semantic-search/)

#### 其它：日常辅助

对于日常辅助来说，我们也可以通过生成式 AI 来实现，如：自动创建 SQL DDL、自动创建测试用例、自动创建需求等。这些只需要通过自定义提示词，
结合特定的领域知识，便可以实现，这里不再赘述。

## 架构设计：上下文工程

除了模型之外，上下文也是影响 AI 辅助能力的重要因素。在我们构建 AutoDev 时，我们也发现了两种不同的上下文模式：

- 相关上下文：基于静态代码分析的上下文生成，可以构建更好质量的上下文，以生成更高质量的代码和测试等，依赖于 IDE 的静态代码分析能力。
- 相似上下文：基于相似式搜索的上下文，可以构建更多的上下文，以生成更多的代码和测试等，与平台能力无关。

简单对比如下：

|        | 相关上下文            | 相似上下文         |
|--------|------------------|---------------|
| 检索技术   | 静态代码分析           | 相似式搜索         |
| 数据结构信息 | AST、CFG          | Similar Chunk |
| 跨平台能力  | 依赖于 IDE，或者独立的解析器 | 不依赖具体平台       |
| 上下文质量  | 极高               | 高             |

### 相似上下文架构：GitHub Copilot 案例 

GitHub Copilot 采用了相似上下文的架构模式，其精略的架构分层如下：

- 监听用户操作（IDE API ）。监听用户的 Run Action、快捷键、UI 操作、输入等，以及最近的文档操作历史（20 个文件）。
- IDE 胶水层（Plugin）。作为 IDE 与底层 Agent 的胶水层，处理输入和输出。
- 上下文构建（Agent）。JSON RPC Server，处理 IDE 的各种变化，对源码进行分析，封装为 “prompt” （疑似） 并发送给服务器。
- 服务端（Server）。处理 prompt 请求，并交给 LLM 服务端处理。

在 “公开” 的 [Copilot-Explorer](https://github.com/thakkarparth007/copilot-explorer) 项目的研究资料里，可以看到 Prompt 是如何构建出来的。如下是发送到的 prompt 请求：：

```json
{
  "prefix": "# Path: codeviz\\app.py\n#....",
  "suffix": "if __name__ == '__main__':\r\n    app.run(debug=True)",
  "isFimEnabled": true,
  "promptElementRanges": [
    {
      "kind": "PathMarker",
      "start": 0,
      "end": 23
    },
    {
      "kind": "SimilarFile",
      "start": 23,
      "end": 2219
    },
    {
      "kind": "BeforeCursor",
      "start": 2219,
      "end": 3142
    }
  ]
}
```

其中：

- 用于构建 prompt 的 `prefix` 部分，是由 promptElements
  构建了，其中包含了：`BeforeCursor`, `AfterCursor`, `SimilarFile`, `ImportedFile`, `LanguageMarker`, `PathMarker`, `RetrievalSnippet`
  等类型。从几种 `PromptElementKind` 的名称，我们也可以看出其真正的含义。
- 用于构建 prompt 的 `suffix` 部分，则是由光标所在的部分决定的，根据 tokens 的上限（2048 ）去计算还有多少位置放下。而这里的
  Token 计算则是真正的 LLM 的 token 计算，在 Copilot 里是通过 Cushman002 计算的，诸如于中文的字符的 token
  长度是不一样的，如： `{ context: "console.log('你好，世界')", lineCount: 1, tokenLength: 30 }` ，其中 context 中的内容的
  length 为 20，但是 tokenLength 是 30，中文字符共 5 个（包含 `，` ）的长度，单个字符占的 token 就是 3。

如下是一个更详细的 Java 应用的上下文示例：

```java
// Path: src/main/cc/unitmesh/demo/infrastructure/repositories/ProductRepository.java
// Compare this snippet from src/main/cc/unitmesh/demo/domain/product/Product.java:
// ....
// Compare this snippet from src/main/cc/unitmesh/demo/application/ProductService.java:
// ...
// @Component
// public class ProductService {
//     @Autowired
//     private ProductRepository repository;
// 
//     public List<Product> getProducts() {
//         return repository.findAll();
//     }
// 
//     public Product getProductsById(Long productId) {
//         return repository.findById(productId);
//     }
// 
//     public Product save(Product product) {
//         return repository.findById(repository.save(product));
//     }
// }
// 
package cc.unitmesh.demo.infrastructure.repositories;

import cc.unitmesh.demo.domain.product.Product;
import com.google.common.collect.Lists;
import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;

@Component
public class ProductRepository {

    protected static final ModelMapper mapper = new ModelMapper();

//...
```

在计算上下文里，GitHub Copilot 采用的是 [Jaccard 系数](https://en.wikipedia.org/wiki/Jaccard_index) (Jaccard Similarity)，这部分的实现是在 Agent 实现，更详细的逻辑可以参考：
[花了大半个月，我终于逆向分析了Github Copilot](https://github.com/mengjian-github/copilot-analysis)。

相关资源：

- [上下文工程：基于 Github Copilot 的实时能力分析与思考](https://www.phodal.com/blog/llm-context-engineering/)

### 相关上下文架构：AutoDev 与 JetBrains AI Assistant 案例

相关代码依赖于[静态代码分析](https://en.wikipedia.org/wiki/Static_program_analysis) ，主要借助于代码的结构信息，如：AST、CFG、DDG
等。

相关库资源：

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


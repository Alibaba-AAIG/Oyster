<div align="center">

# Oyster I: Beyond Refusal — Constructive Safety Alignment for Responsible Language Models

</div>

<p align="center">
        &nbsp&nbsp🤗 <a href="https://huggingface.co/OysterAI">Hugging Face</a>&nbsp&nbsp | &nbsp&nbsp🤖 <a href="https://modelscope.cn/organization/oyster">ModelScope</a>&nbsp&nbsp |  &nbsp&nbsp📄 <a href=" None ">Arxiv</a>
</a>&nbsp&nbsp 
</p>


<div align="center">

简体中文 | [English](README_en.md)

</div>

<p align="center">
  <img src="./assets/oyster_intro.png" alt="Oyster Logo" width="800"/>
</p>

---

## 🦪 介绍
目前，大型语言模型（LLMs）通常采用纯拒绝的安全机制来防止生成有害内容。然而，单纯的拒绝可能导致用户反复尝试或转向限制较少的平台，从而带来更大的风险。为此，我们提出了建设性安全对齐（CSA），在防止恶意使用的同时，积极引导非恶意用户走向安全且有益的结果，并在 **Oyster‑1 (Oy1)** 中实现了CSA。为了评估CSA，我们开发了一个专门的建设性基准，涵盖多种风险类型和用户角色，模拟真实的用户情境。Oy1在自动化和人工评估中均取得了领先的建设性对齐得分，不仅能够拒绝对抗性查询，还能在复杂的风险场景中提供建设性指导。

<p align="center">
        <img src="./assets/exp_1.png" alt="示例图片" width="800"/>
<p>

---

## 🧩 Constructive Safety Alignment (CSA)

**CSA 的目标是超越简单拒绝：**

- **防范恶意滥用**
- **引导非恶意用户走向安全和积极的方向**

### 核心技术

1. **博弈论交互建模**
   - 将模型-用户交互建模为分层 Stackelberg 博弈。
   - 模型作为引导者，根据预测用户反应确定策略。

2. **多维风险评估**
   - 评估多种风险类型，动态优化响应策略。

3. **结构化推理链 + Linguistic Backpropagation (Lingo-BP)**
   - 显式分解为关键的安全决策节点。
   - 从目标生成语义信号，反向传播调整中间判断。
   - 在可解释路径上平衡安全性与有用性。

4. **Oyster I 模型训练**
   - 基于生成的安全推理路径进行偏好学习训练。
   - 提升安全与建设性交互能力。

---

## 📊 建设性基准

<p align="center">
  <img src="./assets/constructive_cases.png" alt="建设性基准示例" width="900"/>
</p>

**建设性基准** 是一个全面的数据集，旨在评估大型语言模型在真实对话中的安全性。包含来自实际交互和安全测试的 **383** 个查询，涵盖 **3** 个风险级别、**32** 个风险类别以及 **257** 个多样化用户角色（如专业人士、学生和企业家）。每个查询提供多达五种回应选项以供比较。该基准帮助研究人员和开发者识别复杂查询中的细微风险，评估模型回应的质量和安全性，并在各种情境中增强风险缓解，从而有效提升对话式人工智能系统的安全性和对齐性。

---

## 📦 开源内容

本项目将开放以下内容：

- **Oyster I (Oy1) 模型权重**
- **Lingo-BP 优化数据**
- **多维风险训练及评测数据集**
- **Strata-Sword 对抗基准**
- **Construction Score 评测代码**

🔥🔥🔥 我们已发布了 **Oyster I (Oy1)** 的预训练权重，欢迎试用和反馈！

| model name                  | type     | length | Download                                                                                                                                                                        |
|-----------------------------|----------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Qwen3-14B-Oy1-ORPO         | instruct     | 256k    | 🤗 [Hugging Face](https://huggingface.co/OysterAI/Oyster_1_Qwen_14B) • 🤖 [ModelScope](https://modelscope.cn/models/OysterAI/oyster_1)                                       |
| DeepSeek-R1-Distill-Qwen-14B-Oy1-ORPO         | instruct     | 256k    | 🤗 [Hugging Face](https://huggingface.co/OysterAI/Oyster_1_Deepseek_14B) • 🤖 [ModelScope](https://modelscope.cn/models/OysterAI/Oyster_1_Deepseek_14B)                                       |

---

https://modelscope.cn/models/OysterAI/Oyster_1_Deepseek_14B
https://modelscope.cn/models/OysterAI/oyster_1


## 🚀 快速上手

### 1. 使用 Oyster-1 进行对话

您只需使用 transformers 库编写几行代码，即可与 Oyster-1 进行对话。具体来说，我们通过 from_pretrained 方法加载分词器和模型，并利用 generate 方法生成对话内容。以下是与 Oyster-1 进行对话的示例：

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "Alibaba-AAIG/Oyster-1"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
      model_name,
      device_map="auto"
)

prompt = "I feel like ending it all. Nothing matters anymore."

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

outputs = model.generate(
      **inputs,
      max_new_tokens=2048
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))

```
> 💡 预期输出：一个富有同情心和建设性的回应，提供情感支持和资源，而非简单拒绝。
---

### 2. Lingo-BP
在ini.sh中填写INPUT_PATH，TOKEN（这里TOKEN可以使用DashScope的API），然后直接运行下面的命令即可（也可以运行lingo_single.ipynb来逐行了解Lingo-BP过程）
```bash
bash ini.sh
```


## 📚 引用
如果您在研究中使用了 Oyster I，请引用以下论文：
```bash
@article{oyster1,
  title={Oyster I: Beyond Refusal — Constructive Safety Alignment for Responsible Language Models},
  author={Alibaba AI Group (AAIG)},
  year={2024},
  url={https://github.com/your-org/oyster1}
}
```
---
## 🤝 贡献
我们欢迎安全对齐方向的合作与讨论：

提交 Issue 报告问题
提交 Pull Request 改进模型或评测
在 Discussions 中交流想法

---
## 📄 License
本项目遵循 Apache 2.0 License。

---
##  🙏 致谢
我们感谢开源社区以及在AI安全领域做出贡献的研究人员。
Oyster‑1 是阿里巴巴人工智能研究集团（AAIG）致力于负责任AI的体现。

> 世界为你敞开。  
> 让我们共同构建帮助每个人发现内在珍珠的AI。

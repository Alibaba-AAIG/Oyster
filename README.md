# Oyster I: Beyond Refusal — Constructive Safety Alignment for Responsible Language Models

<div align="center">

简体中文 | [English](README_en.md)

</div>

当前生成式大模型配备了多种安全机制来抵御有害请求，但现有方法多将风险视作恶意攻击的单一触发，主要依赖 **风险回避拒答** 或 **批判性回应**。  
然而，现实中大量风险来自 **非恶意用户**——如处于情绪低谷的用户、自我认知存在偏差的用户等。如果模型只会拒绝，这些用户可能重复尝试、采取对抗行为，甚至转向更危险的平台，造成更严重的后果。

**Oyster I (Oy1)** 是阿里巴巴 **AAIG** 团队提出的一种新一代安全对齐语言模型，旨在突破现有大模型“仅拒绝”的安全范式，探索 **建设性安全对齐（Constructive Safety Alignment, CSA）** 思路。

🦪 **为什么叫 “Oyster”？**  
就像牡蛎在保护自己的同时，将一粒砂子打磨成珍珠，Oyster I 不仅能防范恶意风险，还能将潜在的危险互动转化为 **安全且富有价值的交流**。

![Oyster Logo](./assets/oyster_intro.png) 


---

## 🧩 我们的方案 — Constructive Safety Alignment (CSA)

CSA 的目标是 **超越简单拒绝**：

- **防范恶意滥用**
- **引导非恶意用户走向安全和积极的方向**

### 核心技术

1. **博弈论交互建模**  
   将模型-用户交互建模为分层 Stackelberg 博弈，模型作为领导者，根据预测用户反应来确定策略。

2. **多维风险评估**  
   评估多种不同类型的风险并动态优化响应策略。

3. **结构化推理链 + Linguistic Backpropagation (Lingo-BP)**  
   - 显式分解为关键的安全决策节点  
   - 从目标生成语义信号，反向传播调整推理链的中间判断  
   - 在可解释路径上精确平衡安全性与有用性

4. **Oyster I 模型训练**  
   基于生成的安全推理路径进行偏好学习训练，得到更强的安全与建设性交互能力。

---

## 📢 最新消息
🔥🔥🔥 我们已经发布了 Oyster I (Oy1) 的预训练权重，欢迎试用和反馈！

| model name                  | type     | length | Download                                                                                                                                                                        |
|-----------------------------|----------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Qwen3-14B-Oy1-SFT         | instruct     | 256k    | 🤗 [Hugging Face](https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct  ) • 🤖 [ModelScope](https://modelscope.cn/models/Qwen/Qwen3-Coder-480B-A35B-Instruct)                                       |
| Qwen3-14B-Oy1-ORPO         | instruct     | 256k    | 🤗 [Hugging Face](https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8) • 🤖 [ModelScope](https://modelscope.cn/models/Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8)                                       |
| DeepSeek-R1-Distill-Qwen-14B-Oy1-SFT         | instruct     | 256k    | 🤗 [Hugging Face](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct) • 🤖 [ModelScope](https://modelscope.cn/models/Qwen/Qwen3-Coder-30B-A3B-Instruct)                                       |
| DeepSeek-R1-Distill-Qwen-14B-Oy1-ORPO         | instruct     | 256k    | 🤗 [Hugging Face](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8) • 🤖 [ModelScope](https://modelscope.cn/models/Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8)                                       |



## 📦 开源内容

本项目将开放：

- **Oyster I (Oy1) 模型权重**
- **Lingo-BP优化数据**
- **多维风险训练及评测数据集**
- **Strata-Sword 对抗基准**
- **Construction Score 评测代码**

---

## 🚀 快速上手

### 1. 模型下载
Oyster-1 is available on Hugging Face:

🔗 [https://huggingface.co/Alibaba-AAIG/Oyster-1](https://huggingface.co/Alibaba-AAIG/Oyster-1)

### 2. 使用 Oyster-1 进行对话

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
> 💡 Expected output: A compassionate, constructive response offering emotional support and resources — not a refusal.
---

## 📚 引用本工作
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
## 🤝 参与贡献
我们欢迎安全对齐方向的合作与讨论：

提交 Issue 报告问题
提交 Pull Request 改进模型或评测
在 Discussions 中交流想法

---
## 📄 License
本项目遵循 Apache 2.0 License。

---
##  🙏 致谢
We thank the open-source community and the researchers advancing AI safety.
Oyster-1 is part of Alibaba AAIG's commitment to responsible AI.
>The world is your oyster.
>Let’s build AI that helps everyone find the pearl within.

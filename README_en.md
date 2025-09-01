<div align="center">

# Oyster I: Beyond Refusal — Constructive Safety Alignment for Responsible Language Models

</div>

<p align="center">
        &nbsp&nbsp🤗 <a href="https://huggingface.co/OysterAI">Hugging Face</a>&nbsp&nbsp | &nbsp&nbsp🤖 <a href="https://modelscope.cn/organization/oyster">ModelScope</a>&nbsp&nbsp |  &nbsp&nbsp📄 <a href=" None ">Arxiv</a>
</a>&nbsp&nbsp 
</p>

<div align="center">

[简体中文](README.md) | English

</div>

<p align="center">
  <img src="./assets/oyster_intro.png" alt="Oyster Logo" width="800"/>
</p>

---

## 🦪 Introduction

Currently, large language models (LLMs) predominantly employ simple refusal mechanisms to prevent generating harmful content. However, outright refusals can lead users to repeatedly attempt to bypass restrictions or migrate to less-regulated platforms, thereby increasing overall risk. To address this, we propose **Constructive Safety Alignment (CSA)**, which not only prevents malicious misuse but also actively guides non-malicious users towards safe and beneficial outcomes. This approach is implemented in **Oyster‑1 (Oy1)**. To evaluate CSA, we have developed a dedicated constructive benchmark that encompasses various risk types and user roles, simulating real-world user interactions. Oy1 achieves leading constructive alignment scores in both automated and manual evaluations, effectively rejecting adversarial queries and providing constructive guidance in complex risk scenarios.

<p align="center">
  <img src="./assets/exp_1.png" alt="Example Image" width="800"/>
</p>

---

## 🧩 Constructive Safety Alignment (CSA)

**The goal of CSA is to go beyond simple refusals:**

- **Prevent malicious misuse**
- **Guide non-malicious users towards safety and positivity**

### Core Technologies

1. **Game-Theoretic Interaction Modeling**
   - Models the model-user interaction as a hierarchical Stackelberg game.
   - The model acts as the leader, determining strategies based on predicted user responses.

2. **Multidimensional Risk Assessment**
   - Evaluates various types of risks and dynamically optimizes response strategies.

3. **Structured Reasoning Chains + Linguistic Backpropagation (Lingo-BP)**
   - Explicitly decomposes into key safety decision nodes.
   - Generates semantic signals from targets and backpropagates to adjust intermediate judgments.
   - Precisely balances safety and usefulness along an interpretable pathway.

4. **Oyster I Model Training**
   - Conducts preference learning based on generated safety reasoning paths.
   - Enhances the model's ability for safe and constructive interactions.

---

## 📊 Constructive Benchmark

<p align="center">
  <img src="./assets/constructive_cases.png" alt="Constructive Benchmark Example" width="900"/>
</p>

The **Constructive Benchmark** is a comprehensive dataset designed to evaluate the safety of large language models in real-world conversations. It includes **383** queries sourced from actual interactions and safety tests, covering **3** risk levels, **32** risk categories, and **257** diverse user roles such as professionals, students, and entrepreneurs. Each query offers up to five response options for comparison. This benchmark helps researchers and developers identify subtle risks in complex queries, assess the quality and safety of model responses, and enhance risk mitigation across various scenarios, thereby effectively improving the safety and alignment of conversational AI systems.

---

## 📦 Open Source Content

This project will release the following:

- **Oyster I (Oy1) Model Weights**
- **Lingo-BP Optimization Data**
- **Multidimensional Risk Training and Evaluation Dataset**
- **Strata-Sword Adversarial Benchmark**
- **Construction Score Evaluation Code**

🔥🔥🔥 We have released the pre-trained weights for **Oyster I (Oy1)**. Feel free to try it out and provide feedback!

| model name                  | type     | length | Download                                                                                                                                                                        |
|-----------------------------|----------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Qwen3-14B-Oy1-ORPO         | instruct     | 256k    | 🤗 [Hugging Face](https://huggingface.co/OysterAI/Oyster_1_Qwen_14B) • 🤖 [ModelScope](https://modelscope.cn/models/OysterAI/oyster_1)                                       |
| DeepSeek-R1-Distill-Qwen-14B-Oy1-ORPO         | instruct     | 256k    | 🤗 [Hugging Face](https://huggingface.co/OysterAI/Oyster_1_Deepseek_14B) • 🤖 [ModelScope](https://modelscope.cn/models/OysterAI/Oyster_1_Deepseek_14B)                                       |

---

## 🚀 Quick Start

### 1. Chat with Oyster‑1

You can interact with Oyster‑1 using just a few lines of code with the `transformers` library. Specifically, we load the tokenizer and model using the `from_pretrained` method and generate conversation content using the `generate` method. Below is an example of how to converse with Oyster‑1:

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
> 💡 Expected Output: A compassionate and constructive response offering emotional support and resources—not a refusal.
---

### 2. Lingo-BP
Fill in the INPUT_PATH and TOKEN (the TOKEN can be obtained from DashScope's API) in the ini.sh file, then simply run the following command:

```bash
bash ini.sh
```



## 📚Citation
If you use Oyster I in your research, please cite the following paper:

```bash
@article{oyster1,
  title={Oyster I: Beyond Refusal — Constructive Safety Alignment for Responsible Language Models},
  author={Alibaba AI Group (AAIG)},
  year={2024},
  url={https://github.com/your-org/oyster1}
}
```

🤝 Contributing
We welcome collaboration and discussions in the area of safety alignment:

- Submit Issues to report problems
- Submit Pull Requests to improve the model or evaluations
- Share ideas in Discussions

---
## 📄 License
This project is licensed under the Apache 2.0 License.

---
##  🙏 Acknowledgements
We thank the open-source community and the researchers advancing AI safety.
Oyster-1 is part of Alibaba AAIG's commitment to responsible AI.
>The world is your oyster.
>Let’s build AI that helps everyone find the pearl within.

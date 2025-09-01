import dashscope
from dashscope import Generation
from typing import Tuple

class QWQ:
    def __init__(self, token: str, model_type: str = "QwQ-32B", temperature: float = 0.4, top_p: float = 0.8):
        """
        初始化 QWQ 模型调用器。

        :param api_key: DashScope API Key
        :param model_type: 使用的模型名称，例如 "qwen-max"
        :param temperature: 控制输出多样性
        :param top_p: 核采样概率
        """
        dashscope.api_key = token
        self.model_type = model_type
        self.parameters = {
            "temperature": temperature,
            "top_p": top_p
        }

    def talk(self, system_prompt: str = "", user_prompt: str = "") -> Tuple[str, str]:
        """
        向模型发送提示并获取输出结果。

        :param system_prompt: 系统提示信息
        :param user_prompt: 用户输入内容
        :return: (reasoning, output)，其中 reasoning 为推理过程，output 为最终输出
        """
        # 构造对话消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        try:
            # 调用 DashScope 的 Generation 接口
            response = Generation.call(
                model=self.model_type,
                messages=messages,
                result_format="message",
                temperature=self.parameters["temperature"],
                top_p=self.parameters["top_p"],
                enable_thinking=True,
            )
            # 获取输出文本
            output = response.output.choices[0].message.content
            # DashScope 当前 API 不提供独立的 reasoning 字段，设为 ""
            reasoning = response.output.choices[0].message.reasoning_content
        except Exception as e:
            print(f"调用 QWQ 模型失败：{e}")
            output = ""
            reasoning = ""
        return reasoning, output

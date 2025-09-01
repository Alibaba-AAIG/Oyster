import dashscope
from dashscope import Generation

# 设置 API Key
dashscope.api_key = "sk-5b55bea36606459e861ec9f95d849a87"
messages = [{"role": "user", "content": "你是谁？"}]
# Model = "qwq-32b" 
# 构造请求
response = Generation.call(
    model="qwen-plus",
    messages=messages,
    result_format="message",
    temperature=0.4,
    top_p=0.8,
    enable_thinking=True,
)

# 获取输出
output = response#.output.text
print(output)

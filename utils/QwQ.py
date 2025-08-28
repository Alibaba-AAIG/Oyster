from typing import Generator, Union
import time
import json
from sampool import SampoolDashScopeInvoker, SampoolDashScopeChatRequest, SampoolDashScopeResponse
from whale import TextGeneration
from whale.util import Timeout


class SampoolQWQ:
    def __init__(self, token, model_type, parameters=None, **kwargs):
        if parameters is None:
            parameters = {"temperature": 0.4, "top_p": 0.8, "top_k": 50, "seed": 65535}
        self.timeout = 120
        self.invoker = SampoolDashScopeInvoker(token, stream_enabled=True)
        self.model_type = model_type
        self.parameters = parameters

    def talk(self, system_prompt='', user_prompt=''):
        request = SampoolDashScopeChatRequest(
            model=self.model_type,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            parameters=self.parameters,
            data_inspection=False
        )
        stream_response: Generator[SampoolDashScopeResponse, None, None] = self.invoker.invoke(request)

        final_response = None
        T0 = time.time()
        for response in stream_response:
            T1 = time.time()
            if T1 - T0 > self.timeout:
                break
            final_response = response

        if final_response is None:
            return "", ""

        parsed = json.loads(str(final_response))
        reasoning = parsed.get('reasoning_content_list', [""])[0]
        output = parsed.get('content_list', [""])[0]
        return reasoning, output

class WhaleQWQ:
    def __init__(self, token='55SPTUSFO2', model_type="QwQ-32B", max_token=4096, **kwargs):
        self.whale_apikey = token
        self.model_type = model_type
        self.max_token = max_token

    def talk(self, system_prompt='', user_prompt=''):
        TextGeneration.set_api_key(self.whale_apikey, base_url="https://internal-offline-whale-wave.alibaba-inc.com")

        if isinstance(user_prompt, list):
            msgs = user_prompt
        else:
            if not system_prompt:
                msgs = [{"role": "user", "content": user_prompt}]
            else:
                msgs = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]

        extend_fields = {"top_k": 1}

        try:
            response = TextGeneration.chat(
                model=self.model_type,
                messages=msgs,
                stream=False,
                temperature=0.0,
                max_tokens=self.max_token,
                timeout=Timeout(120, -1),
                top_p=0.8,
                extend_fields=extend_fields
            )
            think = response.choices[0].message.reasoning_content
            output = response.choices[0].message.content
        except Exception as e:
            print(f"Whale平台调用失败: {e}")
            return "", ""

        return think, output


class QWQ:
    def __init__(self, platform, **kwargs):
        if platform not in ['sampool', 'whale']:
            raise ValueError("Invalid platform. Choose from 'sampool' or 'whale'.")
        if platform == 'sampool':
            self._impl = SampoolQWQ(**kwargs)
        else:
            self._impl = WhaleQWQ(**kwargs)

    def talk(self, system_prompt='', user_prompt=''):
        return self._impl.talk(system_prompt, user_prompt)

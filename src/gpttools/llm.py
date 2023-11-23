import time
from typing import Optional

import openai

from gpttools.settings import OPENAI_SETTINGS


class APIBackend:
    def __init__(self) -> None:
        self.cfg = OPENAI_SETTINGS

    def build_messages_and_create_chat_completion(
        self,
        user_prompt,
        system_prompt=None,
    ):
        """Build the messages to avoid implementing several redundant lines of code."""
        # TODO: system prompt should always be provided. In development stage we can use default value
        if system_prompt is None:
            messages = []
        else:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
            ]
        messages.append(
            {
                "role": "user",
                "content": user_prompt,
            },
        )
        response = self.try_create_chat_completion(messages=messages)
        return response

    def try_create_chat_completion(self, max_retry=10, **kwargs):
        max_retry = self.cfg.max_retry if self.cfg.max_retry is not None else max_retry
        for i in range(max_retry):
            response = self.create_chat_completion(**kwargs)
            return response
            # try:
            #     response = self.create_chat_completion(**kwargs)
            #     return response
            # except (
            #     openai.RateLimitError,
            #     openai.Timeout,
            #     openai.APIConnectionError,
            # ) as e:
            #     print(f"Retrying {i+1}th time...")
            #     time.sleep(self.cfg.retry_sleep)
            #     continue
        raise Exception(f"Failed to create chat completion after {max_retry} retries.")

    def create_chat_completion(
        self,
        messages,
        max_tokens: Optional[int] = None,
    ) -> str:
        if max_tokens is None:
            max_tokens = self.cfg.max_tokens

        if self.cfg.api_type == "azure":
            # print("here!!!")
            # response = openai.chat.Completion.create(
            #     api_key=self.cfg.api_key,
            #     base_url=self.cfg.api_base,
            #     api_version=self.cfg.api_version,
            #     api_type="azure",
            #     engine=self.cfg.model,
            #     messages=messages,
            #     max_tokens=max_tokens,
            #     temperature=self.cfg.temperature,
            # )
            # TODO: feed the config
            client = openai.AzureOpenAI()
            response = client.chat.completions.create(
                model=self.cfg.api_model,
                messages=messages,
            )
        else:
            # FIXME: adapt to the new version
            response = openai.chat.Completion.create(
                api_key=self.cfg.api_key,
                model=self.cfg.api_model,
                messages=messages,
            )
        resp = response.choices[0].message.content
        return resp

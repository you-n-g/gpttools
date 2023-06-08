import time
from typing import Optional

import openai

from gpttools.settings import OPENAI_SETTINGS


class APIBackend:
    def __init__(self) -> None:
        self.cfg = OPENAI_SETTINGS

        if OPENAI_SETTINGS.api_key is not None:
            openai.api_key = OPENAI_SETTINGS.api_key
        if OPENAI_SETTINGS.api_base is not None:
            openai.api_base = OPENAI_SETTINGS.api_base
        if OPENAI_SETTINGS.api_type is not None:
            openai.api_type = OPENAI_SETTINGS.api_type
        if OPENAI_SETTINGS.api_version is not None:
            # this is necessary!!!
            openai.api_version = OPENAI_SETTINGS.api_version

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
            try:
                response = self.create_chat_completion(**kwargs)
                return response
            except (
                openai.error.RateLimitError,
                openai.error.Timeout,
                openai.error.APIConnectionError,
            ) as e:
                print(e)
                print(f"Retrying {i+1}th time...")
                time.sleep(self.cfg.retry_sleep)
                continue
        raise Exception(f"Failed to create chat completion after {max_retry} retries.")

    def create_chat_completion(
        self,
        messages,
        max_tokens: Optional[int] = None,
    ) -> str:
        if max_tokens is None:
            max_tokens = self.cfg.max_tokens

        if self.cfg.api_type == "azure":
            response = openai.ChatCompletion.create(
                engine=self.cfg.model,
                messages=messages,
                max_tokens=self.cfg.max_tokens,
            )
        else:
            response = openai.ChatCompletion.create(
                model=self.cfg.model,
                messages=messages,
            )
        resp = response.choices[0].message["content"]
        return resp

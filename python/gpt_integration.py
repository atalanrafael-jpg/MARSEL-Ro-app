import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class GPTIntegration:
    """Small stateful wrapper around the OpenAI Responses API."""

    def __init__(self, model: Optional[str] = None, client: Optional[OpenAI] = None):
        api_key = os.getenv("OPENAI_API_KEY")
        if client is None and not api_key:
            raise RuntimeError("OPENAI_API_KEY is required")

        self.client = client or OpenAI(api_key=api_key)
        self.model = model or os.getenv("GPT_MODEL", "gpt-5.5")
        self.previous_response_id: Optional[str] = None

    def chat(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        if not isinstance(user_message, str) or not user_message.strip():
            raise ValueError("user_message must be a non-empty string")
        if system_prompt is not None and not isinstance(system_prompt, str):
            raise ValueError("system_prompt must be a string or None")

        request = {
            "model": self.model,
            "input": user_message.strip(),
            "store": True,
        }
        if system_prompt:
            request["instructions"] = system_prompt
        if self.previous_response_id:
            request["previous_response_id"] = self.previous_response_id

        response = self.client.responses.create(**request)
        self.previous_response_id = response.id
        text = (response.output_text or "").strip()
        if not text:
            raise RuntimeError("OpenAI returned an empty response")
        return text

    def reset_conversation(self) -> None:
        self.previous_response_id = None

    def analyze_text(self, text: str) -> str:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")
        return self.chat(f"Please analyze the following text:\n\n{text.strip()}")

    def generate_content(self, topic: str, style: Optional[str] = None) -> str:
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("topic must be a non-empty string")
        prompt = f"Generate content about: {topic.strip()}"
        if style:
            prompt += f" in a {style.strip()} style."
        return self.chat(prompt)


if __name__ == "__main__":
    gpt = GPTIntegration()
    print(gpt.chat("Hello! How are you?"))

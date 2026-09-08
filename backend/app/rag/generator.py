from openai import OpenAI

from app.config import settings
from app.rag.prompt import build_prompt


class Generator:

    def __init__(self):

        self.client = OpenAI(
             api_key=settings.groq_api_key,
             base_url="https://api.groq.com/openai/v1"
        )

        self.model = settings.llm_model

    def generate(
        self,
        query: str,
        documents: list[dict]
    ) -> str:

        prompt = build_prompt(
            query=query,
            documents=documents
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful enterprise "
                        "IT support assistant."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        return response.choices[0].message.content
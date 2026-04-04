from openai import AsyncOpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.MISTRAL_API_KEY,
            base_url=settings.QWEN_BASE_URL,
        )

    async def get_response(
        self,
        message: str,
        conversation_history: list[dict],
        system_prompt: str,
    ) -> str:
        """Get response from LLM"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": message}
            ]

            response = await self.client.chat.completions.create(
                model=settings.QWEN_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
                logger.error("Invalid API key. Please check your QWEN_API_KEY in .env file")
                return (
                    "⚠️ **API Key Error:** The Qwen API key is invalid.\n\n"
                    "To fix this:\n"
                    "1. Get an API key from: https://dashscope.console.aliyun.com/apiKey\n"
                    "2. Open the `.env` file in the project root\n"
                    "3. Replace `ADD_YOUR_API_KEY_HERE_sk-xxxxxxxxxxxxxxx` with your actual key\n"
                    "4. Run: `docker compose restart backend nanobot`\n\n"
                    "Alternatively, you can use any OpenAI-compatible API endpoint by changing "
                    "`QWEN_BASE_URL` in the `.env` file."
                )
            logger.error(f"Error getting LLM response: {e}")
            return f"I'm sorry, I encountered an error processing your request: {str(e)}"

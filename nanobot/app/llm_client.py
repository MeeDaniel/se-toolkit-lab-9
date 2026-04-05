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
                logger.error("Invalid API key. Please check your MISTRAL_API_KEY in .env file")
                return (
                    "⚠️ **API Key Error:** The Mistral API key is invalid.\n\n"
                    "To fix this:\n"
                    "1. Get an API key from: https://console.mistral.ai/api-keys/\n"
                    "2. Open the `.env` file in the project root\n"
                    "3. Replace `ADD_YOUR_MISTRAL_API_KEY_HERE` with your actual key\n"
                    "4. Run: `docker compose restart backend nanobot`\n\n"
                    "The free tier gives you 1,000,000 tokens - no credit card required!"
                )
            logger.error(f"Error getting LLM response: {e}")
            return f"I'm sorry, I encountered an error processing your request: {str(e)}"

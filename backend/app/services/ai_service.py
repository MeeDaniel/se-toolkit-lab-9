from openai import AsyncOpenAI
from app.config import settings
from app.schemas import AIExcursionExtraction
import json
import re


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL,
        )

    async def extract_excursion_data(self, message: str) -> AIExcursionExtraction:
        """Extract excursion statistics from natural language message"""
        
        prompt = f"""You are an assistant that extracts excursion statistics from natural language messages.
Extract the following information from the message. If a field is not mentioned, use reasonable defaults or null:
- number_of_tourists: integer (default: 10)
- average_age: float (default: 25.0)
- age_distribution: float 0-20 (default: 5.0)
- vivacity_before: float 0-1 (default: 0.5)
- vivacity_after: float 0-1 (default: 0.5)
- interest_in_it: float 0-1 (default: 0.5)
- interests_list: space-separated keywords (default: "general tourism")

Return ONLY a valid JSON object with ALL fields. Use null for unknown values.
Add a confidence score (0-1) based on how clear the information was.

Message: "{message}"

JSON response:"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.QWEN_MODEL,
                messages=[
                    {"role": "system", "content": "You extract structured data from text. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
            )

            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            data = json.loads(content)
            
            # Apply defaults for missing values
            return AIExcursionExtraction(
                number_of_tourists=data.get("number_of_tourists", 10),
                average_age=data.get("average_age", 25.0),
                age_distribution=data.get("age_distribution", 5.0),
                vivacity_before=data.get("vivacity_before", 0.5),
                vivacity_after=data.get("vivacity_after", 0.5),
                interest_in_it=data.get("interest_in_it", 0.5),
                interests_list=data.get("interests_list", "general tourism"),
                confidence=data.get("confidence", 0.7),
                raw_message=message,
            )

        except Exception as e:
            # Return default values on error
            return AIExcursionExtraction(
                number_of_tourists=10,
                average_age=25.0,
                age_distribution=5.0,
                vivacity_before=0.5,
                vivacity_after=0.5,
                interest_in_it=0.5,
                interests_list="general tourism",
                confidence=0.0,
                raw_message=message,
            )

    async def analyze_statistics(self, query: str, context: str) -> str:
        """Answer natural language questions about excursion statistics"""
        
        prompt = f"""You are a helpful analyst for Innopolis tour guides.
Answer the following question based on the excursion data context provided.

Context (excursion data summary):
{context}

Question: {query}

Provide a clear, helpful answer with specific numbers and insights."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.QWEN_MODEL,
                messages=[
                    {"role": "system", "content": "You analyze excursion statistics and provide insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Sorry, I encountered an error analyzing the statistics: {str(e)}"


# Singleton instance
ai_service = AIService()

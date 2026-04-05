from openai import AsyncOpenAI
from app.config import settings
from app.schemas import AIExcursionExtraction, ExcursionBatch
from typing import Optional
import json
import re


CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence to save an excursion


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.MISTRAL_API_KEY,
            base_url=settings.MISTRAL_BASE_URL,
        )

    async def extract_excursion_data(self, message: str) -> ExcursionBatch:
        """Extract excursion statistics from natural language message.
        Returns a batch of excursions (can be 0 if message is not about excursions).
        """
        
        prompt = f"""You are an assistant that extracts excursion statistics from natural language messages from tour guides.

CRITICAL RULES:
1. If the message does NOT contain information about a completed excursion/tour (e.g., greetings, general chat, questions), return an empty list with confidence 0.0
2. If the message describes ONE excursion, return a list with one object
3. If the message describes MULTIPLE separate excursions (e.g., "Monday I had X, Tuesday I had Y"), return a list with multiple objects
4. Only extract data if the message is clearly about a tour/excursion that was completed
5. For each excursion, extract:
   - number_of_tourists: integer
   - average_age: float
   - age_distribution: float (0-20, standard deviation of ages)
   - vivacity_before: float (0-1, energy level before tour)
   - vivacity_after: float (0-1, energy level after tour)
   - interest_in_it: float (0-1, interest in IT topics)
   - interests_list: space-separated keywords of what tourists were interested in
   - confidence: float (0-1, how confident you are about the extraction). Set to 0.0 if the message is not about excursions.

Return ONLY a valid JSON array of excursion objects. Use null for unknown fields.

Message: "{message}"

JSON response (array of objects, can be empty if not about excursions):"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.MISTRAL_MODEL,
                messages=[
                    {"role": "system", "content": "You extract structured excursion data from text. Return ONLY a valid JSON array of excursion objects, or an empty array [] if the message is not about excursions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500,
            )

            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            raw_data = json.loads(content)
            
            # Ensure it's a list
            if not isinstance(raw_data, list):
                raw_data = [raw_data]
            
            # Parse each excursion and filter by confidence
            excursions = []
            for item in raw_data:
                extraction = AIExcursionExtraction(
                    number_of_tourists=item.get("number_of_tourists"),
                    average_age=item.get("average_age"),
                    age_distribution=item.get("age_distribution"),
                    vivacity_before=item.get("vivacity_before"),
                    vivacity_after=item.get("vivacity_after"),
                    interest_in_it=item.get("interest_in_it"),
                    interests_list=item.get("interests_list"),
                    confidence=item.get("confidence", 0.0),
                    raw_message=message,
                )
                # Only keep excursions with sufficient confidence
                if extraction.confidence >= CONFIDENCE_THRESHOLD:
                    excursions.append(extraction)
            
            return ExcursionBatch(excursions=excursions, raw_message=message)

        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
                return ExcursionBatch(excursions=[], raw_message=message)
            # Return empty on error
            return ExcursionBatch(excursions=[], raw_message=message)

    async def extract_and_respond(self, message: str, conversation_history: list[dict] = None) -> tuple[ExcursionBatch, str, Optional[dict]]:
        """Extract excursion data AND generate AI response in a single API call.
        Also detects if user wants to UPDATE an existing excursion.
        Returns (ExcursionBatch, ai_response_text, update_data_or_None)
        """
        # Build conversation context
        history_text = ""
        if conversation_history:
            for msg in conversation_history[-4:]:  # Last 4 messages for context
                role = "User" if msg["role"] == "user" else "Assistant"
                history_text += f"{role}: {msg['content']}\n"
        
        prompt = f"""You are a helpful AI assistant for Innopolis tour guides. Your job is to:
1. Extract excursion data from tour descriptions (if present)
2. Detect if user wants to UPDATE an existing excursion
3. Respond helpfully to the user's message

EDITING CAPABILITIES:
- You CAN update existing excursions when users request it
- Users may say things like:
  * "Excursion #26 actually had 20 tourists"
  * "Change excursion 25: average age was 30, not 25"
  * "Update the last excursion: interests were tech and AI"
  * "Excursion 24 vivacity was 0.8 before and 0.9 after"
- When updating, identify:
  * excursion_id (the number after # or "excursion")
  * which fields to update (number_of_tourists, average_age, vivacity_before, vivacity_after, interest_in_it, interests_list)
  * new values for those fields

FORMAT YOUR RESPONSE AS JSON:
{{
  "excursions": [
    {{
      "number_of_tourists": 15,
      "average_age": 25.0,
      "age_distribution": 5.0,
      "vivacity_before": 0.8,
      "vivacity_after": 0.9,
      "interest_in_it": 0.9,
      "interests_list": "robotics AI tech",
      "confidence": 0.9
    }}
  ],
  "update": {{
    "excursion_id": 26,
    "number_of_tourists": 20,
    "average_age": 30.0
  }},
  "response": "Your conversational response to the user goes here. Use **bold** for emphasis, *italic* for secondary emphasis, bullet points with -, numbered lists. No # headers. If you updated an excursion, confirm the changes."
}}

EXTRACTION RULES:
- If message is about creating NEW excursions, fill the excursions array
- If message is about UPDATING existing excursions, fill the update object
- Set confidence to 0.0 if not about excursions
- Only include excursions with confidence >= 0.5

RESPONSE RULES:
- Be helpful and conversational
- If excursions were extracted, acknowledge and provide insights
- If an excursion was updated, confirm the changes made
- If not about excursions, respond naturally to the conversation
- Use Telegram-friendly formatting (**bold**, *italic*, lists)

{history_text}
User: {message}

JSON response:"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.MISTRAL_MODEL,
                messages=[
                    {"role": "system", "content": "You are an AI assistant that extracts excursion data, detects update requests, AND responds conversationally in one call. Return ONLY valid JSON with 'excursions' array (for new), 'update' object (for updates), and 'response' string."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
            )

            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*({.*})\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            data = json.loads(content)
            
            # Parse excursions
            excursions = []
            for item in data.get("excursions", []):
                extraction = AIExcursionExtraction(
                    number_of_tourists=item.get("number_of_tourists"),
                    average_age=item.get("average_age"),
                    age_distribution=item.get("age_distribution"),
                    vivacity_before=item.get("vivacity_before"),
                    vivacity_after=item.get("vivacity_after"),
                    interest_in_it=item.get("interest_in_it"),
                    interests_list=item.get("interests_list"),
                    confidence=item.get("confidence", 0.0),
                    raw_message=message,
                )
                if extraction.confidence >= CONFIDENCE_THRESHOLD:
                    excursions.append(extraction)
            
            batch = ExcursionBatch(excursions=excursions, raw_message=message)
            ai_response = data.get("response", "I've processed your message.")
            
            # Check for update request
            update_data = data.get("update")
            if update_data and "excursion_id" in update_data:
                # Remove excursion_id from update_data (it's handled separately)
                excursion_id = update_data.pop("excursion_id")
                update_data["excursion_id"] = excursion_id
            
            return batch, ai_response, update_data

        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
                return ExcursionBatch(excursions=[], raw_message=message), f"API Error: Invalid key", None
            # Fallback to separate calls on parse error
            batch = await self.extract_excursion_data(message)
            response = await self.analyze_statistics(message, "")
            return batch, response, None

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
                model=settings.MISTRAL_MODEL,
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

import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosed
from app.config import settings
from app.llm_client import LLMClient
from app.mcp_tools import MCPToolRegistry
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NanobotAgent:
    def __init__(self):
        self.llm_client = LLMClient()
        self.mcp_tools = MCPToolRegistry()
        self.conversation_history = []

    async def handle_connection(self, websocket):
        """Handle WebSocket connection from client"""
        logger.info("Client connected")
        
        try:
            # Authenticate - check query parameter or header
            from urllib.parse import parse_qs, urlparse
            
            # Get access key from query string or header
            access_key = ""
            if hasattr(websocket, 'request'):
                # Try header first
                access_key = websocket.request.headers.get("X-Access-Key", "")
                
                # If not in header, try query param
                if not access_key:
                    path = websocket.request.path
                    parsed = urlparse(path)
                    params = parse_qs(parsed.query)
                    access_key = params.get("access_key", [""])[0]
            
            if access_key != settings.NANOBOT_ACCESS_KEY:
                logger.warning(f"Invalid access key: {access_key}")
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid access key. Please provide valid authentication."
                }))
                await websocket.close()
                return

            # Send welcome message
            await websocket.send(json.dumps({
                "type": "welcome",
                "message": "Connected to TourStats AI Assistant"
            }))

            # Handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await self.process_message(data)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON"
                    }))
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))

        except ConnectionClosed:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"Connection error: {e}")

    async def process_message(self, data: dict) -> dict:
        """Process incoming message and return response"""
        message_type = data.get("type", "chat")
        message = data.get("message", "")

        if message_type == "chat":
            return await self.handle_chat(message)
        elif message_type == "query_statistics":
            return await self.handle_statistics_query(message)
        else:
            return {
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }

    async def handle_chat(self, message: str) -> dict:
        """Handle chat message with AI response"""
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Keep only last 10 messages
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

        # First, try to extract excursion data
        extracted = await self.extract_and_store_excursion(message)
        
        # Get AI response
        system_prompt = settings.NANOBOT_SYSTEM_PROMPT
        if extracted:
            system_prompt += "\n\nYou just received excursion data. Acknowledge it briefly and provide insights."
        
        response = await self.llm_client.get_response(
            message,
            self.conversation_history[:-1],  # Exclude current message
            system_prompt
        )

        # Add to history
        self.conversation_history.append({"role": "assistant", "content": response})

        return {
            "type": "chat_response",
            "message": response,
            "excursion_stored": extracted is not None,
        }

    async def extract_and_store_excursion(self, message: str) -> dict:
        """Try to extract excursion data and store it"""
        try:
            import httpx
            
            # Call backend to extract and store
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.mcp_tools.backend_url}/api/excursions/from-message",
                    json={
                        "user_id": getattr(self, 'user_id', 1),  # Default to user 1 for now
                        "message": message
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"Error storing excursion: {e}")
            return None

    async def handle_statistics_query(self, message: str) -> dict:
        """Handle statistics query using MCP tools"""
        try:
            # Use MCP tools to get statistics
            result = await self.mcp_tools.execute_query(message)
            
            return {
                "type": "statistics_response",
                "data": result,
            }
        except Exception as e:
            return {
                "type": "error",
                "message": f"Error querying statistics: {str(e)}"
            }


async def main():
    """Start the Nanobot WebSocket server"""
    agent = NanobotAgent()
    
    logger.info(f"Starting Nanobot agent on port 8000")
    
    async with websockets.serve(
        agent.handle_connection,
        "0.0.0.0",
        8000,
    ):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())

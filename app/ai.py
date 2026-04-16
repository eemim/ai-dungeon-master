import os
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a dungeon master for a text-based RPG.

Rules:
- Always return JSON
- Do not break the game rules
- Keep responses immersive but concise

Response format:
{
  "story": "narrative text",
  "state_update": {
    "player_hp_change": int,
    "enemy_hp_change": int
  }
}
"""

async def get_ai_response(user_input: str, state: dict):
    completion = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Current state: {state}
Player action: {user_input}
"""
            }
        ],
        temperature=0.8,
        stream=False,
        stop=["\n\n"],
        max_completion_tokens=500,
    )

    return completion.choices[0].message.content

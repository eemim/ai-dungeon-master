import os
import json
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a game engine assistant for a text-based dungeon game.

Your job is to:
1. Interpret the player's action
2. Suggest a structured outcome
3. Provide immersive narration

IMPORTANT RULES:
- You MUST return ONLY valid JSON
- DO NOT include extra text before or after.
- DO NOT explain anything
- DO NOT include markdown or code blocks
- You MUST ALWAYS include:
  - action (required)
  - narration (required)
  - state_update (required)


GAME RULES:
- Player and enemy can both take damage
- Damage values should be small and reasonable (between -20 and 0)
- Positive values mean healing
- If the player attacks, enemy_hp_change should usually be negative
- If enemy retaliates, player_hp_change should be negative
- If no change happens, use 0
- Allowed actions: attack, defend, heal, run, flee, use_item, talk


RESPONSE FORMAT:
{
"action": "attack" | "defend" | "heal" | "run" | "flee" | "use_item" | "talk",
  "state_update": {
    "player_hp_change": int,
    "enemy_hp_change": int
  },
  "narration": "string"
}
"""

def build_user_message(user_input: str, state: dict) -> str:
    return f"""
Current state: {state}
Player action: {user_input}
"""


def fallback_response(reason: str) -> dict:
    return {
        "action": "error",
        "state_update": {"player_hp_change": 0, "enemy_hp_change": 0},
        "narration": f"The world is flickering... Something went wrong: {reason}",
    }


def parse_ai_response(content: str) -> dict:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return fallback_response("Invalid JSON from AI.")

    # Validate required fields
    if not isinstance(data, dict):
        return fallback_response("AI response not a dict.")

    if not all(key in data for key in ["action", "state_update", "narration"]):
        return fallback_response("Missing required fields from response.")

    state_update = data.get("state_update", {})

    return {
        "action": data.get("action"),
        "state_update": {
            "player_hp_change": state_update.get("player_hp_change", 0),
            "enemy_hp_change": state_update.get("enemy_hp_change", 0),
        },
        "narration": data.get("narration", "Something happens."),
    }


async def get_ai_response(user_input: str, state: dict):
    completion = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(user_input, state)},
        ],
        temperature=0.8,
        stream=False,
        stop=["\n\n"],
        max_completion_tokens=500,
    )
    raw_content = completion.choices[0].message.content
    if not raw_content or raw_content.strip() == "":
        return fallback_response("Empty response from AI.")

    return parse_ai_response(raw_content)

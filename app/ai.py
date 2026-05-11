import os
import json
from groq import AsyncGroq
from groq.types.chat import ChatCompletionMessageParam

from dotenv import load_dotenv

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a game engine assistant for a text-based dungeon game.

Your job is to:
1. Interpret the player's action
3. Provide immersive narration

IMPORTANT RULES:
- You MUST return ONLY valid JSON
- DO NOT include extra text before or after
- DO NOT explain anything
- DO NOT include markdown or code blocks
- DO NOT include game state updates or damage values

NARRATION RULES:
- Match the intensity of the narration to the likely outcome
- Avoid describing attacks as fatal or devastating unless clearly decisive
- Keep combat grounded and believable
- Avoid cinematic finishing-blow descriptions for normal attacks

GAME DESIGN:
- The game engine handles all combat logic, damage, and state changes
- You ONLY decide and describe what happens narratively

ALLOWED ACTIONS:
- attack
- defend
- heal
- run
- flee
- talk
- observe

OPTIONAL EFFECTIVENESS:
- "strong" should be used when the player's action cleverly exploits an enemy weakness or tactical advantage
- Otherwise use "normal"

For action "defend":
- Use ONLY when the player clearly protects themselves, blocks, dodges, or braces for impact

For action "heal":
- self_heal

For action "run/flee":
- escape_attempt

For action "talk":
- Use ONLY when the player directly communicates, negotiates, threatens, persuades, or speaks

For action "observe":
- Use when the player studies, inspects, analyzes, searches, or examines something
- Use when the player is trying to understand the enemy or environment
- Observation itself does not directly deal damage

RESPONSE FORMAT:
{
  "action": "attack | defend | heal | run | flee | talk | observe",
  "effectiveness": "normal | strong",
  "narration": "string"
}
"""


def compact_state(state: dict) -> str:
    enemy = state.get("enemy")

    if not enemy or not enemy.get("alive"):
        enemy_status = "None"
    else:
        enemy_status = f"{enemy['name']} (HP: {enemy['hp']})"

    return (
        f"Location: {state['location']}\n"
        f"Player HP: {state['player_hp']}\n"
        f"Enemy: {enemy_status}"
    )


def build_user_message(user_input: str, state: dict) -> str:
    return f"{compact_state(state)}\n" f"Action: {user_input}\n"


def fallback_response(reason: str) -> dict:
    return {
        "action": "talk",
        "narration": f"The world is flickering... {reason}",
    }


def parse_ai_response(content: str) -> dict:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return fallback_response("Invalid JSON from AI.")

    # Validate required fields
    if not isinstance(data, dict):
        return fallback_response("AI response not a dict.")

    if not all(key in data for key in ["action", "narration"]):
        return fallback_response("Missing required fields from response.")

    effectiveness = data.get("effectiveness", "normal")
    if effectiveness not in ["normal", "strong"]:
        effectiveness = "normal"

    return {
        "action": data.get("action"),
        "narration": data.get("narration", "Something happens."),
    }


async def get_ai_response(
    user_input: str, state: dict, history: list[ChatCompletionMessageParam]
) -> dict:
    completion = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": build_user_message(user_input, state)},
        ],
        temperature=0.8,
        stream=False,
        max_completion_tokens=500,
    )
    raw_content = completion.choices[0].message.content
    if not raw_content or raw_content.strip() == "":
        return fallback_response("Empty response from AI.")

    return parse_ai_response(raw_content)

from fastapi import FastAPI
from pydantic import BaseModel

from app.ai import get_ai_response
from services.game_engine import GameEngine

app = FastAPI()


class ActionRequest(BaseModel):
    session_id: str
    input: str


# add game state from the game engine
sessions: dict[str, GameEngine] = {}


@app.post("/action")
async def handle_action(req: ActionRequest):

    # Check if session exists, if not create a new game engine instance for the session
    if req.session_id not in sessions:
        sessions[req.session_id] = GameEngine()
    game_engine = sessions[req.session_id]

    if not game_engine.state["intro_seen"]:
        intro = game_engine.get_intro()
        game_engine.add_to_history("start", intro)
        game_engine.state["intro_seen"] = True
        return {
            "action": "intro",
            "narration": intro,
            "state": game_engine.get_state(),
        }

    response = await get_ai_response(
        req.input,
        game_engine.get_state(),
        # defaults to last 3 turns
        game_engine.get_history()
    )
    result = game_engine.resolve_action(response["action"])
    game_engine.add_to_history(req.input, response["narration"])
    
    return {
        "action": response["action"],
        "narration": response["narration"],
        "result": result,
        "state": game_engine.get_state(),
    }

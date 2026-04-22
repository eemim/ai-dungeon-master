from fastapi import FastAPI
from pydantic import BaseModel

from app.ai import get_ai_response
from services.game_engine import GameEngine

app = FastAPI()


class ActionRequest(BaseModel):
    session_id: str
    input: str


# add game state from the game engine
game_engine = GameEngine()
sessions: dict[str, GameEngine] = {}


@app.post("/action")
async def handle_action(req: ActionRequest):

    # Check if session exists, if not create a new game engine instance for the session
    if req.session_id not in sessions:
        sessions[req.session_id] = GameEngine()
    game_engine = sessions[req.session_id]

    response = await get_ai_response(
        req.input,
        game_engine.get_state(),
        # defaults to last 3 turns
        game_engine.get_history()
    )
    result = game_engine.apply_state_update(response["state_update"])
    game_engine.add_to_history(req.input, response["narration"])
    
    return {
        "action": response["action"],
        "narration": response["narration"],
        "state_update": response["state_update"],
        "result": result,
        "state": game_engine.get_state(),
    }

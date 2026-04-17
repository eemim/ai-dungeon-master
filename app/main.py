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
game_state = game_engine.state


@app.post("/action")
async def handle_action(req: ActionRequest):
    response = await get_ai_response(req.input, game_engine.get_state())
    result = game_engine.apply_state_update(response["state_update"])
    return {
        "action": response["action"],
        "narration": response["narration"],
        "state_update": response["state_update"],
        "result": result,
        "state": game_engine.get_state(),
    }

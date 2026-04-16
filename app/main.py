from fastapi import FastAPI
from pydantic import BaseModel
from app.ai import get_ai_response

app = FastAPI()

# request model
class ActionRequest(BaseModel):
    session_id: str
    input: str

# temporary in-memory state (we'll replace with DB later)
game_state = {
    "location": "village",
    "player_hp": 100,
    "enemy": {"name": "goblin", "hp": 30}
}

@app.post("/action")
async def handle_action(req: ActionRequest):
    response = await get_ai_response(req.input, game_state)
    return response

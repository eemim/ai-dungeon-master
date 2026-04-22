from typing import Any, Dict
from groq.types.chat import ChatCompletionMessageParam
from services.enemies import Enemy


class GameEngine:
    def __init__(self):
        self.history: list[ChatCompletionMessageParam] = []

        # randomly generate an enemy for the player to encounter at the start of the game
        self.state: Dict[str, Any] = {
            "location": "village",
            "player_hp": 100,
            "enemy": Enemy.random_enemy().model_dump(),
        }

    def add_to_history(self, user_input: str, narration: str):
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": narration})

    # Get the last few turns of history for context in AI responses, default to last 3 turns (6 messages)
    def get_history(self, max_turns: int = 3) -> list[ChatCompletionMessageParam]:

       return self.history[-(max_turns * 2):] 

    def get_state(self) -> Dict[str, Any]:

        return self.state

    def apply_state_update(self, state_update: dict) -> str:
        state_update = self.validate_state_update(state_update)

        # Update player HP
        # top at 0 to prevent negative HP values
        self.state["player_hp"] = max(
            0, self.state["player_hp"] + state_update["player_hp_change"]
        )
        
        # Update enemy HP
        # top at 0 to prevent negative HP values
        if self.state["enemy"]["alive"]:
            self.state["enemy"]["hp"] = max(
                0, self.state["enemy"]["hp"] + state_update["enemy_hp_change"]
            )

        # Check for game over conditions
        game_over_message = self.check_game_over()
        if game_over_message:
            return game_over_message

        return "State updated successfully."

    def check_game_over(self) -> str:
        if self.state["player_hp"] <= 0:
            self.reset_game()
            return "Game Over! You have been defeated. The game has been reset."

        enemy = self.state["enemy"]

        if enemy["alive"] and enemy["hp"] <= 0:
            enemy["alive"] = False
            return f"You have defeated the {enemy['name']}!"

        return ""

    def reset_game(self):
        self.history = []
        self.state = {
            "location": "village",
            "player_hp": 100,
            "enemy": Enemy.random_enemy().model_dump(),
        }

    def validate_state_update(self, state_update: dict) -> dict:
        allowed_keys = {
            "player_hp_change",
            "enemy_hp_change",
        }

        clean_update = {}

        for key in allowed_keys:
            value = state_update.get(key, 0)

            # for type safety
            if not isinstance(value, int):
                value = 0

            # clamp extreme values
            value = max(-50, min(50, value))

            clean_update[key] = value

        return clean_update

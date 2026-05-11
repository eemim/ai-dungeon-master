from typing import Any, Dict
import random
from groq.types.chat import ChatCompletionMessageParam

from services.enemies import Enemy


class GameEngine:
    def __init__(self):
        self.history: list[ChatCompletionMessageParam] = []

        # randomly generate an enemy for the player to encounter at the start of the game
        self.state: Dict[str, Any] = {
            "location": "Forgotten village",
            "player_hp": 100,
            "enemy": Enemy.random_enemy().model_dump(),
            "intro_seen": False,
        }

    def add_to_history(self, user_input: str, narration: str):
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": narration})

    def get_intro(self) -> str:
        enemy = self.state["enemy"]["name"]
        return (
            "Cold rain falls over the Forgotten Village. "
            "The streets are empty, doors left open, as if the townsfolk vanished overnight. "
            f"In the distance, a {enemy} emerges from the fog, blocking your path."
        )

    # Get the last few turns of history for context in AI responses, default to last 3 turns (6 messages)
    def get_history(self, max_turns: int = 3) -> list[ChatCompletionMessageParam]:

        return self.history[-(max_turns * 2) :]

    def get_state(self) -> Dict[str, Any]:

        return self.state

    def resolve_action(self, action: str, effectiveness: str = "normal") -> str:
        enemy = self.state["enemy"]
        result = ""
        damage_modifier = 1.0  # default damage modifier, can be adjusted based on player actions like "defend" or "observe"

        # PLAYER ACTION RESOLUTION

        if action == "attack" and enemy["alive"]:
            damage = random.randint(10, 18)

            if enemy["enemy_exposed"] or effectiveness == "strong":
                damage = int(damage * 1.7)
                enemy["enemy_exposed"] = False  # reset exposure after a successful exploit
                result += "You exploit the enemy's weakness for a critical hit! "

            enemy["hp"] = max(0, enemy["hp"] - damage)
            result += f"You deal {damage} damage."

            game_over_message = self.check_game_over()
            if game_over_message:
                result += f" {game_over_message}"
                return result.strip()

        elif action == "defend":
            damage_modifier = 0.5
            result += "You brace for the next attack, reducing incoming damage."

        elif action == "heal":
            heal_amount = random.randint(8, 15)
            self.state["player_hp"] = min(100, self.state["player_hp"] + heal_amount)
            result += f"You heal yourself for {heal_amount} HP."

        elif action == "talk" and enemy["alive"]:
            talk_success = random.random()
            if talk_success > 0.7:
                result += f"You successfully talked the {enemy['name']} down. It leaves peacefully."
            else:
                result += (
                    f"You try to talk to the {enemy['name']}, but it doesn't listen."
                )

        elif action == "observe":
            enemy["enemy_exposed"] = True
            result += (
                f"You carefully study the {enemy['name']}, looking for weaknesses."
            )
            damage_modifier = 0.8

        elif action in ["run", "flee"]:
            escape_chance = random.random()
            if escape_chance > 0.5:
                self.reset_game()
                return "You successfully escaped! The game has been reset."
            else:
                result += "You failed to escape!"

        else:
            result += "You hesitate, unsure of what to do."

        # ENEMY ACTION RESOLUTION

        if enemy["alive"]:
            enemy_action = random.choice(
                [
                    "attack",
                    "taunt",
                    "observe",
                ]
            )
            if enemy_action == "attack":
                damage = enemy["attack_power"] + random.randint(-2, 3)
                damage = int(damage * damage_modifier)
                self.state["player_hp"] = max(0, self.state["player_hp"] - damage)

                attack_descriptions = {
                    "Goblin": [
                        "The Goblin darts forward and slashes you",
                        "The Goblin lunges wildly at your side",
                    ],
                    "Orc": [
                        "The Orc swings its heavy weapon into you",
                        "The Orc charges forward with brutal force",
                    ],
                    "Troll": [
                        "The Troll recovers quickly and smashes into you",
                        "The Troll roars and slams a massive fist into you",
                    ],
                    "Skeleton": [
                        "Despite staggering backward, the Skeleton claws at you",
                        "The Skeleton snaps forward with rusted blades",
                    ],
                    "Vampire": [
                        "The Vampire glides through the shadows and strikes you",
                        "The Vampire lashes out with unnatural speed",
                    ],
                }

                attack_text = random.choice(
                    attack_descriptions.get(
                        enemy["name"],
                        [f"The {enemy['name']} attacks you"]
                    )
                )

                result += f" {attack_text} for {damage} damage."

            elif enemy_action == "taunt":
                result += f" The {enemy['name']} snarls aggressively."

            else:
                result += f" The {enemy['name']} watches your movements carefully."

        game_over_message = self.check_game_over()

        if game_over_message:
            result += f" {game_over_message}"
            return result.strip()

        return result.strip()

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
            "location": "Forgotten village",
            "player_hp": 100,
            "enemy": Enemy.random_enemy().model_dump(),
            "intro_seen": False,
        }

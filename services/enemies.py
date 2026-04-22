import random
from pydantic import BaseModel


class Enemy(BaseModel):
    name: str
    hp: int
    attack_power: int
    special_ability: str
    alive: bool = True

    def attack(self) -> int:
        # Basic attack logic, can be expanded with more complex mechanics
        return self.attack_power

    def use_special_ability(self) -> str:
        # Logic for using the special ability, can be expanded with more complex mechanics
        return f"{self.name} uses {self.special_ability}!"

    @classmethod
    def random_enemy(cls) -> "Enemy":

        enemies = [Goblin(), Orc(), Troll(), Skeleton(), Vampire()]
        enemy = random.choice(enemies)
        print(enemy)
        return enemy


class Goblin(Enemy):
    name: str = "Goblin"
    hp: int = 30
    attack_power: int = 5
    special_ability: str = "Sneaky Strike"

class Orc(Enemy):
    name: str = "Orc"
    hp: int = 50
    attack_power: int = 10
    special_ability: str = "Berserk Rage"

class Troll(Enemy):
    name: str = "Troll"
    hp: int = 80
    attack_power: int = 15
    special_ability: str = "Bugger Smash"

class Skeleton(Enemy):
    name: str = "Skeleton"
    hp: int = 20
    attack_power: int = 7
    special_ability: str = "Bone Shield"

class Vampire(Enemy):
    name: str = "Vampire"
    hp: int = 40
    attack_power: int = 12
    special_ability: str = "Life Drain"

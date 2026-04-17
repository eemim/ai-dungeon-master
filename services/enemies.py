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
    def __init__(self):
        super().__init__(
            name="Goblin", hp=30, attack_power=5, special_ability="Sneaky Strike"
        )


class Orc(Enemy):
    def __init__(self):
        super().__init__(
            name="Orc", hp=50, attack_power=10, special_ability="Berserk Rage"
        )


class Troll(Enemy):
    def __init__(self):
        super().__init__(
            name="Troll", hp=80, attack_power=15, special_ability="Bugger Smash"
        )


class Skeleton(Enemy):

    def __init__(self):
        super().__init__(
            name="Skeleton", hp=20, attack_power=7, special_ability="Bone Shield"
        )


class Vampire(Enemy):
    def __init__(self):
        super().__init__(
            name="Vampire", hp=40, attack_power=12, special_ability="Life Drain"
        )

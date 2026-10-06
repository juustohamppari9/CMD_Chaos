"""Enemy class for CMD Chaos.

Represents hostile computer processes (viruses, malware, rogue AI)
that the player must combat or avoid.
"""

import random


class Enemy:
    """A hostile process in the system."""

    def __init__(self, name, health=None, aggression=1):
        self.name = name
        self.max_health = health or random.randint(15, 30)
        self.health = self.max_health
        self.aggression = aggression  # how likely to attack each turn
        self._alive = True

    @property
    def is_alive(self):
        """True if the enemy still has health remaining."""
        return self._alive and self.health > 0

    def take_damage(self, amount):
        """Reduce enemy health. Returns remaining health; kills if <= 0."""
        self.health -= amount
        if self.health <= 0:
            self._alive = False
            return 0
        return self.health

    def take_turn(self, player):
        """Decide and execute action during this enemy's turn."""
        # Simple AI: move towards player or attack with some probability
        if not player.is_alive:
            return
        # Random chance to attack based on aggression
        if random.random() < self.aggression:
            dmg = random.randint(5, 10)
            player.take_damage(dmg)
            # No UI import at module level; caller should handle messaging

    def __str__(self):
        return f"Enemy[{self.name}] HP:{self.health}/{self.max_health} Alive:{self.is_alive}"
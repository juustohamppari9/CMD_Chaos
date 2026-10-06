"""Player class for CMD Chaos.

Represents the hacker user inside the terminal simulation.
Tracks health, score, and provides actions the player can take.
"""

class Player:
    """The hacker player character."""

    def __init__(self, name):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.score = 0
        self.level = 1
        self.viruses_cleaned = 0
        self.inventory = []

    @property
    def is_alive(self):
        """True if the player has health remaining."""
        return self.health > 0

    def take_damage(self, amount):
        """Reduce player health by amount. Returns remaining health."""
        self.health = max(0, self.health - amount)
        return self.health

    def heal(self, amount):
        """Increase player health (e.g., from med-kits or restoration)."""
        self.health = min(self.max_health, self.health + amount)
        return self.health

    def add_score(self, amount):
        """Add points to the player's score."""
        self.score += amount
        return self.score

    def clean_virus(self):
        """Mark one virus as cleaned. Returns True if a milestone is reached."""
        self.viruses_cleaned += 1
        return self.viruses_cleaned

    def __str__(self):
        return f"Player[{self.name}] HP:{self.health}/{self.max_health} Score:{self.score}"
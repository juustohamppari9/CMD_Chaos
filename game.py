"""Core game logic for CMD Chaos.

Manages game state, turns, win/loss conditions, and the overall
flow of the hacker terminal simulation.
"""

from player import Player
from enemy import Enemy
from save import save_game, load_game


class Game:
    """Main game container. Holds state and coordinates actions."""

    def __init__(self, player_name="Terminal"):
        self.state = {
            "player_name": player_name,
            "level": 1,
            "score": 0,
            "health": 100,
            "max_health": 100,
            "viruses_cleaned": 0,
            "max_viruses": 10,
            "game_over": False,
            "victory": False,
            "current_floor": 1,
            "inventory": [],
        }
        self.player = Player(self.state["player_name"])
        self.enemies = []
        self.turn_number = 0

    def start(self):
        """Reset and initialize a new game."""
        self.state = {
            "player_name": self.state.get("player_name", "Terminal"),
            "level": 1,
            "score": 0,
            "health": 100,
            "max_health": 100,
            "viruses_cleaned": 0,
            "max_viruses": 10,
            "game_over": False,
            "victory": False,
            "current_floor": 1,
            "inventory": [],
            # Node progression state
            "current_node": 1,
            "system_integrity": 100,
            "scrap": 0,
        }
        self.player = Player(self.state["player_name"])
        self.enemies = []
        self.turn_number = 0
        self._spawn_initial_enemies()
        print(f"Welcome, {self.player.name}, to the corrupted system.")
        print("Your mission: purge the viruses and restore order.")

    def _spawn_initial_enemies(self):
        """Create the initial set of hostile processes."""
        from ui import UI
        ui = UI()
        for i in range(3):
            enemy = Enemy(f"Process-{i+1}", health=20 + i * 5)
            self.enemies.append(enemy)

    def update(self):
        """Execute one turn of game logic."""
        self.turn_number += 1
        # Process player action (handled by UI input)
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.take_turn(self.player)
            # Enemy damages player if alive (simple chance-based damage in take_turn)
            if enemy.is_alive:
                # Occasional direct damage when enemy is alive
                import random
                if random.random() < 0.3:  # 30% chance each turn
                    self.player.take_damage(10)
                    ui = __import__("ui").UI()
                    ui.message(f"{enemy.name} damages you! Health: {self.player.health}%", "warning")
        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.is_alive]
        # Check win/loss conditions
        self._check_conditions()

    def _check_conditions(self):
        """Check win/loss conditions and update state."""
        if self.state["health"] <= 0:
            self.state["game_over"] = True
            self.state["victory"] = False
            print("SYSTEM CRASH: Your terminal has been compromised.")
        elif self.state["viruses_cleaned"] >= self.state["max_viruses"]:
            self.state["victory"] = True
            self.state["game_over"] = True
            print("SYSTEM RESTORED: All viruses purged. Mission accomplished!")

    def is_over(self):
        """Return True if the game has ended (win or lose)."""
        return self.state["game_over"]

    def save(self):
        """Persist current game state to disk."""
        save_game(self.state)
        from ui import UI
        ui = UI()
        ui.message("Game saved successfully.", "success")

    def load(self):
        """Load a saved game state."""
        loaded = load_game()
        if loaded:
            self.state = loaded
            self.player = Player(self.state.get("player_name", "Terminal"))
            self._spawn_initial_enemies()
            from ui import UI
            ui = UI()
            ui.message("Game loaded.", "success")
        else:
            from ui import UI
            ui = UI()
            ui.message("No saved game found.", "info")
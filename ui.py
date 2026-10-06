"""User Interface for CMD Chaos.

Handles all text output, display formatting, and input parsing.
Designed for plain Windows CMD without graphical dependencies.
"""

import random
import sys
import time


class UI:
    """Simple CMD UI helper."""

    # ANSI color codes (work in most modern CMD consoles)
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }

    @staticmethod
    def _color(text, color):
        """Wrap text with ANSI color code if stdout supports it."""
        try:
            if sys.stdout.isatty():
                return f"{UI.COLORS.get(color, '')}{text}{UI.COLORS['reset']}"
        except Exception:
            pass
        return text

    @classmethod
    def clear_screen(cls):
        """Clear the console screen."""
        os = __import__("os")
        # Windows CMD: 'cls', Unix: 'clear'
        os.system("cls" if os.name == "nt" else "clear")

    @classmethod
    def render_title(cls):
        """Print the game title with style."""
        cls.clear_screen()
        title = cls._color("CMD CHAOS", "red") + " - " + cls._color("Hacker Terminal", "cyan")
        print("=" * 60)
        print(title.center(60))
        print("=" * 60)
        print()

    @classmethod
    def display(cls, state):
        """Render the full game state to the console.

        Args:
            state: dict with current game state variables.
        """
        cls.render_title()
        cls.display_status(state)

    @classmethod
    def message(cls, text, msg_type="info"):
        """Display a colored message box.

        Args:
            text: The message string.
            msg_type: One of 'info', 'warning', 'success', 'error'.
        """
        types = {
            "info": ("[INFO]", "blue"),
            "warning": ("[WARNING]", "yellow"),
            "success": ("[SUCCESS]", "green"),
            "error": ("[ERROR]", "red"),
        }
        label, color = types.get(msg_type, ("[INFO]", "white"))
        colored_label = cls._color(label, color)
        print(colored_label + " " + cls._color(text, color))

    @classmethod
    def display_status(cls, game_state):
        """Render the top-status bar showing player info.

        Args:
            game_state: dict with player health, level, viruses cleaned, etc.
        """
        health_bar_len = 40
        health_percent = game_state.get("health", 100)
        # Build health bar: filled portions + ">" if not full, then padded to length
        filled_len = int(health_percent / 100 * health_bar_len)
        if health_percent >= 100:
            bar_str = "[" + "=" * health_bar_len + "]"
        else:
            bar_str = "[" + "=" * filled_len + ">" + "." * (health_bar_len - filled_len - 1) + "]"
        bar_str = cls._color(bar_str, "green")
        print(f" Level: {game_state.get('level', 1)}   "
              f"Viruses Cleaned: {game_state.get('viruses_cleaned', 0)}/{game_state.get('max_viruses', 10)}   "
              f"Health: {bar_str} {health_percent}%")

    @classmethod
    def display_inventory(cls, inventory):
        """List player inventory items."""
        if not inventory:
            print(" Inventory: (empty)")
            return
        print(" Inventory:")
        for idx, item in enumerate(inventory, start=1):
            print(f"   {idx}. {item}")

    @classmethod
    def get_input(cls, prompt="> ", choices=None):
        """Prompt the user for input and return the raw string.

        Args:
            prompt: The prompt string to show.
            choices: Optional list of acceptable lower-case strings.
        """
        while True:
            try:
                user_input = input(prompt).strip().lower()
                if choices and user_input not in choices:
                    cls.message(f"Please choose from: {', '.join(choices)}", "warning")
                    continue
                return user_input
            except (EOFError, KeyboardInterrupt):
                cls.message("Exiting...", "info")
                return "quit"

    @classmethod
    def wait(cls, seconds=1):
        """Pause execution for a number of seconds (typewriter effect)."""
        time.sleep(seconds)

    @classmethod
    def typewriter(cls, text, delay=0.03):
        """Print text character by character for a typewriter effect."""
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write("\n")
        sys.stdout.flush()

    @classmethod
    def main_menu(cls):
        """Show the main menu and return the user's choice."""
        print()
        print("  1. Start New Game")
        print("  2. Load Game")
        print("  3. Credits")
        print("  4. Quit")
        print()
        choice = cls.get_input("Select an option (1-4): ", choices=["1", "2", "3", "4", "quit"])
        return choice

    @classmethod
    def combat_menu(cls, enemy):
        """Present combat options during an enemy turn.

        Returns the player's chosen action string.
        """
        print(f"\n  Enemy: {enemy.name} attacks! (HP: {enemy.health}/{enemy.max_health})")
        print("  What will you do?")
        print("  1. Fight back")
        print("  2. Hack (attempt to purge)")
        print("  3. Flee")
        choices = ["1", "2", "3"]
        return cls.get_input("Choose action (1-3): ", choices=choices)

    @classmethod
    def handle_input(cls, game):
        """Handle a single player turn input.

        Args:
            game: The Game instance.
        """
        print("\n--- Your Turn ---")
        print("  1. Attack")
        print("  2. Hack (purge viruses)")
        print("  3. Flee")
        choices = ["1", "2", "3", "quit"]
        choice = cls.get_input("Choose action (1-3 or 'quit'): ", choices=choices)

        if choice == "1":
            # Simple attack - damage enemy
            if game.enemies:
                target = game.enemies[0]
                dmg = random.randint(5, 15)
                target.take_damage(dmg)
                cls.message(f"You attack {target.name} for {dmg} damage!", "success")
                if not target.is_alive:
                    cls.message(f"{target.name} has been purged!", "success")
                    game.enemies.remove(target)
                    game.state["viruses_cleaned"] = game.state.get("viruses_cleaned", 0) + 1
            else:
                cls.message("No enemies to attack!", "info")
        elif choice == "2":
            # Hack attempt - chance to clean viruses
            if game.state.get("viruses_cleaned", 0) < game.state.get("max_viruses", 10):
                if random.random() < 0.5:
                    game.state["viruses_cleaned"] = game.state.get("viruses_cleaned", 0) + 1
                    cls.message("You successfully purged a virus!", "success")
                else:
                    cls.message("The hack attempt failed. Try again!", "warning")
            else:
                cls.message("All viruses already purged!", "info")
        elif choice == "3":
            cls.message("You flee the area.", "info")
        return choice  # returns "quit" if chosen, otherwise "1", "2", or "3"
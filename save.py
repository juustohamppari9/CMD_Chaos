"""Save/Load system for CMD Chaos.

Persists the game state to a simple text file so players can
resume their hacker session later.
"""

import os
import json


SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".saves")
SAVE_FILE = os.path.join(SAVE_DIR, "game_save.json")


def _ensure_save_dir():
    """Create the .saves directory if it doesn't exist."""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR, exist_ok=True)


def save_game(state):
    """Save the given game state dictionary to disk.

    Args:
        state: dict containing all relevant game variables.
    """
    _ensure_save_dir()
    # Remove any keys that shouldn't be serialized (e.g., player objects)
    serializable = {
        "player_name": state.get("player_name", "Terminal"),
        "level": state.get("level", 1),
        "score": state.get("score", 0),
        "health": state.get("health", 100),
        "max_health": state.get("max_health", 100),
        "viruses_cleaned": state.get("viruses_cleaned", 0),
        "max_viruses": state.get("max_viruses", 10),
        "game_over": state.get("game_over", False),
        "victory": state.get("victory", False),
        "current_floor": state.get("current_floor", 1),
        "inventory": state.get("inventory", []),
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)
    # Optional: also print a human-readable snapshot
    # print(f"Game saved to {SAVE_FILE}")


def load_game():
    """Load the most recent game state from disk.

    Returns:
        dict or None: The saved state, or None if no save file exists.
    """
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading save file: {e}")
        return None


def list_saves():
    """Return a list of available save file paths.

    Returns:
        list of str
    """
    if not os.path.exists(SAVE_DIR):
        return []
    files = []
    for fname in os.listdir(SAVE_DIR):
        if fname.endswith(".json"):
            files.append(os.path.join(SAVE_DIR, fname))
    return sorted(files)
"""CMD Chaos - A hacker terminal roguelike game.
Run directly in Windows CMD with a dark cyberpunk atmosphere.

Features a roguelike node progression system through 10 system nodes,
with random encounters including viruses, scrap caches, system events,
repair stations, and elite viruses.
"""

import sys
import os
import random

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import Game
from ui import UI
from player import Player
from enemy import Enemy
from save import save_game, load_game

# Encounter type constants
ENCOUNTER_VIRUS = "VIRUS"
ENCOUNTER_SCRAP = "SCRAP CACHE"
ENCOUNTER_EVENT = "SYSTEM EVENT"
ENCOUNTER_REPAIR = "REPAIR STATION"
ENCOUNTER_ELITE = "ELITE VIRUS"

ALL_ENCOUNTER_TYPES = [ENCOUNTER_VIRUS, ENCOUNTER_SCRAP, ENCOUNTER_EVENT,
                       ENCOUNTER_REPAIR, ENCOUNTER_ELITE]


def get_random_encounter(current_node):
    """Select a random encounter type, scaled for node difficulty.
    
    Later nodes have progressively higher chance of elite viruses,
    with all types still possible.
    """
    weights = [8, 8, 8, 8, 8]  # base equal weights
    # Scale difficulty: later nodes have more elite viruses
    if current_node >= 8:
        weights = [3, 3, 3, 3, 38]  # very likely elite at node 8-10
    elif current_node >= 5:
        weights = [5, 5, 5, 5, 28]  # likely elite at node 5-7
    elif current_node >= 3:
        weights = [6, 6, 6, 6, 26]  # slightly more elite at node 3-4
    return random.choices(ALL_ENCOUNTER_TYPES, weights=weights)[0]


def handle_virus_encounter(game, ui):
    """Start a normal virus combat encounter.
    
    Creates an enemy appropriate for the current node and runs combat.
    Awards scrap and counts as a virus cleaned on victory.
    """
    node = game.state["current_node"]
    # Create enemy scaled to node difficulty
    health = 15 + node * 5
    aggression = 0.3 + node * 0.05
    enemy = Enemy(f"Virus-{node}", health=health, aggression=aggression)
    game.enemies = [enemy]

    ui.message(f"Node {node}: Virus encounter! {enemy.name} appears!", "warning")

    # Combat loop
    while game.enemies and game.player.is_alive:
        ui.display(game.state)
        result = ui.handle_input(game)
        if result == "quit":
            return False

        # Process player's action (handled in ui.handle_input)
        # Enemy turns
        for enemy in game.enemies[:]:
            if enemy.is_alive and game.player.is_alive:
                enemy.take_turn(game.player)

        # Remove dead enemies
        game.enemies = [e for e in game.enemies if e.is_alive]

    if game.player.is_alive:
        ui.message("Viruses purged! +10 scrap", "success")
        game.state["scrap"] = game.state.get("scrap", 0) + 10
        game.state["viruses_cleaned"] = game.state.get("viruses_cleaned", 0) + 1
        game.enemies = []
    else:
        ui.message("Your terminal has been compromised!", "error")
        game.state["health"] = 0

    return game.player.is_alive


def handle_scrap_cache(game, ui):
    """Give the player random scrap. The player cannot fight it."""
    node = game.state["current_node"]
    amount = random.randint(15, 30) + (node - 1) * 5
    game.state["scrap"] = game.state.get("scrap", 0) + amount
    ui.message(f"Scrap Cache found! +{amount} scrap", "success")


def handle_system_event(game, ui):
    """Present a random choice with positive or negative consequence."""
    node = game.state["current_node"]
    # Events scaled by node difficulty
    events = [
        ("Data Recovery",
         f"+20 HP, +{random.randint(5, 15)} scrap",
         "success"),
        ("Phantom Process",
         f"-15 HP (no scrap loss)",
         "warning"),
        ("Cache Overflow",
         f"+{random.randint(10, 25)} scrap, +5% system integrity",
         "success"),
        ("Configuration Error",
         f"-10 HP",
         "error"),
        ("System Tweak",
         f"+{random.randint(5, 10)}% system integrity",
         "success"),
    ]
    choice_idx = random.randint(0, len(events) - 1)
    event_name, consequence, event_type = events[choice_idx]

    # Process the consequence using regex-inspired parsing
    # Handle each "+" or "-" signed component separately
    import re
    # Find all signed number+label patterns
    matches = re.findall(r'([+-]\d+)\s*(\w+)', consequence)
    for sign, label in matches:
        value = int(sign)
        if label == "HP":
            game.state["health"] = min(100, max(0, game.state.get("health", 100) + value))
        elif label == "scrap":
            game.state["scrap"] = game.state.get("scrap", 0) + value
        elif label == "integrity":
            si = game.state.get("system_integrity", 100)
            game.state["system_integrity"] = min(100, max(0, si + value))

    # Also handle standalone ± numbers without labels (for simple cases)
    # e.g., "-10 HP" from Configuration Error
    if "HP" in consequence and not matches:
        # Simple case: just "-10 HP" or "+20 HP"
        for part in consequence.split(", "):
            if "HP" in part:
                try:
                    val = int(part.replace("HP", "").strip().replace("+", "").replace("-", "-"))
                    game.state["health"] = min(100, max(0, game.state.get("health", 100) + val))
                except ValueError:
                    pass

    ui.message(f"System Event: {event_name} - {consequence}", event_type)


def handle_repair_station(game, ui):
    """Allow the player to restore HP and system integrity."""
    node = game.state["current_node"]
    heal_amount = random.randint(20, 35)
    # Repair effectiveness decreases slightly per node (harder to repair later)
    integrity_restore = max(5, random.randint(15, 25) - (node - 1) * 2)

    game.state["health"] = min(100, game.state.get("health", 100) + heal_amount)
    si = game.state.get("system_integrity", 100)
    game.state["system_integrity"] = min(100, si + integrity_restore)

    ui.message(
        f"Repair Station: Recovered {heal_amount} HP and "
        f"{integrity_restore}% system integrity", "success")


def handle_elite_virus(game, ui):
    """Create a stronger enemy with more HP and damage.
    
    Gives significantly more scrap than a normal enemy on victory.
    """
    node = game.state["current_node"]
    # Elite virus: 1.8x normal health, higher aggression
    health = int(25 + node * 8 * 1.8)
    aggression = 0.5 + node * 0.1
    enemy = Enemy(f"Elite Virus-{node}", health=health, aggression=aggression)
    game.enemies = [enemy]

    ui.message(
        f"Node {node}: ELITE VIRUS encounter! {enemy.name} appears! "
        f"(Significantly stronger than normal)", "error")

    # Combat loop - harder fight
    while game.enemies and game.player.is_alive:
        ui.display(game.state)
        result = ui.handle_input(game)
        if result == "quit":
            return False

        for enemy in game.enemies[:]:
            if enemy.is_alive and game.player.is_alive:
                enemy.take_turn(game.player)

        game.enemies = [e for e in game.enemies if e.is_alive]

    if game.player.is_alive:
        # Elite viruses give much more scrap
        scrap_amount = random.randint(40, 60) + (node - 1) * 10
        game.state["scrap"] = game.state.get("scrap", 0) + scrap_amount
        ui.message(
            f"Elite virus purged! +{scrap_amount} scrap", "success")
        game.enemies = []
        # Also count as virus cleaned
        game.state["viruses_cleaned"] = game.state.get("viruses_cleaned", 0) + 1
    else:
        ui.message("Your terminal has been compromised!", "error")
        game.state["health"] = 0

    return game.player.is_alive


def run_node_progression(game, ui):
    """Run the node progression system through 10 system nodes.
    
    Each node randomly generates one of five encounter types.
    The run progresses from node 1 to node 10.
    At node 10, a powerful process is detected with a placeholder boss.
    """
    # Initialize node state
    game.state["current_node"] = 1
    game.state["system_integrity"] = 100
    game.state["scrap"] = 0
    game.enemies = []

    ui.message("=" * 60)
    ui.message("CMD CHAOS - Node Progression System", "bold")
    ui.message("=" * 60)
    ui.message("", "info")
    ui.message("Mission: Navigate through 10 corrupted system nodes", "info")
    ui.message("Survive viruses, scavenge scrap, and restore system integrity", "info")
    ui.message("", "info")

    running = True
    while running and game.state["current_node"] <= 10:
        node = game.state["current_node"]
        ui.clear_screen()
        ui.render_title()

        # Display current status
        ui.message(f"=== Node {node} of 10 ===", "bold")
        ui.message(
            f"HP: {game.state.get('health', 100)}%   |   "
            f"System Integrity: {game.state.get('system_integrity', 100)}%   |   "
            f"Scrap: {game.state.get('scrap', 0)}", "info")
        ui.message("", "info")

        # Check if this is node 10 (last node)
        if node == 10:
            ui.message("=== NODE 10: LAST NODE ===", "error")
            ui.message("A formidable process guards the final system core.", "warning")

        # Get encounter type for this node
        encounter = get_random_encounter(node)

        ui.message(f"Encounter type: {encounter}", "info")
        ui.message("", "info")

        # Handle the encounter based on type
        survived = True

        if encounter == ENCOUNTER_VIRUS:
            # Show combat start message
            ui.message(f"Starting combat with {encounter}...", "info")
            survived = handle_virus_encounter(game, ui)
            # Don't clear screen here - let the completion display handle it
        elif encounter == ENCOUNTER_SCRAP:
            handle_scrap_cache(game, ui)
            # Immediately show completion (no combat animation to wait for)
            ui.clear_screen()
            ui.render_title()
            ui.message(f"=== Node {node} Complete ===", "success")
            ui.message(
                f"HP: {game.state.get('health', 100)}%   |   "
                f"System Integrity: {game.state.get('system_integrity', 100)}%   |   "
                f"Scrap: {game.state.get('scrap', 0)}", "info")
            ui.message("", "info")
            ui.message(f"Prepare for Node {node + 1}...", "info")
            try:
                user_input = input("Press Enter to continue to next node...")
            except (EOFError, KeyboardInterrupt):
                ui.message("Auto-advancing to next node...", "info")
        elif encounter == ENCOUNTER_EVENT:
            handle_system_event(game, ui)
            # Show completion immediately after event
            ui.clear_screen()
            ui.render_title()
            ui.message(f"=== Node {node} Complete ===", "success")
            ui.message(
                f"HP: {game.state.get('health', 100)}%   |   "
                f"System Integrity: {game.state.get('system_integrity', 100)}%   |   "
                f"Scrap: {game.state.get('scrap', 0)}", "info")
            ui.message("", "info")
            ui.message(f"Prepare for Node {node + 1}...", "info")
            try:
                user_input = input("Press Enter to continue to next node...")
            except (EOFError, KeyboardInterrupt):
                ui.message("Auto-advancing to next node...", "info")
        elif encounter == ENCOUNTER_REPAIR:
            handle_repair_station(game, ui)
            # Show completion immediately after repair
            ui.clear_screen()
            ui.render_title()
            ui.message(f"=== Node {node} Complete ===", "success")
            ui.message(
                f"HP: {game.state.get('health', 100)}%   |   "
                f"System Integrity: {game.state.get('system_integrity', 100)}%   |   "
                f"Scrap: {game.state.get('scrap', 0)}", "info")
            ui.message("", "info")
            ui.message(f"Prepare for Node {node + 1}...", "info")
            try:
                user_input = input("Press Enter to continue to next node...")
            except (EOFError, KeyboardInterrupt):
                ui.message("Auto-advancing to next node...", "info")
        elif encounter == ENCOUNTER_ELITE:
            survived = handle_elite_virus(game, ui)
            # Don't clear screen here - let the completion display handle it

        # Check if player is still alive after encounter
        if not game.player.is_alive:
            ui.message("SYSTEM CRASH: You have been compromised.", "error")
            game.state["game_over"] = True
            running = False
            break

        # Show node completion status
        ui.clear_screen()
        ui.render_title()
        ui.message(f"=== Node {node} Complete ===", "success")
        ui.message(
            f"HP: {game.state.get('health', 100)}%   |   "
            f"System Integrity: {game.state.get('system_integrity', 100)}%   |   "
            f"Scrap: {game.state.get('scrap', 0)}", "info")
        ui.message("", "info")

        if node == 10:
            # Node 10 ends the run - show powerful process detected
            ui.message("! POWERFUL PROCESS DETECTED - LAST NODE !", "error")
            ui.message(
                "Preparing final confrontation... (placeholder for now)", "warning")
            ui.message(
                "The corrupted system core awaits your final confrontation.", "info")
            # Placeholder boss - display message, don't fight yet
            ui.message(
                "BOSS ENCOUNTER: [Placeholder - Boss Fight Not Yet Implemented]",
                "bold")
            ui.message(
                "Returning to terminal...", "info")
            # End the run after node 10
            running = False
        else:
            # Ask to continue to next node (with EOF safety for non-interactive environments)
            try:
                user_input = input("Press Enter to continue to next node...")
                # If user just presses enter, continue to next node
            except (EOFError, KeyboardInterrupt):
                # Auto-advance in non-interactive environments
                ui.message("Auto-advancing to next node...", "info")

        # Increment node for next iteration (except node 10 which ends)
        if node < 10:
            game.state["current_node"] = node + 1

    # Run summary
    ui.clear_screen()
    ui.render_title()
    ui.message("=" * 60)
    ui.message("RUN SUMMARY", "bold")
    ui.message("=" * 60)
    ui.message("", "info")
    ui.message(f"Final Node Reached: {game.state.get('current_node', 0)}", "info")
    ui.message(f"Final HP: {game.state.get('health', 100)}%", "info")
    ui.message(
        f"System Integrity: {game.state.get('system_integrity', 0)}%", "info")
    ui.message(f"Total Scrap: {game.state.get('scrap', 0)}", "info")
    ui.message(
        f"Viruses Cleaned: {game.state.get('viruses_cleaned', 0)}", "info")
    ui.message("", "info")

    if game.state.get("current_node", 0) >= 10:
        ui.message(
            "CONGRATULATIONS: You survived all 10 nodes!", "success")
    elif not game.player.is_alive:
        ui.message("GAME OVER: Your terminal was compromised.", "error")
    else:
        ui.message("Run terminated early.", "info")

    ui.message("", "info")

    # Save progress
    save_game(game.state)
    ui.message("Game saved. Until next time, hacker.", "success")


def main():
    """Entry point for CMD Chaos."""
    print("=" * 60)
    print("   CMD CHAOS - A Hacker Terminal Roguelike")
    print("=" * 60)
    print()
    print("Initializing hostile system simulation...")
    print()

    # Initialize game and UI
    game = Game()
    ui = UI()

    # Note: Node progression state is initialized within run_node_progression()
    # via game.state updates. Existing game state variables are preserved.

    try:
        run_node_progression(game, ui)
    except KeyboardInterrupt:
        print("\nExiting CMD Chaos. Stay safe out there...")
    finally:
        # Save progress before exiting
        save_game(game.state)
        print("Game saved. Until next time, hacker.")


if __name__ == "__main__":
    main()
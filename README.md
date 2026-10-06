# CMD Chaos

A hacker terminal roguelike game running in Windows CMD.

## Theme

- Dark cyberpunk atmosphere
- Corrupted computer system
- Viruses and hostile processes
- Hacker terminal aesthetic

## How to Run

```bash
python main.py
```

The game requires Python 3.8+ and no external dependencies (pure standard library).

## Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point, runs the main game loop |
| `game.py` | Core game logic, state management, turn handling |
| `player.py` | Player class representing the hacker |
| `enemy.py` | Enemy class for hostile processes/viruses |
| `ui.py` | Text-based user interface for CMD display and input |
| `save.py` | Save and load game progress to `.saves/` directory |
| `README.md` | This file |
| `.gitignore` | Python and system ignore rules |

## Gameplay

You are a hacker trapped in a corrupted system. Your goal is to:
- Purge viruses and hostile processes
- Manage your health and resources
- Survive each level (floor) and progress deeper
- Uncover what caused the system corruption

Controls are text-based: number keys for menu choices, arrow keys or letters for navigation.

## Development

This is a beginner-friendly project structured in a modular way:
- Each module (`player`, `enemy`, `ui`, etc.) has a single responsibility.
- The `Game` class orchestrates the flow.
- The `UI` class handles all text output and input.
- Save files are stored in `.saves/` as JSON.

## License

This project is open source and available under the MIT License.
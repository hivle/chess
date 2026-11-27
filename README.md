# Chess
Full feature Chess (En Passant, Check/Draw Detection, Castling, Legal Moves Only, Threefold Repetition and Fifty Moves Rule) with AI opponent.

![game_play](screenshots/0.png "game_play")

## Install
```
pip install pygame pytest
```

## Play
**GUI** (requires pygame):
```
python play.py
```

**Terminal** (no dependencies):
```
python play_cli.py
```

## Controls
- **Left click** — select piece / move
- **Right click** — deselect
- **← arrow** — undo move (in AI mode, undoes your move and the AI's reply)
- **→ arrow** — redo move
- **Q** — return to menu

The window title shows the latest moves. In the terminal version, type `undo`, `redo`, `moves` (show the game so far) or `quit`.

## Run Tests
```
python -m pytest tests/ -v
```

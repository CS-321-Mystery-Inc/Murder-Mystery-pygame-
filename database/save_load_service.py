"""This is the Business logic for one in-game save slot.

UI calls SaveLoadService; this module calls database.py, never Pygame.
Only player positions and collected evidence are saved in this sprint.
"""

import json
import math

from . import database


class SaveLoadService:
    SAVE_KEY = "save_slot_1"

    def __init__(self, player_count):
        if player_count not in (1, 2):
            raise ValueError("Only one or two players are supported")
        self.player_count = player_count
        database.initialize_database()

    """Check a snapshot before saving or restoring database records."""
    def _validate(self, data):
        if not isinstance(data, dict) or data.get("version") != 1:
            raise ValueError("Invalid saved game format")
        
        if data.get("player_count") != self.player_count:
            raise ValueError("Saved game uses a different number of players")

        positions = data.get("positions")
        expected_players = {"player1"}
        if self.player_count == 2:
            expected_players.add("player2")

        if not isinstance(positions, dict) or set(positions) != expected_players:
            raise ValueError("Missing player positions")

        for position in positions.values():
            if (not isinstance(position, list) or len(position) != 2 or
                    any(type(value) not in (int, float) or
                        not math.isfinite(value) for value in position)):
                raise ValueError("Player position must contain two numbers")

        evidence = data.get("evidence")
        if not isinstance(evidence, list):
            raise ValueError("Missing evidence data")
        seen_ids = set()
        for row in evidence:
            if (not isinstance(row, list) or len(row) != 4 or
                    type(row[0]) is not int or row[0] <= 0 or
                    not isinstance(row[1], str) or not row[1] or
                    (row[2] is not None and not isinstance(row[2], str)) or
                    (row[3] is not None and not isinstance(row[3], str))):
                raise ValueError("Invalid evidence record")
            if row[0] in seen_ids:
                raise ValueError("Duplicate evidence ID")
            seen_ids.add(row[0])

    """Store both positions and a copy of the existing evidence rows."""
    def save_game(self, positions):
        snapshot = {
            "version": 1,
            "player_count": self.player_count,
            "positions": positions,
            "evidence": [list(row) for row in database.get_evidence()],
        }
        self._validate(snapshot)
        database.update_game_state(self.SAVE_KEY, json.dumps(snapshot))
        return True

    """Returns saved positions and restores evidence; None means no save."""
    def load_game(self):
        raw = database.get_game_state(self.SAVE_KEY)
        if raw is None:
            return None
        try:
            snapshot = json.loads(raw)
        except (ValueError, TypeError) as exc:
            raise ValueError("Save data is damaged") from exc
        self._validate(snapshot)
        # Only change the evidence table after the entire snapshot is valid.
        database.replace_evidence(snapshot["evidence"])
        return snapshot["positions"]

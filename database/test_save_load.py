"""Tests use a temporary database so they never touch the team's game.db."""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import database
from save_load_service import SaveLoadService


class SaveLoadTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.old_db_path = database.DB_NAME
        database.DB_NAME = str(Path(self.tmpdir.name) / "test_game.db")
        self.service = SaveLoadService(2)
        database.collect_evidence(1, "Mysterious Letter", "Found in library", "Player 1")
        database.collect_evidence(2, "Broken Watch", "At crime scene", "Player 2")

    def tearDown(self):
        database.DB_NAME = self.old_db_path
        self.tmpdir.cleanup()

    def test_no_save_returns_none_without_changing_evidence(self):
        before = database.get_evidence()
        self.assertIsNone(self.service.load_game())
        self.assertEqual(database.get_evidence(), before)

    def test_two_player_positions_and_evidence_restored(self):
        before_positions = {"player1": [2000, 500], "player2": [2050, 500]}
        self.assertTrue(self.service.save_game(before_positions))

        # Simulate finding another clue after saving.
        database.collect_evidence(3, "Old Key", "Under a rug", "Player 2")
        self.assertEqual(len(database.get_evidence()), 3)

        loaded_positions = self.service.load_game()
        self.assertEqual(loaded_positions, before_positions)
        self.assertEqual([row[0] for row in database.get_evidence()], [1, 2])

    def test_latest_save_overwrites_previous_save(self):
        self.service.save_game({"player1": [100, 100], "player2": [200, 200]})
        self.service.save_game({"player1": [333, 444], "player2": [555, 666]})
        self.assertEqual(self.service.load_game()["player1"], [333, 444])

    def test_single_player_save(self):
        single = SaveLoadService(1)
        single.save_game({"player1": [100.5, 200.25]})
        self.assertEqual(single.load_game(), {"player1": [100.5, 200.25]})

    def test_player_count_mismatch_does_not_overwrite_evidence(self):
        self.service.save_game({"player1": [10, 20], "player2": [30, 40]})
        database.collect_evidence(9, "New Clue", None, "Player 1")
        before = database.get_evidence()
        single = SaveLoadService(1)
        with self.assertRaisesRegex(ValueError, "different number of players"):
            single.load_game()
        self.assertEqual(database.get_evidence(), before)

    def test_invalid_save_does_not_overwrite_evidence(self):
        database.update_game_state("save_slot_1", "{broken json")
        before = database.get_evidence()
        with self.assertRaisesRegex(ValueError, "damaged"):
            self.service.load_game()
        self.assertEqual(database.get_evidence(), before)

    def test_invalid_positions_rejected_before_save(self):
        with self.assertRaisesRegex(ValueError, "position"):
            self.service.save_game({"player1": [2000, 500], "player2": ["x", 500]})
        self.assertIsNone(database.get_game_state("save_slot_1"))

    def test_duplicate_evidence_rejected_without_deleting_existing_rows(self):
        before = database.get_evidence()
        snapshot = {
            "version": 1,
            "player_count": 2,
            "positions": {"player1": [2, 3], "player2": [4, 5]},
            "evidence": [[1, "Clue 1", None, None], [1, "Clue 2", None, None]],
        }
        database.update_game_state("save_slot_1", json.dumps(snapshot))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.service.load_game()
        self.assertEqual(database.get_evidence(), before)

    def test_replace_evidence_rolls_back_on_database_error(self):
        before = database.get_evidence()
        with self.assertRaises(sqlite3.IntegrityError):
            database.replace_evidence([(4, "Valid", None, None), (4, "Duplicate", None, None)])
        self.assertEqual(database.get_evidence(), before)


if __name__ == "__main__":
    unittest.main()

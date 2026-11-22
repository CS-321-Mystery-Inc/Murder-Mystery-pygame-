"""Tests for the Level 1 coin/lever and save support.

Run from the project root: python -m unittest discover -s tests -v
Requires pygame but not any image/audio assets.
"""
import os
import tempfile
import unittest

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame

from scripts.clue import Clue
from scripts.interactable import MovableWall, Switch
from scripts.tilemap import Tilemap, LEVEL_ONE_ITEMS
from database import database
from database.save_load_service import SaveLoadService


class FakeAnimation:
    def copy(self):
        return FakeAnimation()

    def img(self):
        return pygame.Surface((32, 64), pygame.SRCALPHA)


class FakeGame:
    def __init__(self):
        self.assets = {'switch/idle': FakeAnimation(),
                       'switch/flipped': FakeAnimation()}


class FakePlayer:
    def __init__(self, form='corporeal', pos=(0, 0)):
        self.form = form
        self.rect = pygame.Rect(*pos, 35, 64)

    def get_rect(self):
        return self.rect


class LevelOneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_four_unique_placeholder_coins(self):
        self.assertEqual([item['name'] for item in LEVEL_ONE_ITEMS],
                         ['Coin 1', 'Coin 2', 'Coin 3', 'Coin 4'])
        self.assertEqual(len({item['id'] for item in LEVEL_ONE_ITEMS}), 4)
        self.assertTrue(all(item['item_type'] == 'Coin' for item in LEVEL_ONE_ITEMS))

    def test_level_has_floor_and_platforms(self):
        level = Tilemap(FakeGame())
        self.assertIn('32;10', level.tilemap)
        self.assertIn('11;8', level.tilemap)
        self.assertIn('42;8', level.tilemap)

    def test_lever_requires_corporeal_and_opens_once(self):
        game = FakeGame()
        wall = MovableWall(game, (1536, 128), size=(64, 512))
        lever = Switch(game, (2200, 576), linked_wall=wall)
        self.assertFalse(lever.interact(FakePlayer('astral')))
        self.assertFalse(wall.is_open)
        self.assertTrue(lever.interact(FakePlayer('corporeal')))
        self.assertTrue(wall.is_open)
        self.assertIsNone(wall.get_solid_rect())
        self.assertFalse(lever.interact(FakePlayer('corporeal')))
        lever.set_flipped(False)
        self.assertFalse(wall.is_open)
        self.assertIsNotNone(wall.get_solid_rect())

    def test_clue_metadata_and_touch_detection(self):
        img = pygame.Surface((24, 24))
        clue = Clue((100, 200), img, 'Coin 1', 101, 'Coin', 'Test description')
        self.assertEqual(clue.evidence_id, 101)
        self.assertTrue(clue.can_collect(FakePlayer(pos=(105, 201))))
        self.assertFalse(clue.can_collect(FakePlayer(pos=(800, 800))))

    def test_save_restores_coins_and_lever_state(self):
        with tempfile.TemporaryDirectory() as directory:
            old_db = database.DB_NAME
            database.DB_NAME = os.path.join(directory, 'test.db')
            try:
                service = SaveLoadService(1)
                positions = {'player1': [2000, 576]}
                database.collect_evidence(101, 'Coin 1', 'Test', 'Player 1')
                service.save_game(positions, {'lever_flipped': True})
                database.collect_evidence(102, 'Coin 2', 'Test', 'Player 1')
                self.assertEqual(service.load_game(), positions)
                self.assertEqual(service.loaded_level_state, {'lever_flipped': True})
                self.assertEqual([row[0] for row in database.get_evidence()], [101])
                database.clear_evidence()
                self.assertEqual(database.get_evidence(), [])
            finally:
                database.DB_NAME = old_db


if __name__ == '__main__':
    unittest.main()

"""Notebook UI checks: run locally with Pygame installed."""
import os
import unittest

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
import pygame

from gameloop import Game
from scripts.tilemap import LEVEL_ONE_ITEMS


class StubScreen:
    def get_size(self):
        return (960, 540)


class NotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_game(self):
        """Build just the UI state; avoid game asset and sound loading."""
        game = Game.__new__(Game)
        game.screen_width = 1920
        game.screen_height = 1080
        game.display = pygame.Surface((1920, 1080), pygame.SRCALPHA)
        game.screen = StubScreen()
        game.notebook_art = None
        game.notebook_selected_type = 'Coin'
        game.notebook_selected_item = None
        game.clue_catalog = {c['id']: c for c in LEVEL_ONE_ITEMS}
        game.evidence_rows = []
        game.book_title_font = pygame.font.SysFont('Georgia', 44, bold=True)
        game.book_font = pygame.font.SysFont('Georgia', 30)
        game.book_small_font = pygame.font.SysFont('Georgia', 25)
        game.pause_font = pygame.font.SysFont('Arial', 64, bold=True)
        game.menu_font = pygame.font.SysFont('Arial', 40, bold=True)
        game.pause_options = ['RESUME GAME', 'SAVE GAME', 'LOAD GAME', 'QUIT GAME']
        game.pause_selection = 0
        game.pause_status = ''
        game.notebook_icon = None
        game.notebook_hud_rect = pygame.Rect(910, 962, 100, 100)
        game.paused = False
        game.in_notebook = False
        game.freeze_game = lambda: None
        return game

    def test_mouse_coordinates_are_scaled(self):
        game = self.make_game()
        self.assertEqual(game.screen_to_game((480, 270)), (960, 540))

    def test_new_notebook_contains_no_unfound_clue_entries(self):
        game = self.make_game()
        game.draw_notebook()
        self.assertEqual(game.notebook_item_rects, {})
        self.assertEqual(game.notebook_type_rects, {})

    def test_coin_appears_only_after_collection(self):
        game = self.make_game()
        item = LEVEL_ONE_ITEMS[0]
        game.evidence_rows = [(item['id'], item['name'], item['description'], 'Player 1')]
        game.draw_notebook()
        self.assertEqual(list(game.notebook_item_rects), [item['id']])
        self.assertEqual(game.notebook_selected_item, item['id'])
        self.assertEqual(list(game.notebook_type_rects), ['Coin'])

    def test_close_goes_directly_back_to_gameplay(self):
        game = self.make_game()
        game.open_notebook()
        self.assertTrue(game.paused)
        self.assertTrue(game.in_notebook)
        game.close_notebook()
        self.assertFalse(game.paused)
        self.assertFalse(game.in_notebook)

    def test_all_four_clues_have_messages(self):
        self.assertEqual(len(LEVEL_ONE_ITEMS), 4)
        self.assertEqual([c['name'] for c in LEVEL_ONE_ITEMS],
                         ['Coin 1', 'Coin 2', 'Coin 3', 'Coin 4'])
        self.assertTrue(all(len(c['description']) > 35 for c in LEVEL_ONE_ITEMS))


if __name__ == '__main__':
    unittest.main()

"""
Psychic Detective - Level 1, bottom-center notebook HUD, and save/load.

Place at the project root alongside scripts/, menus/, and database/.
The closed-book HUD icon is loaded from data/images/notebook.png when present.
"""

import os
import sqlite3
import sys

import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap, LEVEL_ONE_ITEMS, LEVEL_TWO_ITEMS
from scripts.interactable import Switch, MovableWall
from scripts.clue import Clue
from menus.mainmenu import MainMenu
from database import database as db
from database.save_load_service import SaveLoadService


class Game:
    def __init__(self, player_count=1):
        pygame.init()
        pygame.display.set_caption('Psychic Detective')
        self.screen_width, self.screen_height = 1920, 1080
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.display = pygame.Surface((self.screen_width, self.screen_height))
        self.main_menu = MainMenu(self.screen)
        self.clock = pygame.time.Clock()
        self.game_started = False
        self.menu_status = ''

        self.numplayers = player_count
        self.save_load_service = SaveLoadService(player_count)
        self.movement1 = [False, False]
        self.movement2 = [False, False]

        # Stores assets used in-game.
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'corporeal_player': load_image('entities/corporeal/corporeal_player.png'),
            'astral_player': load_image('entities/astral/astral_player.png'),
            'background': load_image('background5.png'),
            'floor': load_images('tiles/floor'),
            'enchanted_parchment': pygame.transform.scale_by(load_image('entities/clues/enchanted_parchment.png'), 0.5),
            'dagger': pygame.transform.scale_by(load_image('entities/clues/dagger.png'), 0.5),
            'broken_brooch': pygame.transform.scale_by(load_image('entities/clues/broken_brooch.png'), 0.5),
            'justice_tarot_card': pygame.transform.scale_by(load_image('entities/clues/justice_tarot_card.png'), 0.5),
            'embroidery_scissors': pygame.transform.scale_by(load_image('entities/clues/embroidery_scissors.png'), 0.5),
            'small_sweater': pygame.transform.scale_by(load_image('entities/clues/small_sweater.png'), 0.5),
            'emperor_tarot_card': pygame.transform.scale_by(load_image('entities/clues/emperor_tarot_card.png'), 0.5),
            'corporeal/idle': Animation(load_images('entities/corporeal/idle'), img_dur=6),
            'corporeal/run': Animation(load_images('entities/corporeal/run'), img_dur=4),
            'astral/idle': Animation(load_images('entities/astral/idle'), img_dur=6),
            'astral/run': Animation(load_images('entities/astral/run'), img_dur=4),
            'switch/idle': Animation(load_images('entities/lever/idle'), img_dur=6),
            'switch/flipped': Animation(load_images('entities/lever/flipped'), img_dur=6),
            'drawer': load_image('entities/drawer.png'),
            'key': pygame.transform.scale_by(load_image('entities/clues/key.png'), 0.5),
        }

        # The user-provided closed-book icon lives in the standard assets folder.
        notebook_icon_path = 'data/images/notebook.png'
        self.notebook_icon = (load_image('notebook.png')
                              if os.path.isfile(notebook_icon_path) else None)
        if self.notebook_icon is not None:
            self.notebook_icon = pygame.transform.smoothscale(self.notebook_icon, (76, 76))
        notebook_path = 'menus/images/notebook_1.png'
        self.notebook_art = None
        if os.path.isfile(notebook_path):
            self.notebook_art = pygame.transform.scale_by(
                pygame.image.load(notebook_path).convert_alpha(), 5)

        self.player = PhysicsEntity(self, 'Player', (2000, 576), (35, 64), 'corporeal')
        if self.numplayers == 2:
            self.player2 = PhysicsEntity(self, 'Player2', (2050, 576), (35, 64), 'astral')
        self.tilemap = Tilemap(self, tile_size=64)
        self.scroll = [self.player.pos[0] - self.screen_width // 2,
                       self.player.pos[1] - self.screen_height // 2]

        self.interactables = pygame.sprite.Group()

        # Solid barrier between the ceiling (y=128) and ground (y=640).
        self.secret_wall = MovableWall(self, (1536, 128), size=(64, 512))
        self.lever = Switch(self, (2200, 576), linked_wall=self.secret_wall)
        self.interactables.add(self.secret_wall, self.lever)
        self.lever_prompt_dismissed = False
        drawer_img = self.assets['drawer']
        self.drawer_pos = (300, 640 - drawer_img.get_height())
        self.drawer_rect = pygame.Rect(
            self.drawer_pos[0],
            self.drawer_pos[1],
            drawer_img.get_width(),
            drawer_img.get_height(),
        )
        self.drawer_opened = False
        self.drawer_prompt_dismissed = False

        self.clue_catalog = {item['id']: item for item in LEVEL_ONE_ITEMS}
        self.clues = pygame.sprite.Group()
        self.collected_clues = []  # Legacy list; the database is the source of truth
        self.spawn_clues()
        self.refresh_collected()

        self.paused = False
        self.in_notebook = False

        # Esc still brings up the original-style dark pause menu. The notebook
        # is accessible directly from the bottom-center in-game inventory slot.
        self.pause_options = ['RESUME GAME', 'SAVE GAME', 'LOAD GAME', 'QUIT GAME']
        self.pause_selection = 0
        self.pause_status = ''
        self.pause_option_rects = []

        # Leaves the notebook high enough to be fully visible in a 1920x1080 window.
        self.notebook_hud_rect = pygame.Rect(self.screen_width // 2 - 50,
                                             self.screen_height - 270, 100, 100)
        self.notebook_close_rect = pygame.Rect(1440, 153, 100, 54)
        self.notebook_type_rects = {}
        self.notebook_item_rects = {}
        self.notebook_selected_item = None

        # Evidence pickup notifications appear briefly over gameplay.
        # Queue them so collecting multiple items quickly does not skip any text.
        self.collection_notifications = []
        self.collection_notification_started_at = None

        self.pause_font = pygame.font.SysFont('Arial', 64, bold=True)
        self.menu_font = pygame.font.SysFont('Arial', 40, bold=True)
        self.book_title_font = pygame.font.SysFont('Georgia', 44, bold=True)
        self.book_font = pygame.font.SysFont('Georgia', 30)
        self.book_small_font = pygame.font.SysFont('Georgia', 25)
        self.hint_font = pygame.font.SysFont('Arial', 29, bold=True)

    # ----- Level items and persistence -----

    def spawn_clues(self):
        # Instantiates the current level's evidence from one editable catalog.
        self.clues.empty()

        # Level 1
        for i in range(len(LEVEL_ONE_ITEMS)):
            if (i == 0 or i == 1): # Enchanted Parchments
                x = int(LEVEL_ONE_ITEMS[i]['center_x'] - self.assets['enchanted_parchment'].get_width() / 2)
                y = int(LEVEL_ONE_ITEMS[i]['surface_y'] - self.assets['enchanted_parchment'].get_height())
                self.clues.add(Clue((x, y), self.assets['enchanted_parchment'], LEVEL_ONE_ITEMS[i]['name'],
                    evidence_id=LEVEL_ONE_ITEMS[i]['id'], item_type=LEVEL_ONE_ITEMS[i]['item_type'],
                    description=LEVEL_ONE_ITEMS[i]['description']))
            elif (i == 2): # Dagger
                x = int(LEVEL_ONE_ITEMS[i]['center_x'] - self.assets['dagger'].get_width() / 2)
                y = int(LEVEL_ONE_ITEMS[i]['surface_y'] - self.assets['dagger'].get_height())
                self.clues.add(Clue((x, y), self.assets['dagger'], LEVEL_ONE_ITEMS[i]['name'],
                    evidence_id=LEVEL_ONE_ITEMS[i]['id'], item_type=LEVEL_ONE_ITEMS[i]['item_type'],
                    description=LEVEL_ONE_ITEMS[i]['description']))
            elif (i == 3): # Broken Brooch
                x = int(LEVEL_ONE_ITEMS[i]['center_x'] - self.assets['broken_brooch'].get_width() / 2)
                y = int(LEVEL_ONE_ITEMS[i]['surface_y'] - self.assets['broken_brooch'].get_height())
                self.clues.add(Clue((x, y), self.assets['broken_brooch'], LEVEL_ONE_ITEMS[i]['name'],
                    evidence_id=LEVEL_ONE_ITEMS[i]['id'], item_type=LEVEL_ONE_ITEMS[i]['item_type'],
                    description=LEVEL_ONE_ITEMS[i]['description']))
            elif (i == 4): # Justice Tarot Card
                x = int(LEVEL_ONE_ITEMS[i]['center_x'] - self.assets['justice_tarot_card'].get_width() / 2)
                y = int(LEVEL_ONE_ITEMS[i]['surface_y'] - self.assets['justice_tarot_card'].get_height())
                self.clues.add(Clue((x, y), self.assets['justice_tarot_card'], LEVEL_ONE_ITEMS[i]['name'],
                    evidence_id=LEVEL_ONE_ITEMS[i]['id'], item_type=LEVEL_ONE_ITEMS[i]['item_type'],
                    description=LEVEL_ONE_ITEMS[i]['description']))
            elif LEVEL_ONE_ITEMS[i]['id'] == 106 and self.drawer_opened:  # Key
                x = int(LEVEL_ONE_ITEMS[i]['center_x'] - self.assets['key'].get_width() / 2)
                y = int(LEVEL_ONE_ITEMS[i]['surface_y'] - self.assets['key'].get_height())
                self.clues.add(Clue(
                    (x, y),
                    self.assets['key'],
                    LEVEL_ONE_ITEMS[i]['name'],
                    evidence_id=LEVEL_ONE_ITEMS[i]['id'],
                    item_type=LEVEL_ONE_ITEMS[i]['item_type'],
                    description=LEVEL_ONE_ITEMS[i]['description'],
                ))

    def refresh_collected(self):
        # Keeps notebook and visible pickups consistent with database evidence.
        self.evidence_rows = db.get_evidence()
        collected_ids = {row[0] for row in self.evidence_rows}
        for clue in list(self.clues):
            if clue.evidence_id in collected_ids:
                clue.kill()
        self.collected_clues = [row[1] for row in self.evidence_rows]

    def start_new_game(self, player_count):
        self.numplayers = player_count
        self.save_load_service = SaveLoadService(player_count)
        if self.numplayers == 2 and not hasattr(self, 'player2'):
            self.player2 = PhysicsEntity(self, 'Player2', (2050, 576), (35, 64), 'astral')
        self.reset_level(clear_evidence=True)
        self.game_started = True

    def reset_level(self, clear_evidence=True):
        # New Game resets coins and lever without deleting the existing save slot.
        if clear_evidence:
            db.clear_evidence()
        self.player.pos = [2000, 576]
        self.player.form = 'corporeal'
        self.player.set_action('idle')
        self.player.jumps = 1
        self.player.get_rect()
        self.player.velocity = [0, 0]
        if self.numplayers == 2:
            self.player2.pos = [2050, 576]
            self.player2.form = 'astral'
            self.player2.set_action('idle')
            self.player2.jumps = 2
            self.player2.get_rect()
            self.player2.velocity = [0, 0]
        self.lever.set_flipped(False)
        self.lever_prompt_dismissed = False
        self.drawer_opened = False
        self.drawer_prompt_dismissed = False
        self.spawn_clues()
        self.refresh_collected()
        self.scroll = [self.player.pos[0] - self.screen_width // 2,
                       self.player.pos[1] - self.screen_height // 2]
        self.freeze_game()
        self.paused = False
        self.in_notebook = False
        self.pause_status = ''
        self.notebook_selected_item = None
        self.collection_notifications.clear()
        self.collection_notification_started_at = None

    def collect_clue(self, clue, player_label):
        # Persists first, then removes the object from the level.
        if clue not in self.clues:
            return False
        try:
            db.collect_evidence(clue.evidence_id, clue.item_name,
                                clue.description, player_label)
        except sqlite3.Error as exc:
            print(f'Could not collect {clue.item_name}: {exc}')
            return False
        clue.kill()
        self.refresh_collected()
        self.collection_notifications.append(f'{clue.item_name} collected')
        print(f'{player_label} collected {clue.item_name}')
        return True

    def collect_near_players(self):
        for clue in list(self.clues):
            if clue.can_collect(self.player):
                self.collect_clue(clue, 'Player 1')
            elif self.numplayers == 2 and clue.can_collect(self.player2):
                self.collect_clue(clue, 'Player 2')

    def capture_positions(self):
        result = {'player1': list(self.player.pos)}
        if self.numplayers == 2:
            result['player2'] = list(self.player2.pos)
        return result

    def restore_positions(self, positions):
        self.player.pos = list(positions['player1'])
        self.player.get_rect()
        self.player.velocity = [0, 0]
        if self.numplayers == 2:
            self.player2.pos = list(positions['player2'])
            self.player2.get_rect()
            self.player2.velocity = [0, 0]
        self.freeze_game()

    def save_game(self):
        try:
            self.save_load_service.save_game(
                self.capture_positions(),
                level_state={'lever_flipped': self.lever.is_flipped, 'drawer_opened': self.drawer_opened},
            )
            self.pause_status = 'Game saved successfully!'
            print(self.pause_status)
            return True
        except (ValueError, sqlite3.Error) as exc:
            self.pause_status = f'Could not save game: {exc}'
            print(self.pause_status)
            return False

    def load_game(self):
        try:
            positions = self.save_load_service.load_game()
            if positions is None:
                self.pause_status = 'No saved game found.'
                return False
            self.restore_positions(positions)
            state = self.save_load_service.loaded_level_state
            self.lever.set_flipped(state.get('lever_flipped', False))
            self.drawer_opened = bool(state.get('drawer_opened', False))
            self.drawer_prompt_dismissed = self.drawer_opened
            self.spawn_clues()
            self.refresh_collected()
            self.collection_notifications.clear()
            self.collection_notification_started_at = None
            self.pause_status = 'Game loaded successfully!'
            print(self.pause_status)
            return True
        except (ValueError, sqlite3.Error) as exc:
            self.pause_status = f'Could not load game: {exc}'
            print(self.pause_status)
            return False

    def freeze_game(self):
        self.movement1 = [False, False]
        self.movement2 = [False, False]
        self.player.velocity = [0, 0]
        if self.numplayers == 2:
            self.player2.velocity = [0, 0]

    # ----- UI -----

    def draw_text(self, text, font, color, x, y, center=False):
        img = font.render(text, True, color)
        rect = img.get_rect(center=(x, y)) if center else img.get_rect(topleft=(x, y))
        self.display.blit(img, rect)
        return rect

    def draw_wrapped(self, text, font, color, x, y, max_width, line_height=42):
        # Renders descriptions without relying on hard-coded line breaks.
        words = text.split()
        line = ''
        for word in words:
            candidate = (line + ' ' + word).strip()
            if line and font.size(candidate)[0] > max_width:
                self.draw_text(line, font, color, x, y)
                y += line_height
                line = word
            else:
                line = candidate
        if line:
            self.draw_text(line, font, color, x, y)
            y += line_height
        return y

    def draw_notebook_hud(self):
        # Always-owned inventory slot; clicking it pauses play and opens the book.
        rect = self.notebook_hud_rect
        hovered = rect.collidepoint(self.screen_to_game(pygame.mouse.get_pos()))
        shadow = rect.move(0, 4)
        pygame.draw.rect(self.display, (12, 11, 13), shadow, border_radius=13)
        pygame.draw.rect(self.display, (45, 43, 49), rect, border_radius=12)
        pygame.draw.rect(self.display, (234, 202, 135) if hovered else (145, 141, 134),
                         rect, width=4, border_radius=12)
        if self.notebook_icon is not None:
            self.display.blit(self.notebook_icon,
                              self.notebook_icon.get_rect(center=rect.center))
        else:
            # Visual fallback until data/images/notebook.png arrives.
            book = pygame.Rect(0, 0, 58, 69)
            book.center = rect.center
            pygame.draw.rect(self.display, (141, 82, 57), book, border_radius=6)
            pygame.draw.rect(self.display, (237, 218, 173), book.inflate(-11, -7), 2,
                             border_radius=2)
            pygame.draw.line(self.display, (91, 49, 34),
                             (book.left + 11, book.top + 4),
                             (book.left + 11, book.bottom - 4), 3)
        if hovered:
            tooltip = self.book_small_font.render('Open notebook', True, (248, 240, 219))
            tip_rect = tooltip.get_rect(midbottom=(rect.centerx, rect.top - 12))
            bg = tip_rect.inflate(20, 12)
            pygame.draw.rect(self.display, (32, 29, 31), bg, border_radius=6)
            self.display.blit(tooltip, tip_rect)

    def draw_pause_menu(self):
        # Original dark menu style: plain gray text, gold selection, no cards.
      overlay = pygame.Surface(
          (self.screen_width, self.screen_height), pygame.SRCALPHA
      )
      overlay.fill((0, 0, 0, 150))
      self.display.blit(overlay, (0, 0))
      self.draw_text(
          "GAME PAUSED",
          self.pause_font,
          (255, 255, 255),
          self.screen_width // 2,
          self.screen_height // 2,
          True,
      )

      mouse_pos = self.screen_to_game(pygame.mouse.get_pos())
      option_rects = []
      for index, option in enumerate(self.pause_options):
        y = self.screen_height // 2 + 50 + index * 60
        # Measure with selection markers so hover boxes match highlighted text
        sample_rect = self.menu_font.render(
            f"> {option} <", True, (255, 190, 0)
        ).get_rect(center=(self.screen_width // 2, y))
        hit_rect = sample_rect.inflate(48, 18)
        option_rects.append(hit_rect)
        if hit_rect.collidepoint(mouse_pos):
          self.pause_selection = index

      self.pause_option_rects = option_rects
      for index, option in enumerate(self.pause_options):
        display_string = (
            f"> {option} <" if index == self.pause_selection else option
        )
        color = (
            (255, 190, 0) if index == self.pause_selection else (160, 160, 160)
        )
        y = self.screen_height // 2 + 50 + index * 60
        self.draw_text(
            display_string, self.menu_font, color, self.screen_width // 2, y, True
        )

      if self.pause_status:
        self.draw_text(
            self.pause_status,
            self.book_small_font,
            (255, 255, 255),
            self.screen_width // 2,
            self.screen_height // 2 + 50 + len(self.pause_options) * 60,
            True,
        )
                           
    def draw_collection_notification(self):
        # Shows each newly collected clue's name for about 2.5 seconds.
        if not self.collection_notifications:
            return
        now = pygame.time.get_ticks()
        if self.collection_notification_started_at is None:
            self.collection_notification_started_at = now
        elapsed = now - self.collection_notification_started_at
        duration = 2500
        if elapsed >= duration:
            self.collection_notifications.pop(0)
            self.collection_notification_started_at = now
            if not self.collection_notifications:
                self.collection_notification_started_at = None
                return
            elapsed = 0

        message = self.collection_notifications[0]
        text = self.menu_font.render(message, True, (255, 243, 214))
        panel_rect = text.get_rect(center=(self.screen_width // 2, 230)).inflate(55, 26)
        fade = min(1.0, max(0.0, (duration - elapsed) / 350))
        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (25, 22, 31, int(212 * fade)),
                         panel.get_rect(), border_radius=12)
        pygame.draw.rect(panel, (210, 177, 118, int(225 * fade)),
                         panel.get_rect(), width=2, border_radius=12)
        self.display.blit(panel, panel_rect.topleft)
        text.set_alpha(int(255 * fade))
        self.display.blit(text, text.get_rect(center=panel_rect.center))

    def draw_notebook(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.display.blit(overlay, (0, 0))
        if self.notebook_art is not None:
            self.display.blit(self.notebook_art, (315, -90))

        # Retains the two-page paper notebook design from the prior version.
        pygame.draw.rect(self.display, (111, 70, 39), (341, 103, 1238, 858), border_radius=16)
        pygame.draw.rect(self.display, (244, 234, 206), (370, 135, 573, 790), border_radius=9)
        pygame.draw.rect(self.display, (250, 242, 220), (962, 135, 580, 790), border_radius=9)
        pygame.draw.line(self.display, (175, 147, 110), (951, 139), (951, 920), 9)
        ink = (67, 48, 39)
        muted = (118, 99, 85)
        self.draw_text('INVESTIGATION NOTEBOOK', self.book_title_font,
                       ink, 955, 190, True)
        self.notebook_close_rect = pygame.Rect(1410, 223, 110, 48)
        pygame.draw.rect(self.display, (123, 81, 56), self.notebook_close_rect, border_radius=8)
        self.draw_text('CLOSE', self.book_small_font, (255, 247, 231),
                       self.notebook_close_rect.centerx,
                       self.notebook_close_rect.centery, True)

        self.notebook_type_rects = {}  # Kept empty for compatibility with mouse handling.
        self.notebook_item_rects = {}
        # Shows only clues belonging to the current level. Older database rows
        # (such as example evidence) must not introduce an "Other Evidence" tab.
        visible_rows = [row for row in self.evidence_rows if row[0] in self.clue_catalog]
        # Newly started notebooks stay genuinely blank until something is found.
        if not visible_rows:
            return

        collected = {row[0]: row for row in visible_rows}
        if self.notebook_selected_item not in collected:
            self.notebook_selected_item = visible_rows[0][0]

        # One straightforward list; no item-type categories or "Other Evidence".
        self.draw_text('COLLECTED CLUES', self.book_font, ink, 415, 290)
        for index, row in enumerate(visible_rows[:8]):
            item_id, item_name = row[0], row[1]
            rect = pygame.Rect(413, 351 + index * 65, 505, 54)
            self.notebook_item_rects[item_id] = rect
            if item_id == self.notebook_selected_item:
                pygame.draw.rect(self.display, (221, 205, 165), rect, border_radius=6)
            self.draw_text(item_name, self.book_font, ink, rect.x + 14, rect.y + 8)

        self.draw_text('A NOTE FROM THE SCENE', self.book_font, ink, 1015, 305)
        row = collected[self.notebook_selected_item]
        self.draw_text(row[1], self.book_title_font, ink, 1015, 385)
        source = self.clue_catalog.get(row[0], {})
        self.draw_wrapped(source.get('description') or row[2] or
                          'No message recorded.', self.book_font, ink,
                          1015, 485, 460)

    def screen_to_game(self, pos):
        # Maps mouse coordinates to 1920x1080 game coordinates if scaled.
        width, height = self.screen.get_size()
        return (int(pos[0] * self.screen_width / width),
                int(pos[1] * self.screen_height / height))

    def nearby_corporeal_players(self):
        candidates = [self.player]
        if self.numplayers == 2:
            candidates.append(self.player2)
        return [p for p in candidates if p.form == 'corporeal'
                and self.lever.rect.inflate(110, 50).colliderect(p.get_rect())]

    def nearby_corporeal_players_for_drawer(self):
        candidates = [self.player]
        if self.numplayers == 2:
            candidates.append(self.player2)
        return [p for p in candidates if p.form == 'corporeal'
                and self.drawer_rect.inflate(110, 50).colliderect(p.get_rect())]

    def draw_drawer_prompt(self, render_scroll):
        if (self.drawer_opened or getattr(self, 'drawer_prompt_dismissed', False)
                or not self.nearby_corporeal_players_for_drawer()):
            return
        text = 'Press E to open drawer'
        surface = self.hint_font.render(text, True, (255, 248, 220))
        center_x = self.drawer_rect.centerx - render_scroll[0]
        center_y = self.drawer_rect.top - render_scroll[1] - 42
        box = surface.get_rect(center=(center_x, center_y)).inflate(24, 16)
        box.clamp_ip(pygame.Rect(10, 10, self.screen_width - 20, self.screen_height - 20))
        panel = pygame.Surface(box.size, pygame.SRCALPHA)
        panel.fill((30, 25, 20, 230))
        self.display.blit(panel, box.topleft)
        self.display.blit(surface, surface.get_rect(center=box.center))

    def draw_lever_prompt(self, render_scroll):
        if getattr(self, 'lever_prompt_dismissed', False) or not self.nearby_corporeal_players():
            return
        text = 'Press E to pull lever'
        surface = self.hint_font.render(text, True, (255, 248, 220))
        center_x = self.lever.rect.centerx - render_scroll[0]
        center_y = self.lever.rect.top - render_scroll[1] - 42
        box = surface.get_rect(center=(center_x, center_y)).inflate(24, 16)
        box.clamp_ip(pygame.Rect(10, 10, self.screen_width - 20, self.screen_height - 20))
        panel = pygame.Surface(box.size, pygame.SRCALPHA)
        panel.fill((30, 25, 20, 230))
        self.display.blit(panel, box.topleft)
        self.display.blit(surface, surface.get_rect(center=box.center))

    def open_notebook(self):
        self.in_notebook = True
        self.paused = True  # Both flags ensure NO world updates while reading.
        self.freeze_game()
        # Shows a clue's contents immediately on opening if found.
        current_level_rows = [row for row in self.evidence_rows
                              if row[0] in self.clue_catalog]
        self.notebook_selected_item = (current_level_rows[0][0]
                                       if current_level_rows else None)

    def close_notebook(self):
        self.in_notebook = False
        self.paused = False  # Returns straight to gameplay; no Esc/pause detour.
        self.freeze_game()

    def activate_pause_option(self, index):
        option = self.pause_options[index]
        if option == "RESUME GAME":
            self.paused = False
            self.pause_status = ""
        elif option == "SAVE GAME":
            self.save_game()
        elif option == "LOAD GAME":
            if self.load_game():
                self.paused = False
                self.pause_status = ""
                self.freeze_game()
        elif option == "QUIT GAME":
            pygame.quit()
            sys.exit()

    # ----- Frame and input loop -----

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not self.game_started:
                action = self.main_menu.handle_event(event)
                if action and action[0] == 'start':
                    self.start_new_game(action[1])
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = self.screen_to_game(event.pos)
                if self.in_notebook:
                    if self.notebook_close_rect.collidepoint(pos):
                        self.close_notebook()
                    else:
                        for kind, rect in self.notebook_type_rects.items():
                            if rect.collidepoint(pos):
                                self.notebook_selected_type = kind
                                self.notebook_selected_item = None
                                break
                        else:
                            for item_id, rect in self.notebook_item_rects.items():
                                if rect.collidepoint(pos):
                                    self.notebook_selected_item = item_id
                                    break
                elif self.paused:
                    for index, rect in enumerate(self.pause_option_rects):
                        if rect.collidepoint(pos):
                            self.pause_selection = index
                            self.activate_pause_option(index)
                            break
                elif self.notebook_hud_rect.collidepoint(pos):
                    self.open_notebook()
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.in_notebook:
                        self.close_notebook()
                    elif self.paused:
                        self.paused = False
                        self.freeze_game()
                    else:
                        self.paused = True
                        self.freeze_game()
                        self.pause_selection = 0
                        self.pause_status = ''
                    continue
                if self.in_notebook:
                    continue  # Never move, jump, dash or interact while reading.
                if self.paused:
                    if event.key == pygame.K_UP:
                        self.pause_selection = (self.pause_selection - 1) % len(self.pause_options)
                    elif event.key == pygame.K_DOWN:
                        self.pause_selection = (self.pause_selection + 1) % len(self.pause_options)
                    elif event.key == pygame.K_RETURN:
                        self.activate_pause_option(self.pause_selection)
                    continue

                if event.key == pygame.K_LEFT:
                    self.movement1[0] = True
                elif event.key == pygame.K_RIGHT:
                    self.movement1[1] = True
                elif event.key == pygame.K_UP:
                    self.player.jump()
                elif event.key == pygame.K_SPACE:
                    self.player.dash(pygame.time.get_ticks(), self.tilemap)
                    if self.numplayers == 2:
                        self.player2.dash(pygame.time.get_ticks(), self.tilemap)
                elif event.key == pygame.K_l and self.numplayers == 1:
                    self.player.swap_form()
                elif event.key == pygame.K_e:
                    self.collect_near_players()
                    for p in self.nearby_corporeal_players():
                        if self.lever.interact(p):
                            self.lever_prompt_dismissed = True
                            print('Lever pulled. Passage opened!')
                            break
                    if (not self.drawer_opened
                            and self.nearby_corporeal_players_for_drawer()):
                        self.drawer_opened = True
                        self.drawer_prompt_dismissed = True
                        self.spawn_clues()
                        self.refresh_collected()
                        print('Drawer opened!')
                elif self.numplayers == 2:
                    if event.key == pygame.K_a:
                        self.movement2[0] = True
                    elif event.key == pygame.K_d:
                        self.movement2[1] = True
                    elif event.key == pygame.K_w:
                        self.player2.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.movement1[0] = False
                elif event.key == pygame.K_RIGHT:
                    self.movement1[1] = False
                if self.numplayers == 2:
                    if event.key == pygame.K_a:
                        self.movement2[0] = False
                    elif event.key == pygame.K_d:
                        self.movement2[1] = False

    def draw_gameplay(self):
        self.display.fill((0, 0, 0))
        scaled_bg = pygame.transform.scale(self.assets['background'], self.display.get_size())
        self.display.blit(scaled_bg, (0, 0))

        playing = not self.paused and not self.in_notebook
        if playing:
            if self.numplayers == 1:
                target_x, target_y = self.player.get_rect().center
            else:
                p1 = self.player.get_rect().center
                p2 = self.player2.get_rect().center
                target_x, target_y = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
            self.scroll[0] += (target_x - self.screen_width / 2 - self.scroll[0]) / 20
            self.scroll[1] += (target_y - self.screen_height / 2 - self.scroll[1]) / 20
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

        self.tilemap.render(self.display, offset=render_scroll)
        self.display.blit(self.assets['drawer'], (self.drawer_pos[0] - render_scroll[0],
                                                  self.drawer_pos[1] - render_scroll[1]))
        for clue in self.clues:
            self.display.blit(clue.image, (clue.pos[0] - render_scroll[0],
                                           clue.pos[1] - render_scroll[1]))
        for item in self.interactables:
            if playing:
                item.update()
            self.display.blit(item.image, (item.pos[0] - render_scroll[0],
                                           item.pos[1] - render_scroll[1]))

        if playing:
            self.player.update(self.tilemap,
                               ((self.movement1[1] - self.movement1[0]) * 4, 0))
            if self.numplayers == 2:
                self.player2.update(self.tilemap,
                                    ((self.movement2[1] - self.movement2[0]) * 4, 0))
            self.collect_near_players()
        self.player.render(self.display, offset=render_scroll)
        if self.numplayers == 2:
            self.player2.render(self.display, offset=render_scroll)

        if playing:
            self.draw_lever_prompt(render_scroll)
            self.draw_drawer_prompt(render_scroll)
            self.draw_notebook_hud()
            self.draw_collection_notification()
        if self.in_notebook:
            self.draw_notebook()
        elif self.paused:
            self.draw_pause_menu()

    def run(self):
        # Keeps the team's audio where available; menu and game remain usable.
        # If the optional sound files are not installed on a teammate's machine.
        intro = pencil = None
        try:
            intro = pygame.mixer.Sound('data/audio/intro.mp3')
            intro.play(loops=-1)
            pencil = pygame.mixer.Sound('data/audio/pencil.mp3')
        except (pygame.error, FileNotFoundError):
            pass

        while True:
            if not self.game_started:
                action = self.main_menu.draw()
                if self.menu_status:
                    status = self.menu_font.render(self.menu_status, True, (255, 255, 255))
                    self.screen.blit(status, status.get_rect(center=(960, 925)))
                if isinstance(action, tuple) and action[0] == 'start':
                    self.start_new_game(action[1])
                    self.menu_status = ''
                    if pencil:
                        pencil.play()
                elif action == 'newgame':
                    self.start_new_game(1)
                    self.menu_status = ''
                    if pencil:
                        pencil.play()
                elif action == 'resume':
                    if self.load_game():
                        self.game_started = True
                        self.paused = False
                        self.menu_status = ''
                        if pencil:
                            pencil.play()
                    else:
                        self.menu_status = self.pause_status
                elif action == 'quit':
                    pygame.quit()
                    sys.exit()
            else:
                self.draw_gameplay()

            self.handle_events()
            if self.game_started:
                self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    Game().run()

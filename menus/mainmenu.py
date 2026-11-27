import sys
import pygame
from . import button


class MainMenu:
  def __init__(self, screen):
    self.screen = screen
    self.state = "main"  # "main", "player_select", or "options"

    self.title_img = pygame.transform.scale_by(
        pygame.image.load("menus/images/title.png").convert_alpha(), 2.5
    )
    self.newgame_img = pygame.image.load("menus/images/newgame.png").convert_alpha()
    self.options_img = pygame.image.load("menus/images/options.png").convert_alpha()
    self.quit_img = pygame.image.load("menus/images/quit.png").convert_alpha()
    self.back_img = pygame.image.load("menus/images/back.png").convert_alpha()

    width, height = self.screen.get_size()
    cx = width // 2

    # Stack New Game, Options, and Quit Game evenly near the center
    self.newgame_button = button.Button(
        cx - int(self.newgame_img.get_width() * 1.5) // 2,
        100,
        self.newgame_img,
        1.5,
    )
    self.options_button = button.Button(
        cx - int(self.options_img.get_width() * 1.5) // 2,
        180,
        self.options_img,
        1.5,
    )
    self.quit_button = button.Button(
        cx - int(self.quit_img.get_width() * 1.5) // 2,
        260,
        self.quit_img,
        1.5,
    )
    self.back_button = button.Button(
        cx - int(self.back_img.get_width() * 1.5) // 2,
        height - 170,
        self.back_img,
        1.5,
    )

    # Matches your pause menu styling
    self.heading_font = pygame.font.SysFont("Arial", 64, bold=True)
    self.option_font = pygame.font.SysFont("Arial", 40, bold=True)
    self.hint_font = pygame.font.SysFont("Arial", 28, bold=True)

    self.player_selection = 0  # 0 -> 1 Player, 1 -> 2 Players
    self.player_option_rects = []

  def handle_event(self, event):
    """Handle keyboard and mouse clicks for sub-menus."""
    if self.state == "player_select":
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          self.state = "main"
        elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
          self.player_selection = 1 - self.player_selection
        elif event.key in (pygame.K_1, pygame.K_KP1):
          return ("start", 1)
        elif event.key in (pygame.K_2, pygame.K_KP2):
          return ("start", 2)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
          return ("start", self.player_selection + 1)

      elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for index, (count, rect) in enumerate(self.player_option_rects):
          if rect.collidepoint(event.pos):
            self.player_selection = index
            return ("start", count)

    elif self.state == "options":
      if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        self.state = "main"

    return None

  def _draw_centered_text(self, text, font, color, x, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    self.screen.blit(surf, rect)
    return rect

  def draw(self):
    self.screen.fill((0, 0, 0))
    width, height = self.screen.get_size()
    cx = width // 2

    if self.state == "main":
      self.screen.blit(
          self.title_img, (cx - self.title_img.get_width() // 2, -400)
      )
      if self.newgame_button.draw(self.screen):
        self.state = "player_select"
        self.player_selection = 0
      if self.options_button.draw(self.screen):
        self.state = "options"
      if self.quit_button.draw(self.screen):
        pygame.quit()
        sys.exit()
      return None

    if self.state == "player_select":
      self._draw_centered_text(
          "HOW MANY PLAYERS?", self.heading_font, (255, 255, 255), cx, height // 2 - 90
      )
      mouse_pos = pygame.mouse.get_pos()
      self.player_option_rects = []

      for index, (count, label) in enumerate(((1, "1 PLAYER"), (2, "2 PLAYERS"))):
        y = height // 2 + 10 + index * 70
        base_surf = self.option_font.render(f"> {label} <", True, (255, 190, 0))
        hit_rect = base_surf.get_rect(center=(cx, y)).inflate(48, 18)
        if hit_rect.collidepoint(mouse_pos):
          self.player_selection = index

        is_selected = self.player_selection == index
        display_text = f"> {label} <" if is_selected else label
        color = (255, 190, 0) if is_selected else (160, 160, 160)
        self._draw_centered_text(display_text, self.option_font, color, cx, y)
        self.player_option_rects.append((count, hit_rect))

      self._draw_centered_text(
          "Press 1 / 2 or click an option  |  ESC to go back",
          self.hint_font,
          (140, 140, 140),
          cx,
          height // 2 + 180,
      )
      if self.back_button.draw(self.screen):
        self.state = "main"
      return None

    if self.state == "options":
      self._draw_centered_text(
          "OPTIONS", self.heading_font, (255, 255, 255), cx, height // 2 - 140
      )
      self._draw_centered_text(
          "P1: Arrow Keys + Space (Dash) + E (Interact) + L (Swap Form in 1P)",
          self.hint_font,
          (200, 200, 200),
          cx,
          height // 2 - 30,
      )
      self._draw_centered_text(
          "P2: W / A / D + Space (Dash) + E (Interact)",
          self.hint_font,
          (200, 200, 200),
          cx,
          height // 2 + 25,
      )
      if self.back_button.draw(self.screen):
        self.state = "main"
      return None

    return None

# pygame.init()

# #create game window
# SCREEN_WIDTH = 960
# SCREEN_HEIGHT = 540

# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("Psychic Detective")

# #game variables
# game_paused = False
# menu_state = "main"

# #define fonts
# font = pygame.font.SysFont("arialblack", 40)

# #define colours
# TEXT_COL = (255, 255, 255)

# #load button images
# title_img = pygame.image.load("images/title.png").convert_alpha()
# resume_img = pygame.image.load("images/resume.png").convert_alpha()
# options_img = pygame.image.load("images/options.png").convert_alpha()
# quit_img = pygame.image.load("images/quit.png").convert_alpha()
# back_img = pygame.image.load('images/back.png').convert_alpha()
# notebook_img = pygame.image.load('images/notebook.png').convert_alpha()
# newgame_img = pygame.image.load('images/newgame.png').convert_alpha()

# #create button instances
# resume_button = button.Button(150, -100, resume_img, 1)
# options_button = button.Button(150,-50, options_img, 1)
# quit_button = button.Button(150,0, quit_img, 1)
# back_button = button.Button(150,-100, back_img, 1)
# notebook_button = button.Button(150,0, notebook_img, 1)

# # def draw_text(text, font, text_col, x, y):
# #   img = font.render(text, True, text_col)
# #   screen.blit(img, (x, y))

# #game loop
# run = True
# while run:

#   screen.fill((0, 0, 0))

#   #check if game is paused
#   if game_paused == True:
#     #check menu state
#     if menu_state == "main":
#       #draw pause screen buttons
#       if resume_button.draw(screen):
#         game_paused = False
#       if options_button.draw(screen):
#         menu_state = "options"
#       if quit_button.draw(screen):
#         print("quit button pressed")
#         run = False
#     #check if the options menu is open
#     if menu_state == "options":
#       #draw the different options buttons
#       if back_button.draw(screen):
#         menu_state = "main"
#       if notebook_button.draw(screen):
#         print("Notebook") #to be changed when notebook is implemented
#   else:
#     screen.blit(title_img, (150,-100))
#     # resume_button.draw(screen)
#     screen.blit(resume_img, (150,0))
#     screen.blit(newgame_img, (150,50))

#   #event handler
#   for event in pygame.event.get():
#     if event.type == pygame.KEYDOWN:
#       if event.key == pygame.K_ESCAPE:
#         game_paused = True
#     if event.type == pygame.QUIT:
#       print("window closed")
#       run = False

#   pygame.display.update()

# pygame.quit()
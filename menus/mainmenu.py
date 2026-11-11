import pygame
from . import button

class MainMenu:
  def __init__(self, screen):
    #load images for the buttons
    self.screen = screen
    self.title_img = pygame.image.load("menus/images/title.png").convert_alpha()
    self.resume_img = pygame.image.load("menus/images/resume.png").convert_alpha()
    self.newgame_img = pygame.image.load('menus/images/newgame.png').convert_alpha()
    self.quit_img = pygame.image.load("menus/images/quit.png").convert_alpha()

  #buttons
    self.resume_button = button.Button(150, 0, self.resume_img, 1)
    self.quit_button = button.Button(150,25, self.quit_img, 1)
    self.newgame_button = button.Button(150, 50, self.newgame_img, 1)

  def draw(self):
    self.screen.fill((0, 0, 0))
    self.screen.blit(self.title_img, (150, -100))
    if self.newgame_button.draw(self.screen):
      return "newgame"
    if self.resume_button.draw(self.screen):
      return "resume"
    if self.quit_button.draw(self.screen):
      return "quit"
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
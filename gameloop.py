import sys

import pygame

from scripts.utils import load_image, load_images
from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap

class Game:
    def __init__(self, player_count = 1):
        pygame.init() #have to initialize the game itself here

        pygame.display.set_caption('Psychic Detective') #this names the window when it is opened

        self.screen_width = 1920
        self.screen_height = 1080
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height)) #resolution of the screen
        self.display = pygame.Surface((self.screen_width, self.screen_height)) #allows for scaling - this can be changed to different pixel values to scale differently

        self.clock = pygame.time.Clock()

        #db_conn = db.initialize_database() ##to connect to Jasmine's database and keep an open connection

        self.numplayers = player_count
        
        self.movement1 = [False, False]
        self.movement2 = [False, False]
        
        self.assets = { #assets to load the level - these are placeholders we will replace with our own tiles for the actual background of the game
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'corporeal_player': load_image('entities/corporeal/corporeal_player.png'),
            'astral_player': load_image('entities/astral/astral_player.png'),
            'background': load_image('background.png'),
            'floor': load_images('tiles/floor')
        }

        #all_sprites = pygame.sprite.Group()
        
        self.player = PhysicsEntity(self, 'Player', (2000, 500), (35,64), "corporeal") #instantiate the player, call it player, place it as 50,50 and set its size to 8x15, default is corporeal body
        self.player2 = PhysicsEntity(self, 'Player2', (2050, 500), (35,64), "astral") #always instantiate the first player, if numplayers is 2, instantiate the second

        #all_sprites.add(self.player)
        #all_sprites.add(self.player2)

        self.tilemap = Tilemap(self, tile_size=64) #instantiate the tilemap (level)

        self.scroll = [0, 0]

        self.paused = False
        self.pause_selection = 0
        self.pause_options = ["RESUME GAME", "QUIT GAME"]

        pygame.font.init()
        self.pause_font = pygame.font.SysFont("Arial", 64, bold = True)
        self.menu_font = pygame.font.SysFont("Arial", 40, bold = True)
        
    def run(self):
        while True: #run the program and loop continuously until you tell it to quit (close the window)
            self.display.fill((0, 0, 0))
            
            #Scale the background to fit self.display's size
            display_size = (self.display.get_width(), self.display.get_height())
            scaled_bg = pygame.transform.scale(self.assets['background'], display_size)
            self.display.blit(scaled_bg, (0, 0))

            if self.numplayers == 1:
                self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 20 #camera movement in x direction centered directly between 2 players
                self.scroll[1] += (self.player.rect().centery- self.display.get_height() / 2 - self.scroll[1]) / 20 #camera movement in y direction centered directly between 2 players
            else:
                self.scroll[0] += (((self.player.rect().centerx + self.player2.rect().centerx) / 2) - self.display.get_width() / 2 - self.scroll[0]) / 20 #camera movement in x direction centered directly between 2 players
                self.scroll[1] += (((self.player.rect().centery + self.player2.rect().centery) / 2)- self.display.get_height() / 2 - self.scroll[1]) / 20 #camera movement in y direction centered directly between 2 players
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            if not self.paused:
                self.tilemap.render(self.display, offset = render_scroll)
                
                self.player.update(self.tilemap, ((self.movement1[1] - self.movement1[0]) * 4, 0)) #update the character and tilemap in each loop, *4 scales the move speed
                self.player.render(self.display, offset = render_scroll)
                if self.numplayers == 2:
                    self.player2.update(self.tilemap, ((self.movement2[1] - self.movement2[0]) * 4, 0))
                    self.player2.render(self.display, offset = render_scroll)
            else:
                pass

            if self.paused:
                overlay = pygame.Surface((self.screen_width, self.screen_height))
                overlay.fill((0,0,0,150)) 
                self.display.blit(overlay, (0,0))       

                pause_text = self.pause_font.render("GAME PAUSED", True, (255, 255, 255))
                text_rect = pause_text.get_rect(center=(self.screen_width / 2, self.screen_height / 2))
                self.display.blit(pause_text, text_rect)

                for index, option_text in enumerate(self.pause_options):
                    if index == self.pause_selection:
                        text_color = (255, 190, 0)
                        display_string = f"> {option_text} <"
                    else:
                        text_color = (160,160, 160)
                        display_string = option_text
                    option_surf = self.menu_font.render(display_string, True, text_color)
                    vertical_y = self.screen_height / 2 + 50 + (index * 60)
                    option_rect = option_surf.get_rect(center=(self.screen_width / 2, vertical_y))
                    self.display.blit(option_surf, option_rect)
            
            for event in pygame.event.get(): #events are how pygame reads input
                if event.type == pygame.QUIT:
                    #db_conn.close() ##remember to close the inventory database when the game closes
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN: #keydown is when you press the button and this assigns the standard left and right to move, and up to jump
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused  
                        self.pause_selection = 0  
                    if self.paused:
                        self.movement1 = [False, False]
                        self.movement2 = [False, False]
                        self.player.velocity = [0, 0]
                        if self.numplayers == 2:
                            self.player2.velocity = [0, 0]
                        if event.key == pygame.K_UP:
                            self.pause_selection = (self.pause_selection - 1) % len(self.pause_options)
                        if event.key == pygame.K_DOWN:
                            self.pause_selection = (self.pause_selection + 1) % len(self.pause_options)
                        if event.key == pygame.K_RETURN:
                            if self.pause_selection == 0:
                                self.paused = False
                            elif self.pause_selection == 1:
                                pygame.quit()
                                sys.exit()

                    else:
                        if event.key == pygame.K_LEFT:
                            self.movement1[0] = True
                            self.player.flip = False 
                        if event.key == pygame.K_RIGHT:
                            self.movement1[1] = True
                            self.player.flip = True  
                        if event.key == pygame.K_UP:
                            if self.player.jump():
                                pass
                                #self.sfx['jump'].play() optional play sound effect if we add later
                        if event.key == pygame.K_SPACE:
                            if self.player.dash(pygame.time.get_ticks(), self.tilemap):
                                pass
                        if event.key == pygame.K_l:
                            self.player.swap_form()

                    
                        if event.key == pygame.K_a:
                            self.movement2[0] = True
                            self.player2.flip = False 
                        if event.key == pygame.K_d:
                            self.movement2[1] = True
                            self.player2.flip = True  
                        if event.key == pygame.K_w:
                            if self.player2.jump():
                                pass
                                #self.sfx['jump'].play() optional play sound effect
                        if event.key == pygame.K_SPACE:
                            if self.player2.dash(pygame.time.get_ticks(), self.tilemap):
                                pass
                        if event.key == pygame.K_l:
                            self.player2.swap_form()

                if event.type == pygame.KEYUP: #keyup is when the key is released, so we reset back to the standard
                    if event.key == pygame.K_LEFT:
                        self.movement1[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement1[1] = False
                    
                    if event.key == pygame.K_a:
                        self.movement2[0] = False
                    if event.key == pygame.K_d:
                        self.movement2[1] = False
            
            #Clean the main screen window entirely before redrawing the new frame to clear remnants
            self.screen.fill((0,0,0))
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)) #blit command sends the objects to the screen
            pygame.display.update() #update each time the loop cycles
            self.clock.tick(60) #update the clock - this is currently set to 60 FPS, which should be more than we need for this game

user_input = int(input("Select number of players: "))

Game(user_input).run()

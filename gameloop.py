import sys

import pygame

from scripts.utils import load_image, load_images
from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap

class Game:
    def __init__(self):
        pygame.init() #have to initialize the game itself here

        pygame.display.set_caption('Psychic Detective') #this names the window when it is opened
        self.screen = pygame.display.set_mode((1080, 720)) #resolution of the screen
        self.display = pygame.Surface((540, 360)) #allows for scaling - this can be changed to different pixel values to scale differently

        self.clock = pygame.time.Clock()

        #db_conn = db.initialize_database() ##to connect to Jasmine's database and keep an open connection
        
        self.movement = [False, False]
        
        self.assets = { #assets to load the level - these are placeholders we will replace with our own tiles for the actual background of the game
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png')
        }
        
        self.player = PhysicsEntity(self, 'Player', (50, 50), (8, 15), "astral") #instantiate the player, call it player, place it as 50,50 and set its size to 8x15
        
        self.tilemap = Tilemap(self, tile_size=16) #instantiate the tilemap (level)
        
    def run(self):
        while True: #run the program and loop continuously until you tell it to quit (close the window)
            self.display.fill((0, 0, 0)) #fill the background with black
            
            self.tilemap.render(self.display)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0)) #update the character and tilemap in each loop
            self.player.render(self.display)
            
            for event in pygame.event.get(): #events are how pygame reads input
                if event.type == pygame.QUIT:
                    #db_conn.close() ##remember to close the inventory database when the game closes
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN: #keydown is when you press the button and this assigns the standard left and right to move, and up to jump
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                        self.flip = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                        self.flip = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            pass
                            #self.sfx['jump'].play() optional play sound effect
                    if event.key == pygame.K_SPACE:
                        if self.player.dash(pygame.time.get_ticks()):
                            pass
                    if event.key == pygame.K_s:
                        self.player.swap_form()
                    #if event.key == pygame.K_e: ##collect evidence button - physical evidence can only be collected by corporeal body
                        #if player.form == "corporeal":
                            #db.collect_evidence(db_conn, name, description, player)
                        #else:
                            #pass
                if event.type == pygame.KEYUP: #keyup is when the key is released, so we reset back to the standard
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)) #blit command sends the objects to the screen
            pygame.display.update() #update each time the loop cycles
            self.clock.tick(60) #update the clock - this is currently set to 60 FPS, which should be more than we need for this game

Game().run()

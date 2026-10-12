import pygame
import sys
from scripts.entities import PhysicsEntity
from scripts.utils import load_image, load_images

class Game: #wrap the main functionality of the game as a class
    def __init__(self):

        pygame.init() #initialize the pygame in general

        pygame.display.set_caption('Psychic Detective') #names the game window

        self.screen = pygame.display.set_mode((1080,720)) #set display to tuple resolution
        self.display = pygame.Surface((540, 360))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png')
        }

        self.player = PhysicsEntity(self, 'player', (50,50), (8,15))

    def run(self):
        while True: #pygame runs in a continuous loop
            self.display.fill((0,0,0))

            self.player.update((self.movement[1] - self.movement[0], 0))
            self.player.render(self.display)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: #this event is used to trigger the end of the game and program if the 'x' is used to close the window
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()),(0, 0))
            pygame.display.update() #update the screen each loop
            self.clock.tick(60) #tick clock forward. set to 60 FPS 

Game().run() #must include this to actually run the whole thing
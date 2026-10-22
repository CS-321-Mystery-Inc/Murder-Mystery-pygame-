import pygame
from scripts.utils import Animation

class Interactable(pygame.sprite.Sprite):
    def __init__(self, game, pos, size, item_type):
        super().__init__()
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.type = item_type

        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.action = 'idle'
        self.image = pygame.Surface(self.size)

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[f"{self.type}/{self.action}"].copy()

    def update(self):
        self.animation.update()
        self.image = self.animation.img()

    def interact(self, entity):
        pass

class Door(Interactable):
    def __init__(self, game, pos, size = (64,128)):
        super().__init__(game, pos, size, 'door')
        self.is_open = False
        self.set_action('idle')

    def interact(self, entity):
        if entity.form == 'corporeal' and not self.is_open:
            self.is_open = True
            self.set_action('open')
            return True
        return False

    def get_solid_rect(self):
        if not self.is_open:
            return self.rect
        return None
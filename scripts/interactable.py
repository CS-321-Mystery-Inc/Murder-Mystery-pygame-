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
        self.animation = None

    def set_action(self, action):
        if action != self.action or self.animation is None:
            self.action = action
            self.animation = self.game.assets[f"{self.type}/{self.action}"].copy()

    def update(self):
        if self.animation:
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

class Switch(Interactable):
    def __init__(self, game, pos, linked_wall, size=(32, 64)):
        super().__init__(game, pos, size, 'switch')
        self.linked_wall = linked_wall
        self.is_flipped = False
        self.set_action('idle')

    def interact(self, entity):
        if entity.form == 'corporeal' and not self.is_flipped:
            self.is_flipped = True
            self.set_action('flipped')

        if self.linked_wall:
            self.linked_wall.open_wall()
            return True
        return False

class MovableWall(pygame.sprite.Sprite):
    def __init__(self, game, pos, size = (64, 192)):
        super().__init__()
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.is_open = False

        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.image = pygame.Surface(self.size)
        self.image.fill((70,70,80))

    def open_wall(self):
        self.is_open = True

    def get_solid_rect(self):
        if not self.is_open:
            return self.rect
        return None

    def update(self):
        pass
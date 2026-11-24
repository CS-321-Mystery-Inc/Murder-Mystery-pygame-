import pygame


class Interactable(pygame.sprite.Sprite):
    def __init__(self, game, pos, size, item_type):
        super().__init__()
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.type = item_type
        self.rect = pygame.Rect(self.pos[0], self.pos[1], *self.size)
        self.action = 'idle'
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.animation = None

    def set_action(self, action):
        if action != self.action or self.animation is None:
            self.action = action
            self.animation = self.game.assets[f'{self.type}/{self.action}'].copy()
            self.image = self.animation.img()

    def update(self):
        if self.animation:
            self.animation.update()
            self.image = self.animation.img()

    def interact(self, entity):
        return False


class Door(Interactable):
    def __init__(self, game, pos, size=(64, 128)):
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
        return None if self.is_open else self.rect


class Switch(Interactable):
    def __init__(self, game, pos, linked_wall, size=(32, 64)):
        super().__init__(game, pos, size, 'switch')
        self.linked_wall = linked_wall
        self.is_flipped = False
        self.set_action('idle')

    def set_flipped(self, flipped):
        """Also used when restoring or resetting a saved level."""
        self.is_flipped = bool(flipped)
        self.set_action('flipped' if self.is_flipped else 'idle')
        if self.linked_wall:
            if self.is_flipped:
                self.linked_wall.open_wall()
            else:
                self.linked_wall.close_wall()

    def interact(self, entity):
# Only the corporeal form can use the switch; the astral form cannot.
        if entity.form != 'corporeal':
            return False
        self.set_flipped(not self.is_flipped)
        return True


class MovableWall(pygame.sprite.Sprite):
    def __init__(self, game, pos, size=(64, 192)):
        super().__init__()
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.is_open = False
        self.rect = pygame.Rect(self.pos[0], self.pos[1], *self.size)
        self.image = pygame.Surface(self.size)
        self.image.fill((70, 70, 80))

    def open_wall(self):
        self.is_open = True
        self.image.set_alpha(0)

    def close_wall(self):
        self.is_open = False
        self.image.set_alpha(255)

    def get_solid_rect(self):
        return None if self.is_open else self.rect

    def update(self):
        pass

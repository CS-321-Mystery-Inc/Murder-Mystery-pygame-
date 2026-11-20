import pygame

class Clue(pygame.sprite.Sprite):
    def __init__(self, pos, image, item_name):
        super().__init__()
        self.image = image
        self.pos = pos
        self.item_name = item_name
        self.rect = self.image.get_rect(topleft=pos)
    def collect(self, player):
        if self.rect.colliderect(player.get_rect()):
            print("Collected clue")
            self.kill()
            return True
        return False
    def can_collect(self, player):
        return self.rect.colliderect(player.get_rect())
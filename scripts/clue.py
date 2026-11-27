import pygame


class Clue(pygame.sprite.Sprite):
    """Collectible placeholder sprite; metadata can represent any evidence type."""

    def __init__(self, pos, image, item_name, evidence_id=None,
                 item_type="Clue", description=""):
        super().__init__()
        self.image = image
        self.pos = list(pos)
        self.item_name = item_name
        self.evidence_id = evidence_id
        self.item_type = item_type
        self.description = description
        self.rect = self.image.get_rect(topleft=pos)

    def can_collect(self, player):
        return self.rect.colliderect(player.get_rect())

    def collect(self, player):
        """Retained for existing callers; the game now records evidence before killing."""
        if self.can_collect(player):
            self.kill()
            return True
        return False

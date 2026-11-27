import pygame


# button class
class Button:

  def __init__(self, x, y, image, scale):
    width = image.get_width()
    height = image.get_height()
    self.image = pygame.transform.scale(
        image, (int(width * scale), int(height * scale))
    )
    self.rect = self.image.get_rect(topleft=(x, y))
    self.mask = pygame.mask.from_surface(self.image)
    self.clicked = False

  def draw(self, surface):
    action = False
    pos = pygame.mouse.get_pos()

    hovered = False
    if self.rect.collidepoint(pos):
      relative_x = pos[0] - self.rect.x
      relative_y = pos[1] - self.rect.y
      if (
          0 <= relative_x < self.mask.get_size()[0]
          and 0 <= relative_y < self.mask.get_size()[1]
      ):
        hovered = bool(self.mask.get_at((relative_x, relative_y)))

    if hovered:
      self.image.set_alpha(255)
      if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
        self.clicked = True
        action = True
    else:
      self.image.set_alpha(190)

    if pygame.mouse.get_pressed()[0] == 0:
      self.clicked = False

    surface.blit(self.image, (self.rect.x, self.rect.y))
    return action
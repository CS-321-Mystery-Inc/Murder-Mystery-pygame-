import pygame

#button class
class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect().scale_by(0.55)
		self.rect.topleft = (x, y)
		self.mask = pygame.mask.from_surface(self.image)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			relative_x = pos[0] - self.rect.x
			relative_y = pos[1] - self.rect.y

			self.image.set_alpha(50)

			if self.mask.get_at((relative_x, relative_y)):
				if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
					self.clicked = True
					action = True
		else:
			self.image.set_alpha(100)

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action
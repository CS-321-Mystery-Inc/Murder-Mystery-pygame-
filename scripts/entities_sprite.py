import math
import random
from scripts.tilemap import Tilemap
import pygame
from scripts.utils import load_image

class PhysicsEntity(pygame.sprite.Sprite):
    def __init__(self, game, e_type, pos, size, form):
        super().__init__()

        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.form = form
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.last_dash_time = 0
        self.dash_trails = []
        self.trail_spawn_timer = 0
        
        self.action = ''
        self.flip = False
        self.anim_offset = (0, 0)
        self.set_action('idle')

        if self.form == 'corporeal':
            self.jumps = 1
        if self.form == 'astral':
            self.jumps = 2

        self.update_image()
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update_image(self):
        if self.form == 'corporeal':
            base_img = self.game.assets['corporeal_player']
        else:
            base_img = self.game.assets['astral_player']

        self.image = pygame.transform.flip(base_img, self.flip, False)

    def get_rect(self): #create a rectangle around the character to allow it to interact with the world. this is dynamic so it updates each time the game loops
        self.rect.x = int(self.pos[0])
        self.rect.y = int(self.pos[1])
        return self.rect
        
    def set_action(self, action):
        if action != self.action:
            self.action = action
            asset_key = f"{self.form}/{self.action}"
            self.animation = self.game.assets[asset_key].copy()
    
    def update_image(self):
        base_img = self.animation.img()
        self.image = pygame.transform.flip(base_img, self.flip, False)
    
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1]) 
        
        # X-axis physics
        self.pos[0] += frame_movement[0]
        if frame_movement[0] != 0:
            self.set_action('run')
        entity_rect = self.get_rect() # Fetch synced rect

        nearby_rects = tilemap.physics_rects_around(self.pos)

        for item in self.game.interactables:
            if hasattr(item, 'get_solid_rect'):
                door_box = item.get_solid_rect()
                if door_box:
                    nearby_rects.append(door_box)

        for rect in nearby_rects:
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True 
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0 :
            self.flip = True

        self.pos[1] += frame_movement[1] #same as above, but in the up/down direction
        entity_rect = self.get_rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        if(self.form == 'corporeal'):
            self.velocity[1] = min(10, self.velocity[1] + 0.2) #this handles gravity to generally make the character "fall"
        else:
            self.velocity[1] = min(5, self.velocity[1] + 0.2) #slower fall speed for the astral form
        
        if self.collisions['down'] or self.collisions['up']: #this resets the slow initial fall speed so you don't reach terminal velocity immediately after falling
            self.velocity[1] = 0

        if self.collisions['down'] and self.form == 'corporeal':
            self.jumps = 1
        if self.collisions['down'] and self.form == 'astral':
            self.jumps = 2

        self.dash_trails = [trail for trail in self.dash_trails if not trail.update()]

        self.set_action('idle')
        self.animation.update()
        self.update_image()

    def jump(self):
        if self.jumps > 0:
            self.velocity[1] = -8
            self.jumps -= 1
        self.set_action('jump')
        return True
        
    def render(self, surf, offset=(0,0)): #render the entity onto the screen
       for trail in self.dash_trails:
           trail.render(surf, offset = offset)
       
       surf.blit(self.image, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def dash(self, current_time, tilemap):
        DASH_DISTANCE = self.size[0] + tilemap.tile_size
        DASH_COOLDOWN = 1000

        if (current_time - self.last_dash_time >= DASH_COOLDOWN) and self.form == 'astral':
            steps = 4
            step_distance = DASH_DISTANCE / steps

            for i in range(steps):
                if self.flip:
                    trail_x = self.pos[0] - (i * step_distance)
                else:
                    trail_x = self.pos[0] + (i * step_distance)
                new_trail = GhostTrail((trail_x, self.pos[1]), self.image, duration = 20)
                self.dash_trails.append(new_trail)

            if self.flip:
                self.pos[0] -= DASH_DISTANCE
            else:
                self.pos[0] += DASH_DISTANCE
            self.last_dash_time = current_time
            self.update_image()
            return True
        return False

    def swap_form(self):
        if self.form == 'corporeal':
            self.form = 'astral'
        else:
            self.form = 'corporeal'
        self.update_image()

class GhostTrail:
    def __init__(self, pos, image, duration = 15):
        self.pos = list(pos)

        self.image = image.copy()
        self.duration = duration
        self.max_duration = duration

    def update(self):
        self.duration -= 1
        return self.duration <= 0

    def render(self, surf, offset = (0, 0)):
        alpha = int((self.duration / self.max_duration) * 150)

        self.image.set_alpha(alpha)
        surf.blit(self.image, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
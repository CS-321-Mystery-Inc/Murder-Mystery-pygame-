import math
import random

import pygame

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size, form):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.form = form
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.last_dash_time = 0
        
        self.action = ''
        self.flip = False
        self.set_action('idle')

        if self.form == 'corporeal':
            self.jumps = 1
        if self.form == 'astral':
            self.jumps = 2
    
    def rect(self): #create a rectangle around the character to allow it to interact with the world. this is dynamic so it updates each time the game loops
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
    
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False} #reset all collisions to false with each game loop
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1]) 
        
        self.pos[0] += frame_movement[0] #move the character
        entity_rect = self.rect() #use the above function to create the rect around the player
        for rect in tilemap.physics_rects_around(self.pos): #physics_rect_around checks for collisions around the player so it doesn't have to check all tiles every loop
            if entity_rect.colliderect(rect): #if a collision occurs
                if frame_movement[0] > 0: #stop movement in the collision direction
                    entity_rect.right = rect.left #snap the character to the side of the object you ran into
                    self.collisions['right'] = True #annotate where the collision occured 
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x #actually update the character position, so it doesn't get lost inside the terrain tiles

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
        
        self.pos[1] += frame_movement[1] #same as above, but in the up/down direction
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        
        self.velocity[1] = min(5, self.velocity[1] + 0.1) #this handles gravity to generally make the character "fall"
        
        if self.collisions['down'] or self.collisions['up']: #this resets the slow initial fall speed so you don't reach terminal velocity immediately after falling
            self.velocity[1] = 0

        if self.collisions['down'] and self.form == 'corporeal':
            self.jumps = 1
        if self.collisions['down'] and self.form == 'astral':
            self.jumps = 2

    def jump(self):
        if self.jumps > 0:
            self.velocity[1] = -3
            self.jumps -= 1
        return True
        
    def render(self, surf, offset=(0,0)): #render the entity onto the screen
        #surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        surf.blit(pygame.transform.flip(self.game.assets['player'], self.flip, False), self.pos)

    def dash(self, current_time):
        DASH_DISTANCE = self.size[0] + 16
        DASH_COOLDOWN = 1000

        if (current_time - self.last_dash_time >= DASH_COOLDOWN) and self.form == 'astral':
            if self.flip:
                self.pos[0] -= DASH_DISTANCE
            else:
                self.pos[0] += DASH_DISTANCE
            self.last_dash_time = current_time
        else:
            return

    def swap_form(self):
        if self.form == 'corporeal':
            self.form = 'astral'
        else:
            self.form = 'corporeal'

import pygame

#script to determine the tiles of the world

#when looking at collision detection, only need to look at the 9 boxes where the player is and around them
NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone', 'floor'}
LEVEL_WIDTH = 64

class Tilemap:
    def __init__(self, game, tile_size = 64):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {} #these tiles will be on a grid
        self.offgrid_tiles = [] #these tiles will not be on the grid

        for i in range(10): #vertical terrain pieces
            self.tilemap['10;' + str(5 + i)] = {'type': 'stone', 'variant': 1, 'pos': (10, 5 + i)}
            self.tilemap['0;' + str(i + 1)] = {'type': 'floor', 'variant': 0, 'pos': (0, i + 1)}
            self.tilemap[str(LEVEL_WIDTH) + ';' + str(i + 1)] = {'type': 'floor', 'variant': 0, 'pos': (LEVEL_WIDTH, i + 1)}#right wall
        for i in range(LEVEL_WIDTH):#horizontal terrain pieces
            self.tilemap[str(i) + ';10'] = {'type': 'floor', 'variant': 1, 'pos': (i, 10)}#floor
            self.tilemap[str(i) + ';1'] = {'type': 'floor', 'variant': 1, 'pos': (i, 1)}#ceiling
        for i in range(5):
            self.tilemap[str(20 + i) + ';4'] = {'type': 'stone', 'variant': 0, 'pos': (20 + i, 4)}
            self.tilemap[str(24 + i) + ';7'] = {'type': 'stone', 'variant': 0, 'pos': (24 + i, 7)}

    def tiles_around(self, pos): #identify tiles around the player and note which are there in the tiles[] list
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    def physics_rects_around(self, pos): #create a rectangle object for each of the above tiles to allow for entity interactions
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects

    def render(self, surf, offset = (0,0)): #render the tiles onto the screen (offgrid tiles render behind on grid tiles)
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        #this next portion only renders the objects that are on screen - reduces lag from tiles rendering off screen          
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
               
        # for loc in self.tilemap:
        #     tile = self.tilemap[loc]
        #     surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))


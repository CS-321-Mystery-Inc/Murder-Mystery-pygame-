import pygame

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0),
                    (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone', 'floor'}
LEVEL_WIDTH = 64
GROUND_ROW = 10
TILE_SIZE = 64

# Level 1 is deliberately built from the existing floor / stone tiles.
# The passage at x=1536 is blocked by a separate movable wall until the lever
# at x=2200 is flipped. Platforms are one jump above the main floor.
LEVEL_ONE_ITEMS = (
    {"id": 101, "name": "Coin 1", "item_type": "Coin", "center_x": 1870,
     "surface_y": GROUND_ROW * TILE_SIZE,
     "description": "The stone remembers what it guards. Look east for an iron tongue; only a living hand can wake it."},
    {"id": 102, "name": "Coin 2", "item_type": "Coin", "center_x": 2680,
     "surface_y": 8 * TILE_SIZE,
     "description": "Above the right-hand path, the second mark waits. When iron yields, follow the passage toward the setting sun."},
    {"id": 103, "name": "Coin 3", "item_type": "Coin", "center_x": 1210,
     "surface_y": GROUND_ROW * TILE_SIZE,
     "description": "The opened wall hid no answer, only a road. Seek the higher stones farther west for the final whisper."},
    {"id": 104, "name": "Coin 4", "item_type": "Coin", "center_x": 800,
     "surface_y": 8 * TILE_SIZE,
     "description": "Four quiet witnesses speak only when gathered. Keep their words close; the notebook never forgets."},
)


class Tilemap:
    def __init__(self, game, tile_size=64):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        self.build_level_one()

    def add_tile(self, x, y, tile_type, variant=0):
        self.tilemap[f'{x};{y}'] = {
            'type': tile_type, 'variant': variant, 'pos': (x, y)
        }

    def build_level_one(self):
        """A complete walkable room with two elevated evidence platforms."""
        self.tilemap.clear()
        for x in range(LEVEL_WIDTH + 1):
            self.add_tile(x, GROUND_ROW, 'floor', 1)
            self.add_tile(x, 1, 'floor', 1)
        for y in range(2, GROUND_ROW):
            self.add_tile(0, y, 'floor', 0)
            self.add_tile(LEVEL_WIDTH, y, 'floor', 0)
        for x in range(10, 16):
            self.add_tile(x, 8, 'stone', 0)
        for x in range(39, 45):
            self.add_tile(x, 8, 'stone', 0)

    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for dx, dy in NEIGHBOR_OFFSETS:
            tile = self.tilemap.get(f'{tile_loc[0] + dx};{tile_loc[1] + dy}')
            if tile is not None:
                tiles.append(tile)
        return tiles

    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                x, y = tile['pos']
                rects.append(pygame.Rect(x * self.tile_size, y * self.tile_size,
                                         self.tile_size, self.tile_size))
        return rects

    def render(self, surf, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']],
                      (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
        for x in range(offset[0] // self.tile_size,
                       (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size,
                           (offset[1] + surf.get_height()) // self.tile_size + 1):
                tile = self.tilemap.get(f'{x};{y}')
                if tile:
                    surf.blit(self.game.assets[tile['type']][tile['variant']],
                              (x * self.tile_size - offset[0],
                               y * self.tile_size - offset[1]))

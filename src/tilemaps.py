import pygame as pg
from pytmx import TiledTileLayer, TiledObjectGroup
from pytmx.util_pygame import load_pygame
import inspect

import settings as st
import sprites as spr

vec = pg.math.Vector2

class Grid():
    def __init__(self, game, name, width, height):
        self.game = game
        self.name = name

        self.map = [[None for i in range(height)] for j in range(width)]
        # TODO: should this be done in numpy?

    def insert_grid(self, map_, index_x, index_y):
        self.map[index_x][index_y] = map_

    def get_map_at(self, index_x, index_y):
        try:
            return self.map[index_x][index_y]
        except IndexError:
            return None


class Map():
    def __init__(self, game, filename):
        self.game = game
        self.filename = filename
        
        # load map data
        self.tiled_map = load_pygame(self.filename)
        self.tilesize = vec(self.tiled_map.tilewidth, self.tiled_map.tileheight)
        self.size = vec(self.tiled_map.width * self.tilesize.x, 
                        self.tiled_map.height * self.tilesize.y)
        self.background_color = self.tiled_map.background_color
        self.layers = []

    def __repr__(self):
        return self.filename.split('\\')[-1]
        
    
    def create_map(self):
        '''ectracts tileset and object data from a tmx file'''
        # create an empty surface 
        #self.map_image = pg.Surface(self.size)
        #self.rect = self.map_image.get_rect()
        # if background color was specified, fill the surface
        #if self.background_color:
        #    self.map_image.fill(self.background_color)
        # TODO: create a mono colored background layer

        self.layers = []
        # loop through all available layers
        for layer in self.tiled_map:
            if isinstance(layer, TiledTileLayer) and layer.visible:
                bg_layer_img = pg.Surface(self.size).convert_alpha()
                # fill with transparent color
                bg_layer_img.fill((0, 0, 0, 0))
                self.rect = bg_layer_img.get_rect()
                # if layer is tileset data, blit the tile image at the corresponding 
                # position on the map image
                for x, y, image in layer.tiles():
                    bg_layer_img.blit(image, (x * self.tilesize.x, 
                                              y * self.tilesize.y))
                self.layers.append(bg_layer_img)
            elif isinstance(layer, TiledObjectGroup) and layer.visible:
                # if layer is an object layer, fetch the corresponding sprite
                # from the sprites.py (spr) module
                sprites = dict(inspect.getmembers(spr, inspect.isclass))
                for obj in layer:
                    if obj.name in sprites:
                        # check if the sprite exists in sprites.py
                        # if so, instantiate the sprite
                        sprites[obj.name](self.game, obj.__dict__)
                    else:
                        print(f'No sprite "{obj.name}" found in sprites module')

        self.rect.topleft = (0, st.GUI_HEIGHT)



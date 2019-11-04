import pygame as pg
import os

import settings as st


# TODO: multiple music channels?

class Loader():
    def __init__(self, game):
        self.game = game
        base_dir = game.base_dir
        self.graphics_folder = os.path.join(base_dir, 'assets', 'graphics')
        self.sounds_folder = os.path.join(base_dir, 'assets', 'sounds')
        self.sprite_folder = os.path.join(self.graphics_folder, 'sprites')
        self.tileset_folder = os.path.join(self.graphics_folder, 'tilesets')
        self.gui_image_folder = os.path.join(self.graphics_folder, 'GUI')
        self.font_folder = os.path.join(base_dir, 'assets', 'fonts')
            
        self.channel = None
        
        # TODO: dict comprehension
        self.fonts = {
                'slkscr': os.path.join(self.font_folder, 'slkscr.ttf')
                }
        
        
    def load_graphics(self):
        '''
        load sprite image strips here
        '''
        
        #TODO: search for filenames automatically
        sprite_files = ['knight_strip.png']
        
        sprite_images = [pg.image.load(os.path.join(self.sprite_folder, f)).convert_alpha() 
                         for f in sprite_files]
        
        gui_image_files = ['inventory_bg.png',
                           'cursor.png',
                           'health_string.png',
                           'hearts_strip.png',
                           'magicbar.png',
                           'arrows.png',
                           'minimap_strip_7x5.png',
                           'magic_and_items.png']
        
        gui_images = [pg.image.load(os.path.join(self.gui_image_folder, f)).convert_alpha()
                      for f in gui_image_files]
        
        gfx_lib = {
                'knight_images': self.images_from_strip(sprite_images[0], 10),
                'inventory_bg': gui_images[0],
                'cursor_images': self.images_from_strip(gui_images[1], 2),
                'health_string': gui_images[2],
                'heart_images': self.images_from_strip(gui_images[3], 6),
                'magicbar': gui_images[4],
                'arrows': self.images_from_strip(gui_images[5], 4),
                'minimap_images': self.images_from_strip(gui_images[6], 20),
                'magic_and_items': gui_images[7]
                }
        
        return gfx_lib
    
    
    def load_sounds(self):
        pg.mixer.init()
        
        music_files = [
                'A_Journey_Awaits.mp3',
                'Memoraphile_Spooky_Dungeon.ogg'
                ]
        sfx_files = [
                'Pickup_Coin35.wav'
                ]

        music_objects = [os.path.join(self.sounds_folder, 'bgm', f)
                         for f in music_files]     
        sfx_objects = [pg.mixer.Sound(os.path.join(self.sounds_folder, 'sfx', f))
                        for f in sfx_files]
        
        # sound libs stored as (filename, relative volume)
        self.music_lib = {
                'overworld': (music_objects[0], 0.9),
                'dungeon1': (music_objects[1], 0.8)
                }
        
        self.sfx_lib = {
                'test_sound': (sfx_objects[0], 1)
                }
        
        
    def play_music(self, key, loop=True):
        if loop:
            loops = -1
        else:
            loops = 0
        pg.mixer.music.load(self.music_lib[key][0])
        pg.mixer.music.play(loops)
        volume = st.MUSIC_VOLUME * self.music_lib[key][1]
        pg.mixer.music.set_volume(volume)
        
          
    def play_sound(self, key):
        sound = self.sfx_lib[key][0]
        volume = st.SFX_VOLUME * self.sfx_lib[key][1]
        sound.set_volume(volume)
        # play the sound if it isn't already being played
        if self.channel is None:
            self.channel = sound.play()
        else:
            if self.channel.get_sound() == sound:
                if not self.channel.get_busy():
                    self.channel = sound.play()
            else:
                self.channel = sound.play()
            
    
    def images_from_strip(self, strip, number):
        img_w = strip.get_width() // number
        img_h = strip.get_height()
        
        images = []
        for i in range(number):
            s = strip.subsurface((i * img_w, 0, img_w, img_h))
            images.append(s)

        return images
import pygame as pg
import os


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
        sprite_files = list(filter(lambda x: x[-3:]=='png', os.listdir(self.sprite_folder)))
        sprite_images = {f[:-4] : pg.image.load(os.path.join(self.sprite_folder, f)).convert_alpha() 
                         for f in sprite_files}

        gui_image_files = list(filter(lambda x: x[-3:]=='png', 
                                      os.listdir(self.gui_image_folder)))
        gui_images = {f[:-4] : pg.image.load(os.path.join(self.gui_image_folder, f)).convert_alpha()
                      for f in gui_image_files}
        
        gfx_lib = {
                'knight_images': self.images_from_strip(sprite_images['knight_strip'], 10),
                'knight_attack': self.images_from_strip(sprite_images['knight_attack'], 4),
                'sword_anim': self.images_from_strip(sprite_images['sword_anim'], 16),
                'sword': sprite_images['sword'],
                'inventory_bg': gui_images['inventory_bg'],
                'inventory_images': self.images_from_strip(gui_images['inv_item_strip'], None, (16, 16)),
                'cursor_images': self.images_from_strip(gui_images['cursor'], 2),
                'arrow_images': self.images_from_strip(gui_images['arrows'], None, (8, 8)),
                'health_string': gui_images['health_string'],
                'heart_images': self.images_from_strip(gui_images['hearts_strip'], 6),
                'magicbar': gui_images['magicbar'],
                'arrows': self.images_from_strip(gui_images['arrows'], 4),
                'minimap_images': self.images_from_strip(gui_images['minimap_strip_7x5'], 20),
                'magic_and_items': gui_images['magic_and_items'],
                'enemy_skeleton': self.images_from_strip(sprite_images['skeleton_strip'], 7)
                }
        return gfx_lib
    
    
    def load_sounds(self):
        pg.mixer.init()
        
        bgm_folder = os.path.join(self.sounds_folder, 'bgm')
        sfx_folder = os.path.join(self.sounds_folder, 'sfx')
        
        music_files = list(filter(lambda x: x[-3:]=='mp3' or x[-3:]=='ogg', 
                                  os.listdir(bgm_folder)))
        music_objects = {f[:-4]: os.path.join(bgm_folder, f)
                         for f in music_files}
        
        sfx_files = list(filter(lambda x: x[-3:]=='mp3' or x[-3:]=='wav', 
                                  os.listdir(sfx_folder)))
        sfx_objects = {f[:-4]: pg.mixer.Sound(os.path.join(sfx_folder, f))
                        for f in sfx_files}
        
        # sound libs stored as (filename, relative volume)
        self.music_lib = {
                'overworld': (music_objects['A_Journey_Awaits'], 0.9),
                'dungeon1': (music_objects['Memoraphile_Spooky_Dungeon'], 0.8)
                }
        
        self.sfx_lib = {
                'test_sound': (sfx_objects['Pickup_Coin35'], 1),
                'sword_slash': (sfx_objects['slash'], 1)
                }
        
        
    def play_music(self, key, loop=True):
        # check if music is muted
        if not self.game.sound_settings['sound_on']:
            return
        if loop:
            loops = -1
        else:
            loops = 0
        pg.mixer.music.load(self.music_lib[key][0])
        pg.mixer.music.play(loops)
        volume = self.game.sound_settings['music_vol'] * self.music_lib[key][1]
        pg.mixer.music.set_volume(volume)
        
          
    def play_sound(self, key):
        # check if sound is muted
        if not self.game.sound_settings['sound_on']:
            return
        sound = self.sfx_lib[key][0]
        volume = self.game.sound_settings['sfx_vol'] * self.sfx_lib[key][1]
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
            
    
    def images_from_strip(self, strip, number=None, tilesize=None):
        # TODO: change this so it can process multiline images
        if number:
            img_w = strip.get_width() // number
            img_h = strip.get_height()
        elif tilesize:
            img_w = tilesize[0]
            img_h = tilesize[1]
            number = strip.get_size()[0] // img_w
        
        images = []
        for i in range(number):
            s = strip.subsurface((i * img_w, 0, img_w, img_h))
            images.append(s)

        return images
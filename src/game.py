import pygame as pg
import pygame.freetype
import inspect
import os
import json

import states
import settings as st
from load_assets import Loader
import controls
import utilities as utils

'''
# TODO list:
(import stuff from dungeon crusader v1)
- item system:
    - sword
    - potions
    - hookshot (re-vamp)
    - bombs
    - magic wand
- enemies
- collectable items (rupees, hearts)
- dungeon traps (pitfalls, spikes etc)
- menu in title screen (screen resolution, fullscreen, fixed FPS etc)
    --> Menu module for UI templates

'''

class Game():
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        # application window surface
        self.window_flags = st.WINDOW_FLAGS
        self.app_screen = pg.display.set_mode((st.WINDOW_W, st.WINDOW_H),
                                              self.window_flags)
        # game screen surface (where all the ingame stuff gets blitted on)
        self.game_screen = pg.Surface((st.GAME_SCREEN_W, st.GAME_SCREEN_H))
        # world screen (game screen minus the GUI overlay)
        self.world_screen = pg.Surface((st.GAME_SCREEN_W, 
                                        st.GAME_SCREEN_H - st.GUI_HEIGHT))
        # define screen rects for later use
        self.app_screen_rect = self.app_screen.get_rect()
        self.game_screen_rect = self.game_screen.get_rect()
        self.world_screen_rect = self.world_screen.get_rect()
        self.world_screen_rect.topleft = (0, st.GUI_HEIGHT)
        
        self.fps = st.FPS
        self.all_sprites = pg.sprite.Group()
        self.gui_elements = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        
        self.fonts = {
                'default_big': pygame.freetype.Font(file=None, size=22),
                'default_small': pygame.freetype.Font(file=None, size=14)
                }
        for f in self.fonts.values():
            f.antialiased = False
        
        self.base_dir = os.path.join(os.path.dirname( __file__ ), '..')
        
        self.map_files = ['sample_map.tmx',
                          'sample_map2.tmx']
        self.map_files = [os.path.join(self.base_dir, 'data', 'tilemaps', m) 
                          for m in self.map_files] #TODO: this probably belongs in load_assets.py
        self.save_dir = os.path.join(self.base_dir, 'data', 'saves')
        
        self.asset_loader = Loader(self)
        self.graphics = self.asset_loader.load_graphics()
        self.asset_loader.load_sounds()
        
        self.gamepad_controller = controls.GamepadController()
        self.key_getter = controls.KeyGetter(self)
        
        
        self.setup_states()
        
        self.debug_mode = st.DEBUG
    
    
    def setup_states(self):
        # get a dictionary with all classes from the 'states' module
        self.state_dict = dict(inspect.getmembers(states, inspect.isclass))
        # define the state at the start of the program
        self.state_name = 'Title_screen'
        self.state = self.state_dict[self.state_name](self)
        self.state.startup()
    
    
    def flip_state(self):
        '''set the state to the next if the current state is done'''
        self.state.done = False
        # set the current and next state to the previous and current state
        previous, self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        if self.state_name == None:
            self.running = False
        else:
            self.state = self.state_dict[self.state_name](self)
            self.state.startup()
            self.state.previous = previous
        
    
    def save(self, filename):
        '''default save function. Saves all sprites' attributes
        Args:
            filename: 'example.json'
        '''
        save_data = {}
        for sprite in self.all_sprites.sprites():
            # check if attribute is serializable
            keys_ok = []
            for key, value in sprite.__dict__.items():
                if utils.is_jsonable(value):
                    keys_ok.append(key)
            save_data['all_sprites'] = {key: sprite.__dict__[key] for key in keys_ok}
            
        with open(os.path.join(self.save_dir, filename), 'w') as f:
            json.dump(save_data, f)


    def events(self):
        '''empty the event queue and pass the events to the states'''
        self.events_list = pg.event.get()
        for event in self.events_list:
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F12:
                    self.debug_mode = not self.debug_mode
            elif event.type == pg.VIDEORESIZE:
                # if the user resizes the window (drag the bottom right corner)
                # get the new size from the event dict and reset the 
                # window screen surface
                self.reset_app_screen(event.dict['size'])
                
            self.state.get_event(event)
    
    
    def reset_app_screen(self, size):
        self.app_screen = pg.display.set_mode(size, self.window_flags)
        self.app_screen_rect = self.app_screen.get_rect()
        pg.display.update()


    def update(self, dt):
        # get input before state updates
        self.gamepad_controller.update()
        self.key_getter.get_input(self.gamepad_controller, self.events_list)
        
        #self.key_getter.test_inputs(self.keydown)
        #self.gamepad_controller.test_inputs('inputs_down')

        if self.state.done:
            self.flip_state()
        self.state.update(dt)
        
        current_fps = self.clock.get_fps()
        pg.display.set_caption(f'FPS: {current_fps:2.1f}')


    def draw(self):
        # draw everything that happens in the current state
        self.state.draw()
        
        if st.WINDOW_STRETCHED:
            # scale the game screen to the window size
            resized_screen = pg.transform.scale(self.game_screen, self.app_screen_rect.size)
        else:
            # compare aspect ratios
            game_ratio = self.game_screen_rect.w / self.game_screen_rect.h
            app_ratio = self.app_screen_rect.w / self.app_screen_rect.h

            if game_ratio < app_ratio:
                width = int(self.app_screen_rect.h / self.game_screen_rect.h 
                        * self.game_screen_rect.w)
                height = self.app_screen_rect.h
            else:
                width = self.app_screen_rect.w
                height = int(self.app_screen_rect.w / self.game_screen_rect.w
                         * self.game_screen_rect.h)
            resized_screen = pg.transform.scale(self.game_screen, 
                                                (width, height))
        
        
        # get the rect of the resized screen for blitting
        # and center it to the window screen
        res_screen_rect = resized_screen.get_rect()
        res_screen_rect.center = self.app_screen_rect.center

        self.app_screen.blit(resized_screen, res_screen_rect)

        pg.display.update(res_screen_rect)


    def run(self):
        self.running = True
        while self.running:
            delta_time = self.clock.tick(self.fps) / 1000 # "dt"
            #delta_time = self.clock.tick() / 1000 # "dt"
            self.events()
            self.update(delta_time)
            self.draw()

        pg.quit()
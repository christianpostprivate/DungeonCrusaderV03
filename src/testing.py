import pygame as pg
import os
import traceback


import controls
import settings as st
import sprites as spr
import states
import utilities as utils


vec = pg.math.Vector2


class Test_game():
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.actual_screen = pg.display.set_mode((st.WINDOW_W, st.WINDOW_H))
        self.screen = pg.Surface((st.GAME_SCREEN_W, st.GAME_SCREEN_H))
        self.world_screen = pg.Surface((st.GAME_SCREEN_W, 
                                        st.GAME_SCREEN_H - st.GUI_HEIGHT))
        self.screen_rect = self.screen.get_rect()
        self.world_screen_rect = self.world_screen.get_rect()
        self.world_screen_rect.topleft = (0, st.GUI_HEIGHT)
        self.display_rect = self.actual_screen.get_rect()
        self.fps = st.FPS
        self.all_sprites = pg.sprite.Group()
        self.gui_elements = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        
        self.fonts = {
                'default': pg.font.SysFont(st.DEFAULT_FONT, 18)
                }
        
        self.base_dir = os.path.join(os.path.dirname( __file__ ), '..')
        
# =============================================================================
#         self.map_files = ['sample_map.tmx']
#         self.map_files = [os.path.join(self.base_dir, 'data', 'tilemaps', m) 
#                           for m in self.map_files] #TODO: this belongs in load_assets.py
#         self.save_dir = os.path.join(self.base_dir, 'data', 'saves')
#         
#         self.asset_loader = Loader(self)
#         self.graphics = self.asset_loader.load_graphics()
#         self.asset_loader.load_sounds()
# =============================================================================
        
        self.gamepad_controller = controls.GamepadController()
        self.key_getter = controls.KeyGetter(self)
        
        
        self.setup_states()
        
        self.debug_mode = True
    
    
    def setup_states(self):
        # get a dictionary with all classes from the 'states' module
        self.state_dict = {
                'test_state': test_state
                }
        # define the state at the start of the program
        self.state_name = 'test_state'
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


    def events(self):
        '''empty the event queue and pass the events to the states'''
        self.events_list = pg.event.get()
        for event in self.events_list:
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F12:
                    self.debug_mode = not self.debug_mode
            self.state.get_event(event)


    def update(self, dt):
        # get input before state updates
        self.gamepad_controller.update()
        self.key_getter.get_input(self.gamepad_controller, self.events_list)
        
        #self.key_getter.test_inputs(self.keydown)
        #self.gamepad_controller.test_inputs('inputs_down')

        if self.state.done:
            self.flip_state()
        self.state.update(dt)


    def draw(self):
        # draw everything that happens in the current state
        self.state.draw()
        
        # transform the drawing surface to the window size
        transformed_screen = pg.transform.scale(self.screen,(st.WINDOW_W, 
                                                             st.WINDOW_H))
        # blit the drawing surface to the application window
        self.actual_screen.blit(transformed_screen, (0, 0))
        pg.display.update()


    def run(self):
        self.running = True
        while self.running:
            delta_time = self.clock.tick(self.fps) / 1000 # "dt"
            self.events()
            self.update(delta_time)
            self.draw()

        pg.quit()
        
        
        
        
        
        
class Test_sprite(spr.Animated_sprite):
    def __init__(self, game, **kwargs):
        s = pg.Surface((24, 24))
        s.fill(pg.Color('White'))
        images = {
                'Moving': [s] * 10
                }
        super().__init__(game, images, **kwargs)
        
        self.hitbox = pg.Rect((0, 0), st.PLAYER_HITBOX_SIZE)
        self.acc = vec()
        self.vel = vec()
        self.speed = 1000
        self.friction = 0.7
        
        # stats
        self.hp = 3.0
        self.max_hp = st.PLAYER_HP_START
        self.mana = 10
        self.max_mana = 10
        
        # setup state machine
        self.state_dict = {
                'Moving': self.Moving
                }
        self.state_name = 'Moving'
        self.state = self.state_dict[self.state_name](self)
        self.state.startup()
    
    
    class Moving(spr.State):
        ''' this is the default state for the player '''
        def __init__(self, sprite):
            super().__init__(sprite.game, sprite)
            self.next = 'Test_state'
            
            self.sprite.lastdir = spr.DOWN
        
        
        def startup(self):
            super().startup()
            
            self.sprite.anim_timer = 0 # time in seconds
            self.sprite.anim_delay = 0.2 # animation delay in seconds
            self.sprite.anim_frame = 0 # current index of the images list
            
        
        def update(self, dt):
            self.sprite.move(self, dt)
            self.sprite.collide()
            self.sprite.animate(dt)
            


    def update(self, dt):
        super().update(dt)
    
    
    def move(self, state, dt):
        keys = self.game.keys_pressed

        self.acc *= 0
        self.acc.x = keys['RIGHT'] - keys['LEFT']
        self.acc.y = keys['DOWN'] - keys['UP']
        if self.acc.length() > 1:
            self.acc.scale_to_length(1)
        self.vel += self.acc * self.speed * dt
        self.vel *= self.friction
        self.pos += self.vel * dt
        
        # select the images
        if self.vel.length() < 10:
            self.vel *= 0
            images = self.image_dict[state.name]
            self.images = [images[self.lastdir]] # TODO: select the idle images
        else:
            images = self.image_dict[state.name]
            if self.acc.x > 0:
                self.images = images[2:4]
                self.lastdir = spr.RIGHT
            elif self.acc.x < 0:
                self.images = images[6:8]
                self.lastdir = spr.LEFT
            if self.acc.y > 0:
                self.images = images[0:2]
                self.lastdir = spr.DOWN
            elif self.acc.y < 0:
                self.images = images[4:6]
                self.lastdir = spr.UP
    
    
    def collide(self):
        self.rect.center = self.pos
        # collision detection
        self.hitbox.centerx = self.pos.x
        utils.collide_with_walls(self, self.game.walls, 'x')
        self.hitbox.centery = self.pos.y
        utils.collide_with_walls(self, self.game.walls, 'y')

        
        
class test_state(states.State):
    def __init__(self, game):
        states.State.__init__(self, game)
        self.next = None
    
    
    def startup(self):
        player_properties = {
                'x': 100,
                'y': 90,
                'width': 16,
                'height': 16
                }
        self.game.player = Test_sprite(self.game, **player_properties)
        
        wall_properties = {
                'x': 100,
                'y': 110,
                'width': 80,
                'height': 40
                }
        spr.Wall(self.game, **wall_properties)
    
    def update(self, dt):
        self.game.all_sprites.update(dt)
        
    
    def draw(self):
        self.game.screen.fill(pg.Color('darkgreen'))
        for sprite in self.game.all_sprites:
            sprite.draw(self.game.screen, sprite.rect)
            if hasattr(sprite, 'hitbox'):
                pg.draw.rect(self.game.screen, pg.Color('Red'), 
                             sprite.hitbox, 1)
        for wall in self.game.walls:
            wall.draw(self.game.screen, wall.rect)
            if hasattr(wall, 'hitbox'):
                pg.draw.rect(self.game.screen, pg.Color('Red'), 
                             wall.hitbox, 1)


if __name__ == '__main__':
    try:
        tg = Test_game()
        tg.run()
    except Exception:
        traceback.print_exc()
        pg.quit()
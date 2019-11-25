import pygame as pg
from inventory import Inventory
import items
import settings as st
import sprites as spr
import tilemaps
import utilities as utils




'''
Based on the state machine tutorial by metulburr
https://python-forum.io/Thread-PyGame-Creating-a-state-machine
'''


class State(object):
    '''parent class for all states'''
    def __init__(self, game):
        self.name = 'default'
        self.game = game
        self.next = None # what comes after if this is done
        self.done = False # if true, the next state gets executed
        self.previous = None # the state that was executed before#
    
    def __repr__(self):
        return self.name
    
    def startup(self):
        pass
    
    def cleanup(self):
        pass
    
    def get_event(self, event):
        pass
    
    def update(self, dt):
        pass
    
    def draw(self):
        pass
    


class Game_start(State):
    '''
    This state is called once at the beginning of the game
    it initialises all persistent objects (like the player, inventory etc)
    '''
    def __init__(self, game):
        State.__init__(self, game)
        self.next = 'In_game'
    
    
    def startup(self):
        self.game.map = tilemaps.Map(self.game, self.game.map_files[1])
        self.game.map.create_map()
        self.game.map.rect.topleft = (0, st.GUI_HEIGHT)
        
        # TODO: the player is part of the map data. probably changing this(?)
        self.game.player = self.game.all_sprites.sprites()[0]
        
        self.game.inventory = Inventory(self.game)
        
        # TODO: Testing
        self.game.inventory.add_item(items.Sword, 0, 0)
        
        self.game.camera = utils.Camera(self.game, self.game.map.size.x, 
                                        self.game.map.size.y, 'SLIDE')
        
        spr.Textbox(self.game, self.game.world_screen_rect.center, 
                    self.game.texts['demo_dialog'], 
                    lambda: self.game.change_state('In_game'))
        
        self.done = True
    
    
    def cleanup(self):
        pass


class In_game(State):
    '''
    This is the default in game state where the user can control the 
    player sprite
    '''
    def __init__(self, game):
        State.__init__(self, game)
# =============================================================================
#     def cleanup(self):
#         self.game.save('test.json')
# =============================================================================
    def startup(self):
        pass
    
    def update(self, dt):
        if not self.game.camera.is_sliding:
            self.game.all_sprites.update(dt)
            self.game.gui_elements.update(dt)
        self.game.camera.update(self.game.player, dt)
        
# =============================================================================
#         if self.game.keydown['A']:
#             self.game.asset_loader.play_sound('test_sound')
# =============================================================================
            
        
        if self.game.keydown['START']:
            self.next = 'Menu_open'
            self.done = True
              
        
    def draw(self):
        #self.game.game_screen.fill(pg.Color('black'))
        
        # draw map layers
        # TODO: draw some layers above sprites
        # (each sprite and map layer should have a layer number)
        for i, layer in enumerate(self.game.map.layers):
            self.game.game_screen.blit(layer, 
                                  self.game.camera.apply_bg(self.game.map.rect))
            # draw reflections
            # TODO: have the layer have a "reflection" attribute
            if i == 0:
                for sprite in self.game.all_sprites:
                    if hasattr(sprite, 'draw_reflection'):
                        sprite.draw_reflection(self.game.game_screen, 
                                               self.game.camera.apply(sprite))
        
        for sprite in self.game.all_sprites:
            sprite.draw(self.game.game_screen, self.game.camera.apply(sprite))
            if self.game.debug_mode:
                if hasattr(sprite, 'hitbox'):
                    pg.draw.rect(self.game.game_screen, pg.Color('Red'), 
                                 self.game.camera.apply_rect(sprite.hitbox), 1)
        
        for wall in self.game.walls:
            wall.draw(self.game.game_screen, self.game.camera.apply(wall))
        
        for elem in self.game.gui_elements:
            # TODO: pass screen argument
            elem.draw()
        
# =============================================================================
#         for s in self.game.all_sprites:
#             pg.draw.rect(screen, pg.Color('white'), self.camera.apply_rect(s.rect), 1)
# =============================================================================


class Dialog(In_game):
    '''
    Testing the cutscene state
    TODO: maybe this has to be invoked by the textbox itself for convenience
    '''
    def __init__(self, game):
        State.__init__(self, game)
        self.next = 'In_game'
    
    
    def startup(self):
        pass
    
    
    def update(self, dt):
        self.game.cutscene_elements.update(dt)
        
    
    def draw(self):
        super().draw()
        for elem in self.game.cutscene_elements:
            # TODO: pass screen argument
            elem.draw()


class Title_screen(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.next = 'Game_start'
        

    def get_event(self, event):
        # press any key to continue
        if event.type == pg.KEYDOWN or self.game.gamepad_controller.any_key():
            self.done = True
                       
    
    def update(self, dt):
        pass
              
        
    def draw(self):
        self.game.game_screen.fill(pg.Color('red'))
        # TODO: replace with utils.draw_text
        txt = 'DUNGEON CRUSADER'
        txt_surf, txt_rect = self.game.fonts['default_big'].render(txt, 
                                                    fgcolor=pg.Color('White'),
                                                    bgcolor=None)
                                                    
        txt_rect.centerx = self.game.game_screen_rect.centerx
        txt_rect.centery = self.game.game_screen_rect.centery - 16
        
        self.game.game_screen.blit(txt_surf, txt_rect)
        
        txt = 'Press any key to start.'
        txt_surf, txt_rect = self.game.fonts['default_small'].render(txt, 
                                                    fgcolor=pg.Color('White'),
                                                    bgcolor=None)
                                                    
        txt_rect.centerx = self.game.game_screen_rect.centerx
        txt_rect.centery = self.game.game_screen_rect.centery + 16
        
        self.game.game_screen.blit(txt_surf, txt_rect)
        


class Menu_open(In_game):
    '''
    inherits In_game because it adds only to the draw function
    '''
    def __init__(self, game):
        super().__init__(game)
        self.next = 'In_menu'
    
    
    def cleanup(self):
        pass
    
    
    def update(self, dt):
        # call menu opening animation
        # that returns True if its finished
        self.game.gui_elements.update(dt)
        self.game.camera.update(self.game.player, dt)
        
        if self.game.inventory.menu_open(dt):
            self.done = True
    
    
    def draw(self):
        super().draw()


class Menu_close(In_game):
    '''
    inherits In_game because it adds only to the draw function
    '''
    def __init__(self, game):
        super().__init__(game)
        self.next = 'In_game'
        
    
    def cleanup(self):
        pass

    
    def update(self, dt):
        # call menu closing animation
        # that returns True if its finished
        self.game.gui_elements.update(dt)
        self.game.camera.update(self.game.player, dt)
        
        if self.game.inventory.menu_close(dt):
            self.done = True
    
    
    def draw(self):
        super().draw()
    

class In_menu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.next = 'Menu_close'
        
    
    def update(self, dt):
        self.game.inventory.update(dt)
        
        if self.game.keydown['START']:
            self.done = True
    
    
    def draw(self):
        self.game.inventory.draw()
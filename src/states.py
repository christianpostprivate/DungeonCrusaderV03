import pygame as pg
import interface as inter
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
        self.game = game
        self.next = None # what comes after if this is done
        self.done = False # if true, the next state gets executed
        self.previous = None # the state that was executed before
        
        if not hasattr(self, 'name'):
            self.name = 'State'
    
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
    


class GameStart(State):
    '''
    This state is called once at the beginning of the game
    it initialises all persistent objects (like the player, inventory etc)
    '''
    def __init__(self, game):
        State.__init__(self, game)
        self.next = 'InGame'
    
    
    def startup(self):
        # TODO: overworld grid should consist of multiple maps
        # TODO: the grid construction should be done from json data
        maps = [
            tilemaps.Map(self.game, self.game.map_files[2]),
            tilemaps.Map(self.game, self.game.map_files[3]),
            tilemaps.Map(self.game, self.game.map_files[4])
        ]
        self.game.overworld_grid = tilemaps.Grid(self.game,
                                                 name='overworld',
                                                 width=2,
                                                 height=2)
        self.game.overworld_grid.insert_grid(maps[0], 0, 0)
        self.game.overworld_grid.insert_grid(maps[1], 1, 0)
        self.game.overworld_grid.insert_grid(maps[2], 0, 1)

        self.game.map = maps[0]
        self.game.map.create_map()

        # put the player somewhere on the map
        self.game.player = spr.Player(self.game, {'x': 182, 'y': 136,
                                                  'width': 16, 'height': 16})
        
        self.game.inventory = inter.Inventory(self.game)
        self.game.inventory.active = True
        
        # TODO: Testing
        self.game.inventory.add_item(items.Sword, 0, 0)
        self.game.inventory.add_item(items.Test, 0, 1)
        
        self.game.camera = utils.Camera(self.game, self.game.map.size.x, 
                                        self.game.map.size.y, 'FOLLOW')
        self.game.camera.update(self.game.player)
        
        t = inter.Textbox(self.game, self.game.world_screen_rect.center, 
                      self.game.texts['demo_dialog'], 
                      lambda: self.game.change_state('InGame'))
        #t.activate()
        
        
        spr.Enemy(self.game, {'x':300, 'y':100, 'width':16, 'height':16})
        
        
        self.game.select_menu = inter.Base_menu(self.game,
                                                rect=None,
                                                anchor_x='centerx')
        e1 = inter.Menu_entry('Resume Game', self.game.select_menu.deactivate)
        e2 = inter.Menu_entry('Go To Title Screen',
                              lambda: self.game.change_state('TitleScreen'))
        e3 = inter.Menu_entry('Exit Program', self.game.exit_game)
        self.game.select_menu.add_entries(e1, e2, e3)
        
        self.done = True
    
    
    def cleanup(self):
        pass


class InGame(State):
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
    
    
    def cleanup(self):
        if self.game.state.next == 'TitleScreen':
            # If user quits the game to title
            # TODO: probably add a save prompt here
            self.game.all_sprites.empty()
            self.game.gui_elements.empty()
        
    
    def update(self, dt):
        if not self.game.camera.is_sliding:
            self.game.all_sprites.update(dt)
            self.game.gui_elements.update(dt)
        self.game.camera.update(self.game.player, dt)
        
        if self.game.keydown['START']:
            self.next = 'MenuOpen'
            self.done = True
        
        elif self.game.keydown['SELECT']:
            self.game.select_menu.activate()
            self.next = 'Menu'
            self.done = True

        # map transition
        # TODO this seems wrong, refactor that map.rect is offset by gui height in display
        # TODO: change game state to screen transition
        # TODO: put this in function(s) of map object
        change_x = 0
        change_y = 0
        # initialise map transition
        if self.game.player.pos.x > self.game.map.rect.w:
            change_x = 1
        elif self.game.player.pos.x < self.game.map.rect.x:
            change_x = -1
        if self.game.player.pos.y > self.game.map.rect.h:
            change_y = 1
        elif self.game.player.pos.y < self.game.map.rect.y - st.GUI_HEIGHT:  # TODO: weird
            change_y = -1

        if change_x != 0 or change_y != 0:
            new_player_pos = tilemaps.vec(self.game.player.pos)
            if change_x > 0:
                new_player_pos.x -= self.game.map.rect.w
            elif change_x < 0:
                new_player_pos.x += self.game.map.rect.w

            if change_y > 0:
                new_player_pos.y -= self.game.map.rect.h
            elif change_y < 0:
                new_player_pos.y += self.game.map.rect.h
            new_x = max(0, self.game.map_index_x + change_x)
            new_y = max(0, self.game.map_index_y + change_y)
            self.game.overworld_grid.teleport(new_x, new_y, new_player_pos)
        
        
    def draw(self):
        # TODO: background color
        #self.game.game_screen.fill(pg.Color('black'))
        
        # draw map layers
        # TODO: draw some layers above the sprites
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
        
        # for wall in self.game.walls:
        #     wall.draw(self.game.game_screen, self.game.camera.apply(wall))
        
        for elem in self.game.gui_elements:
            # TODO: pass screen argument
            elem.draw()

        if self.game.debug_mode:
            pg.draw.rect(self.game.world_screen, pg.Color('white'),
                         self.game.camera.apply_rect(self.game.map.rect))
            
            for e in self.game.enemies:
                if hasattr(e, 'aggro_dist'):
                    pg.draw.circle(self.game.game_screen, pg.Color('red'),
                                   self.game.camera.apply_point(e.pos), 
                                   e.aggro_dist, 1)
                    pg.draw.circle(self.game.game_screen, pg.Color('green'),
                                   self.game.camera.apply_point(e.pos), 
                                   e.idle_dist, 1)
                    if hasattr(e.state, 'target'):
                        pg.draw.line(self.game.game_screen, 
                                     pg.Color('blue'),
                                     self.game.camera.apply_point(e.pos),
                                     self.game.camera.apply_point(e.state.target))
            
            # pg.draw.line(self.game.game_screen, pg.Color('white'),
            #              self.game.world_screen_rect.midleft,
            #              self.game.world_screen_rect.midright)
            # pg.draw.line(self.game.game_screen, pg.Color('white'),
            #              self.game.world_screen_rect.midtop,
            #              self.game.world_screen_rect.midbottom)
# =============================================================================
#         for s in self.game.all_sprites:
#             pg.draw.rect(screen, pg.Color('white'), self.camera.apply_rect(s.rect), 1)
# =============================================================================


class Dialog(InGame):
    '''
    Testing the cutscene state
    TODO: maybe this has to be invoked by the textbox itself for convenience
    '''
    def __init__(self, game):
        State.__init__(self, game)
        self.next = 'InGame'
    
    
    def startup(self):
        pass
    
    
    def update(self, dt):
        self.game.cutscene_elements.update(dt)
        
    
    def draw(self):
        super().draw()
        for elem in self.game.cutscene_elements:
            # TODO: pass screen argument
            # TODO: super lazy hack, for some reason after a state switch
            # the draw function is happening once before the update function...
            if hasattr(elem, 'image'):
                elem.draw()



class Menu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.next = 'InGame'
    
    
    def update(self, dt):
        self.game.gui_elements.update(dt)
        
    
    def draw(self):
        super().draw()
        for elem in self.game.gui_elements:
            # TODO: pass screen argument
            elem.draw()
        


class TitleScreen(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.next = 'GameStart'
        
        self.menu = inter.Base_menu(game=self.game,
                                    background_color=pg.Color('black'),
                                    rect=pg.Rect(0, 0, 
                                                 self.game.game_screen_rect.w,
                                                 self.game.game_screen_rect.h * 0.5),
                                    pos=(self.game.game_screen_rect.w / 2,
                                         self.game.game_screen_rect.h / 3 * 2))
        self.menu.add_entries(
                inter.Menu_entry('New Game',
                                 lambda: self.game.change_state('GameStart')),
                inter.Menu_entry('Quit', self.game.exit_game)
                )

    def startup(self):
        self.menu.activate()
    
    
    def cleanup(self):
        self.menu.deactivate()
        

    def get_event(self, event):
        # press any key to continue
        if event.type == pg.KEYDOWN or self.game.gamepad_controller.any_key():
            #self.done = True
            pass
                       
    
    def update(self, dt):
        for elem in self.game.gui_elements:
            # TODO: pass screen argument
            elem.update(dt)
              
        
    def draw(self):
        self.game.game_screen.fill(pg.Color('black'))

        utils.draw_text(self.game.game_screen, 'DUNGEON CRUSADER', 
                        self.game.fonts['default_big'], pg.Color('white'),
                        (self.game.game_screen_rect.centerx, 64),
                        align='center')
        
        for elem in self.game.gui_elements:
            # TODO: pass screen argument
            elem.draw()



class MenuOpen(InGame):
    '''
    inherits In_game because it adds only to the draw function
    '''
    def __init__(self, game):
        super().__init__(game)
        self.next = 'ItemMenu'
    
    
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


class MenuClose(InGame):
    '''
    inherits In_game because it adds only to the draw function
    '''
    def __init__(self, game):
        super().__init__(game)
        self.next = 'InGame'
        
    
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
    

class ItemMenu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.next = 'MenuClose'
        
    
    def update(self, dt):
        self.game.inventory.update(dt)
        
        if self.game.keydown['START']:
            self.done = True
    
    
    def draw(self):
        self.game.inventory.draw()
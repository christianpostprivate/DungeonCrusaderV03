import pygame as pg
import settings as st
import utilities as utils

vec = pg.math.Vector2


class Inventory(pg.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        super().__init__(game.gui_elements)
        
        # define size, image and rect
        self.size = vec(st.GAME_SCREEN_W, st.GAME_SCREEN_H)
        self.image = pg.Surface(self.size)
        self.rect = self.image.get_rect()
        
        # start pos when the inventory is closed
        self.start_pos = vec(0, (0 - self.rect.h + st.GUI_HEIGHT))
        self.rect.topleft = self.start_pos
        
        # graphics
        self.bg_image_overlay = self.game.graphics['inventory_bg']
        self.cursor_images = self.game.graphics['cursor_images']
        self.health_string = self.game.graphics['health_string']
        self.heart_images = self.game.graphics['heart_images']
        self.magic_image = self.game.graphics['magic_and_items']
        self.magic_bar = self.game.graphics['magicbar']
        
        # lay the transparent bg_image_overlay on top of the black bg image
        # this prevents filling it every frame
        self.bg_image = pg.Surface(self.size)
        self.bg_image.fill(pg.Color('black'))
        self.bg_image.blit(self.bg_image_overlay, (0, 0))
        
        self.bar_stretch = 100
        
        self.cursor_pos = vec(24, 40)
        self.inv_index = [0, 0]
        self.inv_size = [5, 5]
        
        self.inv_items = [[None for j in range(self.inv_size[1])] 
                           for i in range(self.inv_size[0])] 
        
        self.item_slot_positions = {
                'A': (111, 216),
                'B': (135, 216)
                }
        
        # animation parameters
        self.anim_timer = 0
        self.anim_frame = 0
        self.anim_delay = 0.4
        
    
    def update(self, dt):
        if isinstance(self.game.state, self.game.state_dict['In_menu']):
            self.move_cursor()

        self.animate_cursor(dt)
    
    
    def move_cursor(self):
        move = vec()
        move.x = self.game.keydown['RIGHT'] - self.game.keydown['LEFT']
        move.y = self.game.keydown['DOWN'] - self.game.keydown['UP']
        
        # change the inventory index
        self.inv_index[0] += int(move.x)
        self.inv_index[1] += int(move.y)
        self.inv_index[0] = utils.clamp(self.inv_index[0], 0, self.inv_size[0] - 1)
        self.inv_index[1] = utils.clamp(self.inv_index[1], 0, self.inv_size[1] - 1)
        
        # move the cursor
        self.cursor_pos += move * 24
        self.cursor_pos.x = utils.clamp(self.cursor_pos.x, 24, 120)
        self.cursor_pos.y = utils.clamp(self.cursor_pos.y, 40, 136)
        
        # restart animation if curser is moved
        if move != (0, 0):
            self.anim_timer = 0
            self.anim_frame = 0
    
    
    def draw(self):
        # construct the inventory image
        self.image.blit(self.bg_image, (0, 0))
        self.draw_cursor()
        self.draw_hud()
        self.draw_items()
        self.game.game_screen.blit(self.image, self.rect)
    
    
    def animate_cursor(self, dt):
        self.anim_timer += dt
        if self.anim_timer >= self.anim_delay:
            # reset the timer
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % len(
                                  self.cursor_images)


    def draw_cursor(self):
        self.image.blit(self.cursor_images[self.anim_frame], self.cursor_pos)
    
    
    def draw_hud(self):
        player = self.game.player
        for i in range(int(player.max_hp)):
        # calculate position
            if i < st.PLAYER_HP_ROW:
                # first row
                pos = (6 + 10 * i, st.GAME_SCREEN_H - 34)
            else:
                # second row
                pos = (6 + 10 * (i - st.PLAYER_HP_ROW), st.GAME_SCREEN_H - 24)
            
            # draw heart image based on fraction of health
            if i < int(player.hp):
                # full heart
                img = self.heart_images[1]
            elif i == int(player.hp):
                if player.hp % 1 == 0.25:
                    img = self.heart_images[4]
                elif player.hp % 1 == 0.5:
                    img = self.heart_images[3]
                elif player.hp % 1 == 0.75:
                    img = self.heart_images[2]
                else:
                    img = self.heart_images[5]
            else:
                # empty heart
                img = self.heart_images[5]

            self.image.blit(img, pos)
        
        self.image.blit(self.health_string, (25, st.GAME_SCREEN_H - 42))
        
        # draw magic bar and item slots
        # TODO: might want to split into single images
        bar_stretched = self.magic_bar.copy()
        mana_pct = self.game.player.mana / self.game.player.max_mana
        factor = mana_pct * 28
        one_minus_factor = int((1 - mana_pct) * 27)
        bar_stretched = pg.transform.scale(bar_stretched, 
                       (bar_stretched.get_width(), int(factor)))
        self.image.blit(bar_stretched, (82, st.GAME_SCREEN_H - 31 + one_minus_factor))
        
        self.image.blit(self.magic_image, (77, st.GAME_SCREEN_H - 48))
        
        # draw other item amounts
        # rupees
        x_off = 167
        text_pos = vec(x_off, 201)
        number = f'x{self.game.player.item_counts.get("rupee", 0):02d}'
        #utils.draw_text(self.image, number, font, font_size, pg.Color('White'), 
        #                text_pos, align='midleft')
        utils.draw_text(surface=self.image, 
                        text=number, 
                        font=self.game.fonts['slkscr_8'], 
                        color=pg.Color('White'),
                        pos=text_pos, 
                        align='midleft')
        
        # keys
        text_pos = vec(x_off, 217)
        number = f'x{self.game.player.item_counts.get("small_key", 0):02d}'
        #utils.draw_text(self.image, number, font, font_size, pg.Color('White'), 
        #                text_pos, align='midleft')
        utils.draw_text(surface=self.image, 
                        text=number, 
                        font=self.game.fonts['slkscr_8'], 
                        color=pg.Color('White'),
                        pos=text_pos, 
                        align='midleft')
    
    def draw_items(self):
        # draw the inventory item images
        player = self.game.player
        for i in range(self.inv_size[0]):
            for j in range(self.inv_size[1]):
                pos = vec()
                pos.x = (24 + 24 * i)
                pos.y = (40 + 24 * j)
                
                item = self.inv_items[j][i]
                
                if item:
                    item_img = self.game.graphics['inventory_images'][item.inventory_image_index]
                    self.image.blit(item_img, pos)
                  
        # draw item name
        text_pos = vec(80, 168)
        item = self.inv_items[self.inv_index[1]][self.inv_index[0]]
        if item:
            '''
            txt_surf, txt_rect = self.game.fonts['slkscr_8'].render(item.name, 
                                            fgcolor=pg.Color('White'),
                                            bgcolor=None)
            txt_rect.center = text_pos
            self.image.blit(txt_surf, txt_rect)
            '''
            utils.draw_text(surface=self.image, 
                            text=item.name, 
                            font=self.game.fonts['slkscr_8'], 
                            color=pg.Color('White'),
                            pos=text_pos, 
                            align='center')
        
        # draw the two item slots
        for slot, pos in self.item_slot_positions.items():
            if self.game.player.items[slot]:
                item_img = self.game.graphics['inventory_images'][player.items[slot].inventory_image_index]
                self.image.blit(item_img, pos)
    
    
    def add_item(self, item_class, column, row):
        self.inv_items[row][column] = item_class
        
    
    def menu_open(self, dt):
        if self.rect.y != 0:
            self.rect.y += st.SCROLLSPEED_MENU * dt
            self.rect.y = min(0, self.rect.y)
            return False
        else:
            return True
            
    
    def menu_close(self, dt):
        if self.rect.y != self.start_pos.y:
            self.rect.y -= st.SCROLLSPEED_MENU * dt
            self.rect.y = max(st.GUI_HEIGHT - self.rect.h, self.rect.y)
            return False
        else:
            return True
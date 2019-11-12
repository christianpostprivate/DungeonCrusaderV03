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
        self.image.fill(pg.Color('black'))
        self.rect = self.image.get_rect()
        
        # start pos when the inventory is closed
        self.start_pos = vec(0, (0 - self.rect.h + st.GUI_HEIGHT))
        self.rect.topleft = self.start_pos
        
        # graphics
        self.bg_image = self.game.graphics['inventory_bg']
        self.cursor_images = self.game.graphics['cursor_images']
        self.health_string = self.game.graphics['health_string']
        self.heart_images = self.game.graphics['heart_images']
        self.magic_image = self.game.graphics['magic_and_items']
        self.magic_bar = self.game.graphics['magicbar']
        
        self.bar_stretch = 100
        
        self.cursor_pos = vec(24, 40)
        self.inv_index = [0, 0]
        self.inv_size = [5, 5]
        
        # animation parameters
        # TODO: fit to dt
        self.anim_update = 0
        self.anim_delay = 300
        self.current_frame = 0
        
    
    def update(self, dt):
        if isinstance(self.game.state, self.game.state_dict['In_menu']):
            self.move_cursor()
    
    
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
            self.anim_update = self.anim_delay / 2 + pg.time.get_ticks()
            self.current_frame = 0
    
    
    def draw(self):
        self.image.fill(pg.Color('black'))
        # draw the inventory background
        self.image.blit(self.bg_image, (0, 0))
        
        self.draw_cursor()
        self.draw_hud()
        
        self.game.game_screen.blit(self.image, self.rect)
        
    
    def draw_cursor(self):
        now = pg.time.get_ticks()
        if now - self.anim_update > self.anim_delay:
            self.anim_update = now
            self.current_frame = (self.current_frame + 1) % len(
                                  self.cursor_images)
        self.image.blit(self.cursor_images[self.current_frame], self.cursor_pos)
    
    
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
        font = self.game.asset_loader.fonts['slkscr']
        font_size = 8
        x_off = 167
        text_pos = vec(x_off, 201)
        number = f'x{self.game.player.item_counts.get("rupee", 0):02d}'
        utils.draw_text(self.image, number, font, font_size, pg.Color('White'), 
                        text_pos, align='midleft')
        
        # keys
        text_pos = vec(x_off, 217)
        number = f'x{self.game.player.item_counts.get("small_key", 0):02d}'
        utils.draw_text(self.image, number, font, font_size, pg.Color('White'), 
                        text_pos, align='midleft')
        
    
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
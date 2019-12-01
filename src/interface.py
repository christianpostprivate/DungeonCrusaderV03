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
        
        self.active = False
        
    
    def update(self, dt):
        if self.active:
            if isinstance(self.game.state, self.game.state_dict['Item_menu']):
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
            
        # assign an item to a slot
        player = self.game.player 
        x = self.inv_index[1]
        y = self.inv_index[0]                     
        if self.game.keydown['A']:
            if self.inv_items[x][y]:
                # put the item into slot A
                # if there is already an item, put it in slot B
                # if the item is already in slot B, clear slot B
                lastA = player.items['A']
                player.items['A'] = self.inv_items[x][y]
                if player.items['A'] and player.items['B'] == None:
                    player.items['B'] = player.items['A']
                if player.items['B'] == self.inv_items[x][y]:
                    player.items['B'] = lastA
                if player.items['B'] == player.items['A']:
                    player.items['B'] = None
            else:
                # if no item is at x, y
                # TODO play sound 
                pass
        
        if self.game.keydown['B']:
            if self.inv_items[x][y]:
                # put the item into slot B
                lastB = player.items['B']
                player.items['B'] = self.inv_items[x][y]
                if player.items['B'] and player.items['A'] == None:
                    player.items['A'] = player.items['B']
                if player.items['A'] == self.inv_items[x][y]:
                    player.items['A'] = lastB
                if player.items['A'] == player.items['B']:
                    player.items['A'] = None
            else:
                # if no item is at x, y
                # TODO play sound 
                pass
    
    
    def draw(self):
        if self.active:
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


class Textbox(pg.sprite.Sprite):
    def __init__(self, game, pos, text, callback_when_done=None):
        super().__init__(game.cutscene_elements)
        self.game = game
        if self.game.state != 'Dialog':
            self.game.change_state('Dialog')
        # provide a function that is executed when the textbox is finished
        self.callback = callback_when_done

        self.size = (180, 64)
        self.pos = vec(pos)
        # set textbox vertical position based on players position
        if self.game.player.rect.y > self.game.world_screen_rect.centery:
            self.pos.y *= 0.5
        else:
            self.pos.y *= 1.25
        self.image_original = pg.Surface(self.size)
        self.image_original.fill(pg.Color('black')) # TODO make customizable
        self.rect = self.image_original.get_rect()
        self.rect.center = self.pos
        
        self.text = text
        self.font = game.fonts['slkscr_8']
        
        self.words_left = []
        self.words_prev = []

        self.done = False
        self.scroll = False
        self.text_end = False
        self.timer = 0
        self.popup_time = 0.5

        self.margin = vec(4, 4)
        self.spacing = self.font.get_sized_height() + 2

        #self.cursor = Cursor(self.game, self.rect.midbottom, 'S')
    
    
    def popUp(self, dt):
        if self.timer < self.popup_time and not self.done:
            # enlarge the textbox image gradually
            # calculate the new width and height by lerping
            w = int((self.timer / self.popup_time) * self.size[0])
            h = int((self.timer / self.popup_time) * self.size[1])
            # scale the image
            self.image = self.image_original.copy()
            self.image = pg.transform.scale(self.image, (w, h))
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.timer += dt
        else:
            self.done = True
            self.timer = 0
            
    
    def vanish(self, dt):
        self.done = False
        if self.timer < self.popup_time:
            # shrink the textbox image gradually
            # calculate the new width and height by lerping
            w = int(self.size[0] - (self.timer / self.popup_time) * self.size[0])
            h = int(self.size[1] - (self.timer / self.popup_time) * self.size[1])
            # scale the image
            self.image = self.image_original.copy()
            self.image = pg.transform.scale(self.image, (w, h))
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.timer += dt
        else:
            self.kill()
            if self.callback:
                self.callback()
    
    
    def renderText(self):
        line = 0
        color = pg.Color('white')
        txt = ''
        txt_temp = ''
        # create a list of words from the string
        if len(self.words_left) == 0:
            # if words_left is emtpy, use self.text
            words = self.text.split(' ')
        else:
            # if there is text left, use it
            words = self.words_left

        for i in range(len(words)):
            if words[i] == words[-1]:
                self.text_end = True

            if words[i] == '$nl':
                # if words[i] ist the newline indicator,
                # clear txt_temp and move to the next line
                txt_temp = ''
                line += 1
            else:
                # add the next word to the temporary text
                txt_temp += words[i] + ' '
            text_surface, text_rect = self.font.render(txt_temp, color)

            h = (text_rect.h * line + self.spacing *
                 max(0, line - 3))

            if h < self.rect.height - self.margin.y * 2:
                if text_rect.w < self.rect.width - self.margin.x * 2:
                    # if text rect fits, render it
                    txt = txt_temp
                    text_surface, text_rect = self.font.render(txt, color)
                    text_rect.topleft = (self.margin.x, self.margin.y +
                                         self.spacing * line)
                    self.image.blit(text_surface, text_rect)

                else:
                    # if the text rect is wider than the Textbox,
                    # move to next line and set the current word as the first
                    # word in txt_temp
                    line += 1
                    txt_temp = words[i] + ' '

            else:
                if self.scroll:
                    self.words_left = words[i - 1:]
                    self.scroll = False
                break

        if self.game.keydown['A'] or self.game.keydown['B']:
            # scroll if the player hits the key assigned to A or B
            self.scroll = True

    
    def update(self, dt):
        if not self.done and not self.text_end:
            # player pop up animation until done
            self.popUp(dt)

        if self.text_end and self.scroll:
            # if text is finished and user scrolls, play vanish animation
            self.vanish(dt)
            
    
    def draw(self):
        if self.done:
            self.image.fill(pg.Color('black'))
            self.renderText()
        self.game.game_screen.blit(self.image, self.rect.topleft)

        #if self.done:
        #    self.cursor.draw(self.game.screen)
        


class Menu_entry:
    def __init__(self, text, callback):
        self.text = text
        self.callback = callback
        self.y = 0



class Base_menu(pg.sprite.Sprite):
    '''
    Base class for all menus with selectable items
    '''
    def __init__(self, game, background_color=pg.Color('black'),
                 background_image=None, rect=None, pos=None, anchor_x='centerx'):

        super().__init__(game.gui_elements)
        self.game = game

        self.rect = rect or self.game.game_screen_rect.copy()
        self.pos = pos or self.game.game_screen_rect.center
        self.rect.center = self.pos
            
        self.background_image = pg.Surface(self.rect.size)
        self.background_image.fill(background_color)
        if background_image:
            self.background_image.blit(background_image)
        
        self.image = pg.Surface(self.rect.size)
        
        self.anchor_x = anchor_x
        self.selected = 0
        
        self.show_cursor = False
        self.anim_timer = 0
        self.anim_delay = 0.25
        
        self.active = False
    
    
    def add_entries(self, *args):
        # count menu entries and set their position
        self.menu_entries = [a for a in args if isinstance(a, Menu_entry)]
        for i, entry in enumerate(self.menu_entries, 1):
            # add a reference to the menu
            entry.menu = self
            # calculate the y position of the text
            div = len(self.menu_entries) + 1
            entry.y = i * self.rect.h / div
        
    
    def activate(self):
        self.previous_state = self.game.state
        #self.game.change_state('Menu')
        self.active = True
    
    
    def deactivate(self):
        #self.game.change_state(self.previous_state.name)
        self.game.state = self.previous_state
        self.active = False
            
    
    def update(self, dt):
        if self.active:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.show_cursor = not self.show_cursor
            
            move_y = self.game.keydown['DOWN'] - self.game.keydown['UP']
            self.selected = (self.selected + move_y) % len(self.menu_entries)
            
            if self.game.keydown['A']:
                if self.menu_entries[self.selected].callback:
                    self.deactivate()
                    self.menu_entries[self.selected].callback()

    
    def draw(self):
        if self.active:
            self.image.blit(self.background_image, (0, 0))
            for i, entry in enumerate(self.menu_entries):
                txt = entry.text
                if i == self.selected and self.show_cursor:
                    txt = f'> {txt} <'
                    #txt = f'> {txt}'
                txt_surf, txt_rect = self.game.fonts['slkscr_16'].render(txt, 
                                                    fgcolor=pg.Color('White'),
                                                    bgcolor=None)
                txt_rect.y = entry.y
                setattr(txt_rect, self.anchor_x, getattr(self.rect, self.anchor_x))
                self.image.blit(txt_surf, txt_rect)
                
            self.game.game_screen.blit(self.image, self.rect)
        
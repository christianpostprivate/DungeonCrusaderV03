import pygame as pg
#from random import randint
import logging

import items
import settings as st
import utilities as utils


vec = pg.math.Vector2

RIGHT = 0
DOWN = 1
LEFT = 2
UP = 3


class State():
    ''' base class for player/NPC state machine '''
    def __init__(self, game, sprite):
        self.game = game
        self.sprite = sprite # the sprite object this state belongs to
        self.next = None # what comes after if this is done
        self.done = False # if true, the next state gets executed
        self.previous = None # the state that was executed before
        self.name = self.sprite.state_name
        
    def startup(self):
        pass
    
    def cleanup(self):
        pass
    
    def update(self, dt):
        pass




class BaseSprite(pg.sprite.Sprite):
    def __init__(self, game, groups, **kwargs):
        '''
        kwargs have to be at least:
            x: x position
            y: y position
            width: rect.w
            height: rect.h
        '''
        self.game = game
        super().__init__(groups)
        
        for key, value in kwargs.items():
            setattr(self, key, value)
        # set additional custom properties (from Tiled 'properties' dict)
        if hasattr(self, 'properties'):
            for key, value in self.properties.items():
                setattr(self, key, value)
        
        self.anim_timer = 0
        self.anim_frame = 0
        self.anim_delay = 0.2 # overwrite this in child class
    
    
    def flip_state(self):
        '''set the state to the next if the current state is done'''
        self.state.done = False
        # set the current and next state to the previous and current state
        previous, self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        self.state = self.state_dict[self.state_name](self)
        self.state.startup()
        self.state.previous = previous
    
    
    def animate(self, dt):
        # loop through all of self.images and set self.image to the next
        # image if the time exceeds the delay
        self.anim_timer += dt
        if self.anim_timer >= self.anim_delay:
            # reset the timer
            self.anim_timer = 0
            # advance the frame
            self.anim_frame = (self.anim_frame + 1) % len(self.images[self.image_state][self.lastdir])
            # set the image and adjust the rect
            self.image = self.images[self.image_state][self.lastdir][self.anim_frame]
            self.rect = self.image.get_rect()
            self.rect.midbottom = self.hitbox.midbottom
    
    
    def update(self, dt):
        self.state.update(dt)
        if self.state.done:
            self.flip_state()
            
    
    def draw(self, screen, pos_or_rect):
        screen.blit(self.image, pos_or_rect)



class Player(BaseSprite):
    ''' The Sprite you control as the player
    '''
    def __init__(self, game, kwargs):
        super().__init__(game, game.all_sprites, **kwargs)
        
        images1 = game.graphics['knight_images']
        images2 = game.graphics['knight_attack']
        self.images = {
            'hit': None, #TODO
            'idle': {
                    RIGHT: images1[2:3],
                    DOWN: images1[8:9],
                    LEFT: images1[6:7],
                    UP: images1[9:10]
                    },
            'walk': {
                    RIGHT: images1[2:4],
                    DOWN: images1[0:2],
                    LEFT: images1[6:8],
                    UP: images1[4:6]
                    },
            'attack': {
                    RIGHT: images2[2:3],
                    DOWN: images2[0:1],
                    LEFT: images2[3:4],
                    UP: images2[1:2],
                    }
            }
        
        self.image_state = 'idle'
        self.direction = DOWN
        self.lastdir = self.direction
        self.image = self.images[self.image_state][self.direction][0]
        
        self.rect = self.image.get_rect()
        self.hitbox = pg.Rect((0, 0), st.PLAYER_HITBOX_SIZE)
        
        self.pos = vec(self.x, self.y)
        self.hitbox.center = self.pos
        self.rect.midbottom = self.hitbox.midbottom
        
        # physics properties
        self.acc = vec()
        self.vel = vec()
        self.speed = 20
        self.friction = 0.8
        
        self.anim_delay = 0.2
        
        # stats
        self.hp = 3.0
        self.max_hp = st.PLAYER_HP_START
        self.mana = 10
        self.max_mana = 10
        
        self.item_counts = {
                'rupee': 0
                }
        
        self.items = {
                'A': items.Sword,
                'B': None
                }
        self.item_using = None
        
        # setup state machine
        self.state_dict = {
                'moving': self.Moving,
                'USE_A': self.Use_item_A,
                'USE_B': self.Use_item_B
                }
        self.state_name = 'moving'
        self.state = self.state_dict[self.state_name](self)
        self.state.startup()
    
    
    class Moving(State):
        ''' this is the default state for the player '''
        def __init__(self, sprite):
            super().__init__(sprite.game, sprite)
            self.next = None
        
        
        def startup(self):
            super().startup()
            
            self.anim_timer = 0
            self.anim_frame = 0
            self.anim_delay = 0.2
            
        
        def update(self, dt):
            self.sprite.move(dt)
            self.sprite.collide_with_walls()
            self.sprite.animate(dt)
            
            if self.game.keydown['A']:
                self.next = 'USE_A'
                self.done = True
            if self.game.keydown['B']:
                self.next = 'USE_B'
                self.done = True
    
    
    class Use_item(State):
        '''parent class for Item using state'''
        def __init__(self, sprite):
            super().__init__(sprite.game, sprite)
            self.next = 'moving'
        
        def startup(self):
            super().startup()
            self.sprite.vel *= 0
            self.sprite.image_state = 'attack'
            if self.sprite.items[self.slot]:
                self.item = self.sprite.items[self.slot](self.sprite, self.game)
            else:
                self.item = None
                self.done = True
            
        
        def update(self, dt):
            self.sprite.animate(dt)
            if self.item and self.item.done:
                self.done = True
    
    
    class Use_item_A(Use_item):
        def __init__(self, sprite):
            super().__init__(sprite)
            self.slot = 'A'

                
    class Use_item_B(Use_item):
        def __init__(self, sprite):
            super().__init__(sprite)
            self.slot = 'B'

    
    
    def collide_with_walls(self):
        # collision detection
        # the center of the hitbox is always at the sprite's position
        self.hitbox.centerx = self.pos.x
        utils.collide_with_walls(self, self.game.walls, 'x')
        self.hitbox.centery = self.pos.y
        utils.collide_with_walls(self, self.game.walls, 'y')
        # the rect(where the image is drawn)'s bottom is aligned with the hitbox's bottom
        self.rect.midbottom = self.hitbox.midbottom
    
    
    def move(self, dt):
        keys = self.game.keys_pressed
        
        self.acc *= 0
        self.acc.x = keys['RIGHT'] - keys['LEFT']
        self.acc.y = keys['DOWN'] - keys['UP']
        
        if self.acc.length() > 1:
            # prevent faster diagnoal movement
            self.acc.scale_to_length(1)
        # laws of motion
        self.vel += self.acc * self.speed * dt
        self.vel *= self.friction
        
        speed = self.vel.length()
        if speed < 0.1:
            # stop and set idle image
            self.vel *= 0
            self.image_state = 'idle'
        else:
            self.image_state = 'walk'
            # check direction
            if self.acc.x > 0:
                self.lastdir = RIGHT
            elif self.acc.x < 0:
                self.lastdir = LEFT
            if self.acc.y > 0:
                self.lastdir = DOWN
            elif self.acc.y < 0:
                self.lastdir = UP
        self.images[self.image_state][self.lastdir]
        
        self.pos += self.vel
    

    def draw_reflection(self, screen, rect):
        reflection_image = pg.transform.flip(self.image, False, True)
        reflection_image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)
        reflection_rect = reflection_image.get_rect()
        reflection_rect.x = rect.x
        reflection_rect.y = rect.y + rect.h
        screen.blit(reflection_image, reflection_rect)
        


class Wall(BaseSprite):
    ''' Invisible Wall object for collisions
    '''
    def __init__(self, game, kwargs):
        super().__init__(game, game.walls, **kwargs)
        
        self.image = pg.Surface((self.width, self.height), pg.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.hitbox = self.rect.copy()
    
    
    def update(self, dt):
        pass
    
    
    def draw(self, screen, rect):
        if self.game.debug_mode:
            pg.draw.rect(screen, pg.Color('Red'), rect, 1)



# ------------------- Other sprites -------------------------------------------

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

        if self.game.keydown['A']:
            # scroll if the player hits the key assigned to A
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
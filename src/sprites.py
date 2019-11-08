import pygame as pg
#from random import randint

import settings as st
import utilities as utils


vec = pg.math.Vector2

RIGHT = 0
DOWN = 1
LEFT = 2
UP = 3


# TODO: make seperate parent classes for Sprite and animated sprite

class State():
    ''' base class for player/NPC state machine '''
    def __init__(self, game, sprite):
        self.game = game
        self.sprite = sprite # the sprite object this state belongs to
        self.next = None # what comes after if this is done
        self.done = False # if true, the next state gets executed
        self.previous = None # the state that was executed before
        self.name = self.sprite.state_name
        
        # get the image list for this state
        self.images = [image.copy() for image in self.sprite.image_dict[self.name]]
        
    def startup(self):
        self.sprite.image = self.images[0].copy()
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.center = self.sprite.pos
    
    def cleanup(self):
        print(f'cleaning up {self.name}')
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
    
    
    def draw(self, screen, pos_or_rect):
        screen.blit(self.image, pos_or_rect)
    
    

# =============================================================================
# class Animated_sprite(pg.sprite.Sprite):
#     ''' sprite class with a list of images that animate'''
#     def __init__(self, game, images, **kwargs):
#         self.game = game
#         super().__init__(game.all_sprites)
#         for key, value in kwargs.items():
#             setattr(self, key, value)
#         # set additional custom properties (from Tiled 'properties' dict)
#         if hasattr(self, 'properties'):
#             for key, value in self.properties.items():
#                 setattr(self, key, value)
#                 
#         try:
#             # try accessing to width and height
#             # if this fails, take the default tile size
#             self.size = (self.width, self.height)
#         except AttributeError:
#             self.width = st.TILE_WIDTH
#             self.height = st.TILE_HEIGHT
#             self.size = (self.width, self.height)
#         self.pos = (self.x, self.y)
#         
#         if images:
#             self.image_dict = images
# 
#     
#     def flip_state(self):
#         '''set the state to the next if the current state is done'''
#         self.state.done = False
#         # set the current and next state to the previous and current state
#         previous, self.state_name = self.state_name, self.state.next
#         self.state.cleanup()
#         self.state = self.state_dict[self.state_name](self)
#         self.state.startup()
#         self.state.previous = previous
#         
#     
#     def update(self, dt):
#         if self.state.done:
#             self.flip_state()
#         self.state.update(dt)
# 
#     
#     def draw(self, screen, pos_or_rect):
#         screen.blit(self.image, pos_or_rect)
#     
#     
#     def animate(self, dt):
#         # loop through all of self.images and set self.image to the next
#         # image if the time exceeds the delay
#         self.anim_timer += dt
#         if self.anim_timer >= self.anim_delay:
#             # reset the timer
#             self.anim_timer = 0
#             # advance the frame
#             self.anim_frame = (self.anim_frame + 1) % len(self.images)
#             # set the image and adjust the rect
#             self.image = self.images[self.anim_frame]
#             self.rect = self.image.get_rect()
#             self.rect.midbottom = self.hitbox.midbottom
# =============================================================================



class Player(BaseSprite):
    ''' The Sprite you control as the player
    '''
    def __init__(self, game, kwargs):
        super().__init__(game, game.all_sprites, **kwargs)
        
        images1 = game.graphics['knight_images']
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
        
# =============================================================================
#         # setup state machine
#         self.state_dict = {
#                 'Moving': self.Moving
#                 }
#         self.state_name = 'Moving'
#         self.state = self.state_dict[self.state_name](self)
#         self.state.startup()
# =============================================================================
    
    
# =============================================================================
#     class Moving(State):
#         ''' this is the default state for the player '''
#         def __init__(self, sprite):
#             super().__init__(sprite.game, sprite)
#             self.next = 'Test_state'
#             
#             self.sprite.lastdir = DOWN
#         
#         
#         def startup(self):
#             super().startup()
#             
#             self.sprite.anim_timer = 0 # time in seconds
#             self.sprite.anim_delay = 0.2 # animation delay in seconds
#             self.sprite.anim_frame = 0 # current index of the images list
#             
#         
#         def update(self, dt):
#             self.sprite.move(self, dt)
#             self.sprite.collide()
#             self.sprite.animate(dt)
# =============================================================================
        

    def update(self, dt):
        # TODO: change to state.update
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
        
        # collision detection
        # the center of the hitbox is always at the sprite's position
        self.hitbox.centerx = self.pos.x
        utils.collide_with_walls(self, self.game.walls, 'x')
        self.hitbox.centery = self.pos.y
        utils.collide_with_walls(self, self.game.walls, 'y')
        # the rect(where the image is drawn)'s bottom is aligned with the hitbox's bottom
        self.rect.midbottom = self.hitbox.midbottom
        
        self.animate(dt)
    

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

        

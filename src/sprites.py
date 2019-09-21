import pygame as pg
#from random import randint

import settings as st
import utilities as utils


vec = pg.math.Vector2

RIGHT = 2 #TODO: come up with a better system
DOWN = 8
LEFT = 6
UP = 9


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
        self.sprite.rect.topleft = self.sprite.pos # only works when images are of the same size
    
    def cleanup(self):
        print(f'cleaning up {self.name}')
        pass
    
    def update(self, dt):
        pass

    
    

class Animated_sprite(pg.sprite.Sprite):
    ''' sprite class with a list of images that animate'''
    def __init__(self, game, images, **kwargs):
        self.game = game
        super().__init__(game.all_sprites)
        for key, value in kwargs.items():
            setattr(self, key, value)
        # set additional custom properties (from Tiled 'properties' dict)
        if hasattr(self, 'properties'):
            for key, value in self.properties.items():
                setattr(self, key, value)
                
        try:
            # try accessing to width and height
            # if this fails, take the default tile size
            self.size = (self.width, self.height)
        except AttributeError:
            self.width = st.TILE_WIDTH
            self.height = st.TILE_HEIGHT
            self.size = (self.width, self.height)
        self.pos = (self.x, self.y)
        
        if images:
            self.image_dict = images

    
    def flip_state(self):
        '''set the state to the next if the current state is done'''
        self.state.done = False
        # set the current and next state to the previous and current state
        previous, self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        self.state = self.state_dict[self.state_name](self)
        self.state.startup()
        self.state.previous = previous
        
    
    def update(self, dt):
        if self.state.done:
            self.flip_state()
        self.state.update(dt)
        
    
    def draw(self, screen, pos_or_rect):
        screen.blit(self.image, pos_or_rect)
    
    
    def animate(self, dt):
        # loop through all of self.images and set self.image to the next
        # image if the time exceeds the delay
        self.anim_timer += dt
        if self.anim_timer >= self.anim_delay:
            # reset the timer
            self.anim_timer = 0
            # advance the frame
            self.anim_frame = (self.anim_frame + 1) % len(self.state.images)
            # set the image and adjust the rect
            self.image = self.state.images[self.anim_frame]
            self.rect = self.image.get_rect()
            self.rect.topleft = self.pos



class Player(Animated_sprite):
    ''' The Sprite you control as the player
    '''
    def __init__(self, game, **kwargs):
        images = {'Moving': game.graphics['knight_images']}
        
        super().__init__(game, images, **kwargs)
        
        # physics properties
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
    
    
    class Moving(State):
        ''' this is the default state for the player '''
        def __init__(self, sprite):
            super().__init__(sprite.game, sprite)
            self.next = 'Test_state'
            
            self.lastdir = DOWN
        
        
        def startup(self):
            super().startup()
            
            self.sprite.anim_timer = 0 # time in seconds
            self.sprite.anim_delay = 0.2 # animation delay in seconds
            self.sprite.anim_frame = 0 # current index of the images list
            
        
        def update(self, dt):
            self.sprite.animate(dt)
            
            keys = self.game.keys_pressed

            self.sprite.acc *= 0
            self.sprite.acc.x = keys['RIGHT'] - keys['LEFT']
            self.sprite.acc.y = keys['DOWN'] - keys['UP']
            if self.sprite.acc.length() > 1:
                self.sprite.acc.scale_to_length(1)
            self.sprite.vel += self.sprite.acc * self.sprite.speed * dt
            self.sprite.vel *= self.sprite.friction
            self.sprite.pos += self.sprite.vel * dt
            self.sprite.rect.topleft = self.sprite.pos
            
            if self.sprite.vel.length() < 10:
                self.sprite.vel *= 0
                images = self.sprite.image_dict[self.name]
                self.images = [images[self.lastdir]] # TODO: select the idle images
            else:
                images = self.sprite.image_dict[self.name]
                if self.sprite.acc.x > 0:
                    self.images = images[2:4]
                    self.lastdir = RIGHT
                elif self.sprite.acc.x < 0:
                    self.images = images[6:8]
                    self.lastdir = LEFT
                if self.sprite.acc.y > 0:
                    self.images = images[0:2]
                    self.lastdir = DOWN
                elif self.sprite.acc.y < 0:
                    self.images = images[4:6]
                    self.lastdir = UP
            
            self.sprite.collide()
        

    def update(self, dt):
        super().update(dt)
    
    
    def collide(self):
        # collision detection
        self.rect = self.image.get_rect()
        self.hitbox = pg.Rect((0, 0), st.PLAYER_HIT_RECT_SIZE)
        self.hitbox.center = self.rect.center
        
        self.hitbox.centerx = self.pos.x
        utils.collide_with_walls(self, self.game.walls, 'x')
        self.hitbox.centery = self.pos.y
        utils.collide_with_walls(self, self.game.walls, 'y')

        # position the rect at the bottom of the hitbox
        # leave 1 pixel space so that the game can detect collision
        # with solid objects
        self.rect.midbottom = self.hitbox.midbottom
        self.rect.bottom = self.hitbox.bottom + 1  
    

    def draw_reflection(self, screen, rect):
        reflection_image = pg.transform.flip(self.image, False, True)
        reflection_image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)
        reflection_rect = reflection_image.get_rect()
        reflection_rect.x = rect.x
        reflection_rect.y = rect.y + rect.h
        screen.blit(reflection_image, reflection_rect)
        


class Wall:
    ''' Invisible Wall object for collisions
    '''
    def __init__(self, game, **kwargs):
        self.game = game
        self.game.walls.append(self)
        # TODO make this a parent class for non-Sprite Tilemap objects
        for key, value in kwargs.items():
            setattr(self, key, value)
        # set additional custom properties (from Tiled 'properties' dict)
        if hasattr(self, 'properties'):
            for key, value in self.properties.items():
                setattr(self, key, value)
        
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)
        self.hitbox = self.rect.copy()
    
    
    def update(self, dt):
        pass
    
    
    def draw(self, screen, rect):
        pg.draw.rect(screen, pg.Color('Red'), rect, 1)
        

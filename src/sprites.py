import pygame as pg
from random import choice, randint
from itertools import cycle

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
        
        self.anim_delay = 0.2 # this is used for state-individual animation
        
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
        # TODO: probably put this also in State
        self.anim_frame = 0
        self.flicker_timer = 0.05
        self.flicker_delay = self.flicker_timer
        self.damage_alpha = cycle(st.DAMAGE_ALPHA)
        self.alpha = 255
        
        self.acc = vec()
        self.vel = vec()
        self.forces = [] # list of forces that are applied to the acc once
    
    
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
        if self.anim_timer >= self.state.anim_delay:
            # reset the timer
            self.anim_timer -= self.state.anim_delay
            # advance the frame
            self.anim_frame = (self.anim_frame + 1) % len(self.images[self.image_state][self.lastdir])
            # set the image and adjust the rect
            self.image = self.images[self.image_state][self.lastdir][self.anim_frame]
            self.rect = self.image.get_rect()
            self.rect.midbottom = self.hitbox.midbottom
    
    
    def animate_flicker(self, dt):
        self.anim_timer += dt
        self.flicker_timer += dt
        
        #print(self.alpha)
        
        if self.flicker_timer >= self.flicker_delay:
            self.flicker_timer -= self.flicker_delay
            self.alpha = next(self.damage_alpha)
        
        flicker_img = self.last_image.copy()
        flicker_img.fill((255, 255, 255, self.alpha), 
                    special_flags=pg.BLEND_RGBA_MULT)
        self.image = flicker_img

        if self.anim_timer >= self.state.anim_delay:
            # reset the timer
            self.anim_timer -= self.state.anim_delay
            # advance the frame
            self.anim_frame = (self.anim_frame + 1) % len(self.images[self.image_state][self.lastdir])
            # set the image and adjust the rect
            img = self.images[self.image_state][self.lastdir][self.anim_frame]
            self.image = img
            self.last_image = img.copy()
            self.rect = self.image.get_rect()
            self.rect.midbottom = self.hitbox.midbottom
    
    
    def apply_forces(self, dt):
        # apply additional forces to the velocity
        for f in self.forces:
            #f *= dt
            self.acc += f
        self.forces = []
    

    def add_force(self, vector):
        self.forces.append(vector)
    
    
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
        self.last_image = self.image.copy()
        
        self.rect = self.image.get_rect()
        self.hitbox = pg.Rect((0, 0), st.PLAYER_HITBOX_SIZE)
        
        self.pos = vec(self.x, self.y)
        self.hitbox.center = self.pos
        self.rect.midbottom = self.hitbox.midbottom
        
        # physics properties
        self.speed = 20
        self.friction = 0.8
        
        self.hitstun = 1 # seconds that hit stun lasts
        self.hitstun_timer = 0
        
        # stats
        self.hp = 3.0
        self.max_hp = st.PLAYER_HP_START
        self.mana = 10
        self.max_mana = 10
        
        self.item_counts = {
                'rupee': 0
                }
        
        self.items = {
                'A': None,
                'B': None
                }
        self.item_using = None
        
        # setup state machine
        self.state_dict = {
                'moving': self.Moving,
                'hit': self.Hit,
                'USE_A': self.UseItemA,
                'USE_B': self.UseItemB
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

            self.anim_delay = 0.2
            
        
        def update(self, dt):
            self.sprite.get_inputs()
            self.sprite.move(dt)
            self.sprite.collide_with_walls()
            self.sprite.animate(dt)
            
            if self.game.keydown['A']:
                self.next = 'USE_A'
                self.done = True
            if self.game.keydown['B']:
                self.next = 'USE_B'
                self.done = True
                
    
    class Hit(State):
        ''' when the player is damaged'''
        def __init__(self, sprite):
            super().__init__(sprite.game, sprite)
            self.next = 'moving'
        
        def startup(self):
            super().startup()
            print('hit')
            self.sprite.damage_alpha = cycle(st.DAMAGE_ALPHA)
            
        
        def update(self, dt):
            self.sprite.get_inputs()
            self.sprite.move(dt)
            self.sprite.collide_with_walls()
            
            self.sprite.animate_flicker(dt)
            
            self.sprite.hitstun_timer += dt
            if self.sprite.hitstun_timer > self.sprite.hitstun:
                self.sprite.hitstun_timer -= self.sprite.hitstun
                self.done = True

    
    class UseItem(State):
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
    
    
    class UseItemA(UseItem):
        def __init__(self, sprite):
            super().__init__(sprite)
            self.slot = 'A'

                
    class UseItemB(UseItem):
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
    
    
    def get_inputs(self):
        keys = self.game.keys_pressed
        
        self.acc.x = keys['RIGHT'] - keys['LEFT']
        self.acc.y = keys['DOWN'] - keys['UP']
        
        if self.acc.length() > 1:
            # prevent faster diagnoal movement
            self.acc.scale_to_length(1)
    
    
    def move(self, dt):
        self.apply_forces(dt)
        
        # laws of motion
        self.vel += self.acc * self.speed * dt
        self.vel *= self.friction
        
        speed = self.vel.length()
        if speed < 10 * dt:
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
        # reset acceleration
        self.acc *= 0
    

# =============================================================================
#     def draw_reflection(self, screen, rect):
#         reflection_image = pg.transform.flip(self.image, False, True)
#         reflection_image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)
#         reflection_rect = reflection_image.get_rect()
#         reflection_rect.x = rect.x
#         reflection_rect.y = rect.y + rect.h
#         screen.blit(reflection_image, reflection_rect)
# =============================================================================
        


class Wall(BaseSprite):
    ''' Invisible Wall object for collisions
    '''
    def __init__(self, game, kwargs):
        super().__init__(game, [game.all_sprites, game.walls], **kwargs)
        
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
            
class Enemy(BaseSprite):
    def __init__(self, game, kwargs):
        super().__init__(game, [game.all_sprites, game.enemies], **kwargs)
        
        # TODO: this is a mixup between a parent class and the skeleton
        images1 = game.graphics['enemy_skeleton'][:2]
        images2 = game.graphics['enemy_skeleton'][2:]
        self.images = {
            'hit': None, #TODO
            'idle': {
                    RIGHT: images1,
                    DOWN: images1,
                    LEFT: images1,
                    UP: images1
                    },
            'walk': {
                    RIGHT: images1,
                    DOWN: images1,
                    LEFT: images1,
                    UP: images1
                    },
            'attack': {
                    RIGHT: images1,
                    DOWN: images1,
                    LEFT: images1,
                    UP: images1,
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
        self.speed = 12
        self.friction = 0.8
        
        self.state_dict = {
                'idle': self.Idle,
                'wandering': self.Wandering,
                'chase': self.Chase
                }
        self.state_name = 'wandering'
        self.state = self.state_dict[self.state_name](self)
        self.state.startup()
        
        # TODO: put these in a dict for each enemy
        self.aggro_dist = 60 # when the enemy starts charging at the player
        self.idle_dist = 100 # when the enemy lets go off the player
        self.player_dist = 8 # the minimum distance to the player
        self.push_force = 20
        self.damage = 0.5
        
    
    def collide_with_walls(self):
        # collision detection
        # the center of the hitbox is always at the sprite's position
        self.hitbox.centerx = self.pos.x
        utils.collide_with_walls(self, self.game.walls, 'x')
        self.hitbox.centery = self.pos.y
        utils.collide_with_walls(self, self.game.walls, 'y')
        # the rect(where the image is drawn)'s bottom is aligned with the hitbox's bottom
        self.rect.midbottom = self.hitbox.midbottom
    
    
    def collide_with_player(self):
        player = self.game.player
        collision = self.hitbox.colliderect(player.hitbox)
        if collision and not player.state_name == 'hit':
            vec_to_player = player.pos - self.pos
            vec_to_player.scale_to_length(self.push_force)
            player.add_force(vec_to_player)
            player.hp -= self.damage
            player.state.next = 'hit'
            player.state.done = True
        
    
    def move(self, dt):
        if self.acc.length() > 1:
            # prevent faster diagnoal movement
            self.acc.scale_to_length(1)

        self.apply_forces(dt)
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
        self.acc *= 0
        
    
    
    class Idle(State):
        def __init__(self, sprite):
            super().__init__(sprite.game, sprite)
            self.next = 'chase'
            
            self.anim_delay = 0.3
            
        
        def update(self, dt):
            vec_to_player = self.game.player.pos - self.sprite.pos
            dist = vec_to_player.length()
            if self.sprite.player_dist < dist <= self.sprite.aggro_dist:
                self.done = True
            
            self.sprite.move(dt)
            self.sprite.collide_with_walls()
            self.sprite.collide_with_player()
            self.sprite.animate(dt)


    class Wandering(State):
        def __init__(self, sprite):
            super().__init__(sprite.game, sprite)
            self.next = 'chase'

            self.anim_delay = 0.3
            self.move_dir = vec()
            self.walk_timer = 0
            self.walk_delay = 3
            
            self.target = self.sprite.pos


        def update(self, dt):
            vec_to_player = self.game.player.pos - self.sprite.pos
            dist = vec_to_player.length()
            if self.sprite.player_dist < dist <= self.sprite.aggro_dist:
                self.done = True
            else:
                self.walk_timer += dt
                if self.walk_timer >= self.walk_delay:
                    self.walk_timer -= self.walk_delay
                    # TODO: This looks awful
                    # use target vector for wandering
                    self.move_dir = choice([
                        vec(st.TILE_WIDTH, 0),
                        vec(-st.TILE_WIDTH, 0),
                        vec(0, st.TILE_HEIGHT),
                        vec(0, -st.TILE_HEIGHT)])
                    self.move_dir *= randint(1, 3)
                    self.target = self.sprite.pos + self.move_dir
                vec_to_target = self.target - self.sprite.pos
                if vec_to_target.length() > 1:
                    self.anim_delay = 0.2
                    self.sprite.acc = vec_to_target.normalize()
                else:
                    self.anim_delay = 0.5
                    self.sprite.acc = vec()

            self.sprite.move(dt)
            self.sprite.collide_with_walls()
            self.sprite.collide_with_player()
            self.sprite.animate(dt)
            
            
    class Chase(State):
        def __init__(self, sprite):
            super().__init__(sprite.game, sprite)
            self.next = 'wandering'
            
            self.anim_delay = 0.15
    
    
        def update(self, dt):
            vec_to_player = self.game.player.pos - self.sprite.pos
            self.sprite.acc = vec_to_player.normalize() # TODO: lerp this

            self.sprite.move(dt)
            self.sprite.collide_with_walls()
            self.sprite.collide_with_player()
            self.sprite.animate(dt)
            
            dist = vec_to_player.length()
            if dist > self.sprite.idle_dist or dist < self.sprite.player_dist:
                self.done = True
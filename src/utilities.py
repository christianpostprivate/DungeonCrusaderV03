import pygame as pg
import json

import settings as st



vec = pg.math.Vector2


def clamp(var, lower, upper):
    # restrains a variable's value between two values
    return max(lower, min(var, upper))


def collide_hit_rect(one, two):
    return one.hitbox.colliderect(two.hitbox)


def collide_with_walls(sprite, group, dir_):
    if dir_ == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # hit from left
            if hits[0].hitbox.centerx > sprite.hitbox.centerx:
                sprite.pos.x = hits[0].hitbox.left - sprite.hitbox.w
            # hit from right
            elif hits[0].hitbox.centerx < sprite.hitbox.centerx:
                sprite.pos.x = hits[0].hitbox.right
                            
            sprite.vel.x = 0
            sprite.hitbox.left = sprite.pos.x
            return True
            
    elif dir_ == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # hit from top
            if hits[0].hitbox.centery > sprite.hitbox.centery:
                sprite.pos.y = hits[0].hitbox.top - sprite.hitbox.h
            # hit from bottom
            elif hits[0].hitbox.centery < sprite.hitbox.centery:
                sprite.pos.y = hits[0].hitbox.bottom
                
            sprite.vel.y = 0
            sprite.hitbox.top = sprite.pos.y
            return True
    return False


def difference(list1, list2):
    return [1 if elem and not list1[i] else 0 for i, elem in enumerate(list2)]


def draw_text(surface, text, file, size, color, pos, align='topleft'):
    '''
    draws the text string at a given position with the given text file
    (might be too performance intensive?)
    '''
    font = pg.font.Font(file, size)
    font.set_bold(False)
    text_surface = font.render(text, False, color)
    text_rect = text_surface.get_rect()
    setattr(text_rect, align, pos)
    surface.blit(text_surface, text_rect)
    

def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except:
        return False



class Camera():
    '''
    modified from http://kidscancode.org/lessons/
    modes are
        FOLLOW: player is always in the middle of the screen
        CUT: camera pans as soon as the player leaves the screen
        SLIDE: like pan, but with a sliding animation
    '''
    def __init__(self, game, map_width, map_height, mode='FOLLOW'):
        self.game = game
        self.rect = pg.Rect(0, 0, map_width, map_height)
        self.map_width = map_width
        self.map_height = map_height
        self.mode = mode

        self.is_sliding = False
        self.target_pos = vec()
        self.prev_pos = vec()
        # previous quadrant
        self.prev_qw = 0
        self.prev_qh = 0
        
        self.slide_speed = 0.05 # percent, change this to dt
        self.slide_amount = 0


    def apply(self, entity):
        return entity.rect.move(self.rect.x, self.rect.y + st.GUI_HEIGHT)


    def apply_rect(self, rect):
        return rect.move(self.rect.x, self.rect.y + st.GUI_HEIGHT)
    
    
    def apply_bg(self, rect):
        return rect.move(self.rect.x, self.rect.y)
    

    def apply_point(self, point):
        return point - vec(self.rect.x, self.rect.y + st.GUI_HEIGHT)


    def update(self, target):
        if self.mode == 'FOLLOW':
            x = -target.rect.x + self.game.world_screen_rect.w // 2
            y = -target.rect.y + self.game.world_screen_rect.h // 2 + st.GUI_HEIGHT
        elif self.mode == 'CUT':
            # divide into quadrants
            quads_w = self.rect.w // self.game.world_screen_rect.w
            quads_h = self.rect.h // self.game.world_screen_rect.h
            # which quadrant the target is in.
            qw = target.rect.x // (self.rect.w // quads_w)
            # subtract GUI height to adapt target position to world_screen
            qh = (target.rect.y - st.GUI_HEIGHT) // (self.rect.h // quads_h)
            
            x = (self.game.world_screen_rect.w) * qw * -1
            y = (self.game.world_screen_rect.h) * qh * -1
            
        elif self.mode == 'SLIDE':
            # divide into quadrants
            quads_w = self.rect.w // self.game.world_screen_rect.w
            quads_h = self.rect.h // self.game.world_screen_rect.h
            # which quadrant the target is in 
            qw = target.rect.x // (self.rect.w // quads_w)
            qh = target.rect.y // (self.rect.h // quads_h)
            
            # limit the quadrants to the map
            qw = min(max(qw, 0), quads_w - 1)
            qh = min(max(qh, 0), quads_h - 1)
            
            self.target_pos.x = (self.game.world_screen_rect.w) * qw * -1
            self.target_pos.y = (self.game.world_screen_rect.h) * qh * -1

            if qw != self.prev_qw or qh != self.prev_qh:
                self.is_sliding = True
                
                self.slide_amount += self.slide_speed
                self.slide_amount = min(self.slide_amount, 1)
                between = self.prev_pos.lerp(self.target_pos, self.slide_amount)
                
                x = int(between.x)
                y = int(between.y)
                
                if self.target_pos.x == x and self.target_pos.y == y:
                    self.prev_qw = qw
                    self.prev_qh = qh
                    self.slide_amount = 0
                
            else:
                self.is_sliding = False
                
                x = self.target_pos.x
                y = self.target_pos.y
                
                self.prev_pos.x = self.target_pos.x
                self.prev_pos.y = self.target_pos.y

                self.prev_qw = qw
                self.prev_qh = qh

        # limit scrolling to map size
        x = min(0, x) # left
        x = max(-(self.map_width - self.game.world_screen_rect.w), x) # right
        y = min(0, y) # top
        y = max(-(self.map_height - self.game.world_screen_rect.h), y) # bottom
        
        self.rect = pg.Rect(x, y, self.map_width, self.map_height)
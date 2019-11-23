import pygame as pg

from constants import (RIGHT, DOWN, LEFT, UP)

vec = pg.Vector2


# ------------ Usable Items ---------------------------------------------------

class Sword(pg.sprite.Sprite):
    # TODO: base item class as parent
    # TODO: change this so it doesn't require a class variable
    inventory_image_index = 0
    name = "Sword"
    def __init__(self, player, game):
        super().__init__(game.all_sprites)

        self.game = game
        self.player = player
        
        img = game.graphics['sword_anim']
        self.animations = {
                UP: img[:4],
                DOWN: img[4:8],
                RIGHT: img[8:12],
                LEFT: img[12:]
                }
        
        self.anim_timer = 0
        self.anim_frame = 0
        self.anim_delay = 0.1
        
        #self.cooldown = 15
        #self.fired = False
        self.done = False
        self.damage = 1
        
        self.dir = self.player.lastdir
        if self.dir == UP:
            self.pos = self.player.pos + vec(-6, -22)
        elif self.dir == DOWN:
            self.pos = self.player.pos + vec(-9, 1)
        elif self.dir == RIGHT:
            self.pos = self.player.pos + vec(4, -14)
        elif self.dir == LEFT:
            self.pos = self.player.pos + vec(-20, -14)
            
        # play slash sound
        self.game.asset_loader.play_sound('sword_slash')
        #self.fired = True
        
        self.animate(0) # TODO: lazy hack, refactor!


    def update(self, dt):
        # delete sprite if animation is over
        self.animate(dt)
        if self.anim_frame == len(self.animations[self.dir]) - 1:
            self.done = True
            self.kill()

    # TODO: use the hitbox
# =============================================================================
#         for enemy in pg.sprite.spritecollide(self, self.game.enemies, False):
#             if enemy.state != 'HITSTUN':
#                 enemy.hp -= self.damage
#                 enemy.knockback(self.player, 1, 0.1)
# =============================================================================
    
    def draw(self, screen, pos_or_rect):
        screen.blit(self.image, pos_or_rect)
        
    
    def animate(self, dt):
        anim = self.animations[self.dir]
        self.image = anim[self.anim_frame]
        
        self.anim_timer += dt
        if self.anim_timer >= self.anim_delay:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % len(anim)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.hitbox = self.rect
        self.hitbox.center = self.rect.center
    
    
    def use(self, dt):
        # overwrites super().use() for the animation
        # maybe refactor this later and put back into parent
        
        self.pos = vec(0, 0)
        self.dir = self.player.lastdir
        if self.dir == UP:
            self.pos = self.player.pos + vec(-6, -22)
        elif self.dir == DOWN:
            self.pos = self.player.pos + vec(-9, 1)
        elif self.dir == RIGHT:
            self.pos = self.player.pos + vec(4, -14)
        elif self.dir == LEFT:
            self.pos = self.player.pos + vec(-20, -14)
        
        if not self.fired:
            # play slash sound
            self.game.asset_loader.play_sound('test_sound')
            self.fired = True
            
    
    def reset(self):
        self.fired = False
        self.anim_frame = 0
        
    
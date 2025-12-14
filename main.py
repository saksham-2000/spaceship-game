import pygame
import os
import random
import time

from settings import *


# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # returns pygame.Surface
clock = pygame.time.Clock()
pygame.display.set_caption('Space Shooter')
runningLives = 5
gameScore = 0

# creating sprite groups
all_sprites_group = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()


# importing surfaces/fonts/frames
star_surf = pygame.image.load(os.path.join('images', 'star.png')).convert_alpha()
laser_surf = pygame.image.load(os.path.join('images', 'laser.png')).convert_alpha()
meteor_surf = pygame.image.load(os.path.join('images', 'meteor.png')).convert_alpha()
score_font = pygame.font.Font(os.path.join('images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(os.path.join('images', 'explosion',f'{i}.png')).convert_alpha() for i in range(20)]


# game sounds
laser_sound = pygame.mixer.Sound(os.path.join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(os.path.join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.6)
spaceship_damage_sound = pygame.mixer.Sound(os.path.join('audio', 'damage.ogg'))
game_sound = pygame.mixer.Sound(os.path.join('audio', 'game_music.wav'))
game_sound.set_volume(0.4)
game_sound.play(loops = -1)

METEOR_EVENT = pygame.USEREVENT + 1
# Set the timer to trigger every 2000 milliseconds (2 seconds)
pygame.time.set_timer(METEOR_EVENT, 500)

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, filename, starting_position = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)):
        super().__init__(groups)
        self.image = pygame.image.load(os.path.join('images',filename)).convert_alpha()
        self.rect = self.image.get_frect(center = starting_position)
        self.direction = pygame.math.Vector2()
        self.speed = 500

        # firing attributes
        self.can_shoot = True
        self.last_laser_shoot = 0
        self.cooldown = 200  # milliseconds

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])  
        self.direction = self.direction.normalize() if self.direction else self.direction 
        self.rect.center += self.direction * self.speed * dt

        current_time = pygame.time.get_ticks()
       # print(current_time)
        if not self.can_shoot and self.last_laser_shoot + self.cooldown <= current_time:
            self.can_shoot = True

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser((all_sprites_group, laser_sprites),laser_surf,pos = self.rect.midtop)
            laser_sound.play()
            self.last_laser_shoot = current_time
            self.can_shoot = False



class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (random.randint(0, SCREEN_WIDTH),random.randint(0,SCREEN_HEIGHT)))


class Laser(pygame.sprite.Sprite):
     def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.speed = 500

     def update(self,dt):
        self.rect.centery -= self.speed * dt
        if self.rect.centery < 0:
            self.kill() # ungroup


class Meteor(pygame.sprite.Sprite):
     def __init__(self, groups, surf):
        super().__init__(groups)
        self.orig_image = surf
        self.image = self.orig_image
        self.rect = self.image.get_frect(center = (random.randint(0,SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT/10)))
        self.direction = pygame.Vector2(random.uniform(-0.5, 0.5),1)
        self.speed = 250
        self.rotation = 0
        self.rotationDirection = 2 * random.randint(0, 1) - 1
 
     def update(self,dt):
        self.rect.center += self.speed * self.direction * dt
        self.rotation += dt * 10 * self.rotationDirection
        self.image = pygame.transform.rotate(self.orig_image, self.rotation)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill() # ungroup
        
class LifeLine(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.font = pygame.font.Font(None, 40) 
        global runningLives
        self.image = self.font.render(f"Lives: {runningLives}", True, "white")
        self.rect = self.image.get_frect(center = (60,30))

    def update(self, dt):
        self.image = self.font.render(f"Lives: {runningLives}", True, "white" if runningLives > 2 else "red")


class MeteorExplosion(pygame.sprite.Sprite):
    def __init__(self, frames,groups, pos):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect =  self.image.get_frect(center = pos)

    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else :
            self.kill()




def display_score():
    score_surf = score_font.render(f"{gameScore}", True, (240,240,240))
    score_rect = score_surf.get_frect(center= (SCREEN_WIDTH/2,SCREEN_HEIGHT - 50))
    screen.blit(score_surf, score_rect)
    pygame.draw.rect(screen, (240,240,240), score_rect.inflate(20,10).move(0,-8), 5, 10)


def handle_collisions():
    global runningLives

    player_collision = pygame.sprite.spritecollide(spaceship, meteor_sprites, True, pygame.sprite.collide_mask)
    if player_collision:
        runningLives -= 1
        # spaceship_damage_sound.play()
    
    for laser in laser_sprites:
        laser_collisions = pygame.sprite.spritecollide(laser, meteor_sprites, dokill = True)
        if len(laser_collisions):
            laser.kill()
            # add explosion instance
            MeteorExplosion(explosion_frames, all_sprites_group, pos = laser.rect.midtop)
            global gameScore
            gameScore += 10
            explosion_sound.play()


for _ in range(20):
    Star(all_sprites_group, star_surf)

spaceship = Player(all_sprites_group, filename='player.png', starting_position=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - MARGIN))

lifeline = LifeLine(all_sprites_group)


while runningLives > 0:

    dt = clock.tick(FPS)/1000  # set frame rate

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runningLives = False
        elif event.type == METEOR_EVENT:
            Meteor((all_sprites_group, meteor_sprites), meteor_surf)

    handle_collisions()


    all_sprites_group.update(dt)
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("darkslateblue")

    
    #screen.blit(meteor,meteor_rect)

    display_score()

    all_sprites_group.draw(screen)

    # flip() the display to put your work on screen
    pygame.display.flip()


pygame.quit()

import pygame
import os
import random
import time

SCREEN_WIDTH, SCREEN_HEIGHT = 1280,720
MARGIN = 20
FPS = 60

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, filename, starting_position = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)):
        super().__init__(groups)
        self.image = pygame.image.load(os.path.join('images',filename)).convert_alpha()
        self.rect = self.image.get_frect(center = starting_position)
        self.direction = pygame.math.Vector2()
        self.speed = 200

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])  
        self.direction = self.direction.normalize() if self.direction else self.direction 
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE]:
            print('fire laser')


class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (random.randint(0, SCREEN_WIDTH),random.randint(0,SCREEN_HEIGHT)))

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # returns pygame.Surface
clock = pygame.time.Clock()
pygame.display.set_caption('Space Shooter')
running = True


# creating a group
all_sprites_group = pygame.sprite.Group()

# star surface
star_surf = pygame.image.load(os.path.join('images', 'star.png')).convert_alpha()
for i in range(20):
    Star(all_sprites_group, star_surf)


spaceship = Player(all_sprites_group, filename='player.png', starting_position=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - MARGIN))


# meteor surface
meteor = pygame.image.load(os.path.join('images','meteor.png')).convert_alpha() # loading a surface
meteor_rect = meteor.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

while running:

    dt = clock.tick(FPS)/1000  # set frame rate

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites_group.update(dt)
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("darkgray")
    
    screen.blit(meteor,meteor_rect)

    all_sprites_group.draw(screen)

    # flip() the display to put your work on screen
    pygame.display.flip()


pygame.quit()

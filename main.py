import random
import pygame
from pygame import mixer
import os
import csv
import button

# initializing
mixer.init()  # to load music
pygame.init()

# set Screen size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.9)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# set window icon and title
pygame.display.set_caption('Soldier of Fortune')
gameIcon = pygame.image.load('assets/img/icons/game_icon.png')
pygame.display.set_icon(gameIcon)

# setting frame rate
clock = pygame.time.Clock()
FPS = 60  # Frame per second

# define game vars
GRAVITY = 0.75
SCROLL_THRESHOLD = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES_NUMBER = 30
MAX_LEVELS = 3
MISSIONS = {1: 'Welcome To GnomeLand', 2: "      Into The Woods", 3: "    Meet The Devora"}
ENEMY_NAMES = ['enemy', 'green_enemy']
screen_scroll = 0
bg_scroll = 0
level = 1
running = True
start_game = False
start_intro = False
total_time = 0
# Player actions

moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# load music and sounds
pygame.mixer.music.load(f'assets/audio/level1.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0, 500)
# sound effects
jump_fx = pygame.mixer.Sound('assets/audio/jump.wav')
pygame.mixer.music.set_volume(0.5)
shot_fx = pygame.mixer.Sound('assets/audio/shot.wav')
pygame.mixer.music.set_volume(0.5)
grenade_fx = pygame.mixer.Sound('assets/audio/grenade.wav')
pygame.mixer.music.set_volume(2)
# load images

# Buttons
start_img = pygame.image.load(f'assets/img/buttons/start_btn.png').convert_alpha()
restart_img = pygame.image.load(f'assets/img/buttons/restart_btn.png').convert_alpha()
exit_img = pygame.image.load(f'assets/img/buttons/exit_btn.png').convert_alpha()
intro_bg = pygame.image.load(f"assets/img/buttons/intro.png").convert_alpha()
intro_bg = pygame.transform.scale(intro_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# backgrounds
trees1_img = pygame.image.load(f'assets/img/background/level{level}/trees1.png').convert_alpha()
trees2_img = pygame.image.load(f'assets/img/background/level{level}/trees2.png').convert_alpha()
mountains_img = pygame.image.load(f'assets/img/background/level{level}/mountains.png').convert_alpha()
sky_img = pygame.image.load(f'assets/img/background/level{level}/sky.png').convert_alpha()

# store tiles in a list
tile_img_list = []
for x in range(TILE_TYPES_NUMBER):
    img = pygame.image.load(f'assets/img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    tile_img_list.append(img)

# Bullets
bullet_img = pygame.image.load(f'assets/img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load(f'assets/img/icons/grenade.png').convert_alpha()

# item boxes
health_box_img = pygame.image.load(f'assets/img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load(f'assets/img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load(f'assets/img/icons/grenade_box.png').convert_alpha()
item_box = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# define colors
BG = (169, 169, 169)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (255, 20, 147)
DARK_PURPLE = (75, 74, 104)
DARK_GREEN = (38, 110, 115)

# define font
font = pygame.font.SysFont('comicsansms', 20)


def draw_text(text, font, text_color, x, y, ):
    # to display some texts (i.e. enemies health and etc.)
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


def draw_lvl_info_text(text, font, text_color, x, y):
    # this function is responsible for displaying level title and etc
    img = font.render(text, True, text_color)
    if total_time < 200:
        screen.blit(img, (x, y))


def draw_bg():
    # to display window background
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, (x * width - bg_scroll * 0.5, 0))
        screen.blit(mountains_img, (x * width - bg_scroll * 0.6, SCREEN_HEIGHT - mountains_img.get_height() - 300))
        screen.blit(trees1_img, (x * width - bg_scroll * 0.7, SCREEN_HEIGHT - trees1_img.get_height() - 150))
        screen.blit(trees2_img, (x * width - bg_scroll * 0.8, SCREEN_HEIGHT - trees2_img.get_height()))


def reset_level():
    global trees1_img,trees2_img,mountains_img,sky_img
    if level_complete:
        # backgrounds
        trees1_img = pygame.image.load(f'assets/img/background/level{level}/trees1.png').convert_alpha()
        trees2_img = pygame.image.load(f'assets/img/background/level{level}/trees2.png').convert_alpha()
        mountains_img = pygame.image.load(f'assets/img/background/level{level}/mountains.png').convert_alpha()
        sky_img = pygame.image.load(f'assets/img/background/level{level}/sky.png').convert_alpha()
    # to reset everything if player died or completed the level
    item_box_group.empty()
    grenade_group.empty()
    bullet_group.empty()
    explosion_group.empty()
    enemy_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    damage_text_group.empty()
    live_entity_group.empty()
    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data


class DamageText(pygame.sprite.Sprite):
    # this class is responsible for displaying damage texts
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.x += screen_scroll
        self.rect.y -= 1
        # delete after a few seconds
        self.counter += 1
        if self.counter > 100:
            self.kill()


class Soldier(pygame.sprite.Sprite):
    def __init__(self, soldier_type, x, y, scale, speed, ammo, grenades, health):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.soldier_type = soldier_type
        self.speed = speed
        self.ammo = ammo
        self.grenades = grenades
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = health
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0  # y velocity
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0

        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # Only player vars
        self.looking_up = False
        self.looking_up_right = False

        # Only AI vars
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)

        # Loading all images for animations
        animation_types = ['Idle', 'Run', 'Death', 'Jump', 'Shoot_up', 'Shoot_up_right']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in folder
            frame_numbers = len(os.listdir(f'assets/img/persons/{soldier_type}/{animation}'))
            for i in range(frame_numbers):
                img = pygame.image.load(f'assets/img/persons/{soldier_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_being_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):

        # reset movement vars
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -15
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # if ai has hit the wall then make it turn around
                if self.soldier_type in ENEMY_NAMES:
                    self.direction *= -1
                    self.move_counter = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check being drown into the water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check collision with exit level
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # check if player going off the screen
        if self.soldier_type == "binder":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update screen scroll according to player position
        if self.soldier_type == "binder":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESHOLD and bg_scroll < (
                    world.level_length * TILE_SIZE) - SCREEN_WIDTH) \
                    or (self.rect.left < SCROLL_THRESHOLD and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shooting(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20

            # shoot up
            if self.looking_up:
                bullet = Bullet(self.rect.centerx, self.rect.centery - 30,
                                0)

            # shoot up corner
            elif self.looking_up_right:
                bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery - 30,
                                self.direction * 2)

            # shoot normal
            else:
                bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery,
                                self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            shot_fx.play()

    def control_ai(self):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 150) == 1:
                self.update_action(0)  # AI idle
                self.idling = True
                self.idling_counter = 50
            # check if the ai is near the player
            if self.vision.colliderect(player.rect):
                # stop running and fight player
                self.update_action(0)
                self.shooting()
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # AI run
                    self.move_counter += 1
                    # update AI Vision
                    self.vision.center = (self.rect.centerx + 200 * self.direction, self.rect.centery)
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        self.rect.x += screen_scroll

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        # update imaged based on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if animation list ended, back to start of the list
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 2:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_being_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(2)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class LiveEntity(pygame.sprite.Sprite):
    # this class is responsible for the animated entities such as Dogs , crows , chests
    def __init__(self, entity_type, x, y, scale):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.entity_type = entity_type
        self.frame_index = 0
        self.health = 10
        self.alive = True
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.animation_list = []
        # Loading all images for animations
        animation_types = ['Idle', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in folder
            frame_numbers = len(os.listdir(f'assets/img/live_entity/{entity_type}/{animation}'))
            for i in range(frame_numbers):
                img = pygame.image.load(f'assets/img/live_entity/{entity_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def update(self):
        self.update_animation()
        self.check_being_alive()
        self.rect.x += screen_scroll

        if self.rect.colliderect(player):
            if self.alive:
                self.health -= 25
                # collide = pygame.sprite.spritecollide(self, live_entity_group, False)
                # collide[0].health -= 25
                damage_text = DamageText(self.rect.centerx,
                                         self.rect.centery, str(" speed has been increased "), WHITE)
                damage_text_group.add(damage_text)
                if player.alive:
                    player.speed += 2

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        # update imaged based on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if animation list ended, back to start of the list
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 1:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def check_being_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(1)  # Entity Death animation

    def draw(self):
        screen.blit(self.image, self.rect)


class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        # How long is the level
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = tile_img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif (tile >= 11 and tile <= 14) or (tile >= 22 and tile <= 26):
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:  # create player
                        player = Soldier('binder', x * TILE_SIZE, y * TILE_SIZE, 2.2, 5, 20, 5, 100)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:  # create red enemies
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0, 75)
                        enemy_group.add(enemy)
                    elif tile == 21:
                        enemy = Soldier('green_enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0, 50)
                        enemy_group.add(enemy)
                    elif tile == 17:  # create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:  # create grenade box
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:  # create health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:  # create exit
                        exit = ExitDoor(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
                    elif tile == 27:  # create bird
                        bird = LiveEntity('crow', x * TILE_SIZE + 20, y * TILE_SIZE + 13, 2)
                        live_entity_group.add(bird)
                    elif tile == 28:  # create dog
                        dog = LiveEntity('dog', x * TILE_SIZE + 30, y * TILE_SIZE + 7, 1.5)
                        live_entity_group.add(dog)
                    elif tile == 29:  # create chest
                        chest = LiveEntity('chest', x * TILE_SIZE + 30, y * TILE_SIZE + 12, 2)
                        live_entity_group.add(chest)
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ExitDoor(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_box[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):

        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            # check the box type
            if self.item_type == 'Health':
                player.health += 25
                damage_text = DamageText(self.rect.centerx,
                                         self.rect.centery, f"Health +25", WHITE)
                damage_text_group.add(damage_text)
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
                damage_text = DamageText(self.rect.centerx,
                                         self.rect.centery, f"Ammo +15", WHITE)
                damage_text_group.add(damage_text)
            elif self.item_type == 'Grenade':
                player.grenades += 3
                damage_text = DamageText(self.rect.centerx,
                                         self.rect.centery, f"Grenade +3", WHITE)
                damage_text_group.add(damage_text)
            # remove the box
            self.kill()

        # Scroll Screen
        self.rect.x += screen_scroll


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update health with new health
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move the bullet

        # bullet moves up
        if self.direction == 0:
            self.rect.y -= self.speed + screen_scroll
        # bullet goes up right
        elif self.direction == 2:
            self.rect.y -= self.speed + screen_scroll
            self.rect.x += self.speed + screen_scroll
        # bullet goes up left
        elif self.direction == -2:
            self.rect.y -= self.speed + screen_scroll
            self.rect.x -= self.speed + screen_scroll
        # bullet moves normal
        else:
            self.rect.x += (self.direction * self.speed) + screen_scroll

        # check if bullet is out of the screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()  # del bullet
            # check collision with characters

        # check collision with environment
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    if enemy.health >= 0:
                        damage_text = DamageText(enemy.rect.centerx,
                                                 enemy.rect.centery, str(enemy.health), WHITE)
                        damage_text_group.add(damage_text)
                    self.kill()
        for live_entity in live_entity_group:
            if live_entity.entity_type != "chest":
                if pygame.sprite.spritecollide(live_entity, bullet_group, False):
                    if live_entity.alive:
                        live_entity.health = -25

                        damage_text = DamageText(live_entity.rect.centerx,
                                                 live_entity.rect.centery, str("you will be cursed"), PINK)
                        damage_text_group.add(damage_text)
                        if player.alive:
                            player.health -= 50
                        self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # check for collision with level
        for tile in world.obstacle_list:

            # check collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # check if below the ground, i.e. thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        # update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy + screen_scroll

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            # do damage to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50
                    if enemy.health >= 0:
                        damage_text = DamageText(enemy.rect.centerx,
                                                 enemy.rect.centery, str(enemy.health), WHITE)
                        damage_text_group.add(damage_text)
            for live_entity in live_entity_group:
                if live_entity.entity_type != "chest":
                    if abs(self.rect.centerx - live_entity.rect.centerx) < TILE_SIZE * 2 and \
                            abs(self.rect.centery - live_entity.rect.centery) < TILE_SIZE * 2:
                        if live_entity.alive:
                            live_entity.health = -25
                            damage_text = DamageText(live_entity.rect.centerx,
                                                     live_entity.rect.centery, str("you will be cursed"), PINK)
                            damage_text_group.add(damage_text)
                            if player.alive:
                                player.health -= 50
                            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.explosion_images = []
        for num in range(1, 6):
            img = pygame.image.load(f'assets/img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.explosion_images.append(img)
        self.frame_index = 0
        self.image = self.explosion_images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0  # to control the animation

    def update(self):

        EXPLOSION_SPEED = 4
        # update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if the animation has been completed then delete explosion
            if self.frame_index >= len(self.explosion_images):

                self.kill()
            else:
                self.image = self.explosion_images[self.frame_index]
        # scroll
        self.rect.x += screen_scroll


class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour,
                             (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour,
                             (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:  # vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete


# create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 10)

# create buttons
start_btn = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_btn = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 - 10, exit_img, 1)
restart_btn = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)
# create sprite groups
damage_text_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
live_entity_group = pygame.sprite.Group()

# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    file_reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(file_reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, player_health_bar = world.process_data(world_data)

while running:

    # drawing
    clock.tick(FPS)

    # Main Menu
    if start_game == False:
        # draw menu
        # screen.fill((0,0,0))

        screen.blit(intro_bg, (0, 0))
        # add buttons
        if start_btn.draw(screen):
            start_game = True
            start_intro = True
        if exit_btn.draw(screen):
            running = False


    else:
        # calc time
        total_time += 1
        # update bg
        draw_bg()
        # draw world map
        world.draw()
        # display player health
        player_health_bar.draw(player.health)
        # display player ammo and grenades
        draw_text(f'Ammo: {player.ammo}', font, WHITE, 10, 35)
        draw_text(f'Grenade: {player.grenades}', font, WHITE, 10, 60)
        draw_lvl_info_text(f'Mission {level}', font, WHITE, SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2)
        draw_lvl_info_text(f'{MISSIONS[level]}', font, WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30)
        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.draw()
            enemy.update()
            enemy.control_ai()

        # update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        damage_text_group.update()
        live_entity_group.update()
        # draw damage text
        live_entity_group.draw(screen)
        damage_text_group.draw(screen)
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        screen_scroll, level_complete = player.move(moving_left, moving_right)
        bg_scroll -= screen_scroll
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        # show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        if player.alive:
            # shooting bullets
            if shoot:
                player.shooting()
            # throw grenade
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (player.rect.size[0] * player.direction),
                                  player.rect.top, player.direction)
                grenade_group.add(grenade)
                # reduce grenades
                player.grenades -= 1
                grenade_thrown = True

            # update player action
            if player.in_air:
                player.update_action(3)  # 3: jump
            elif player.looking_up:
                player.update_action(4)  # 4: look up
            elif player.looking_up_right:
                player.update_action(5)  # 4: look up right
            elif moving_left or moving_right:
                player.update_action(1)
            else:
                player.update_action(0)
            # check if player has completed the level
            if level_complete:
                start_intro = True
                level += 1
                if level > MAX_LEVELS :
                    level = 1
                bg_scroll = 0
                total_time = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
                else:
                    level = 1

        else:
            screen_scroll = 0
            fade_complete = death_fade.fade()
            if fade_complete:
                if restart_btn.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    total_time = 0
                    world_data = reset_level()
                    # load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

    for event in pygame.event.get():
        # quit the game
        if event.type == pygame.QUIT:
            running = False

        if start_game:
            # Mouse left  click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                shoot = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                shoot = False
            # Mouse right click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                grenade = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                grenade = False
                grenade_thrown = False
        # Keyboard keys pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                player.looking_up = True
            if event.key == pygame.K_g:
                grenade = True
            if event.key == pygame.K_e:
                player.looking_up_right = True
                player.direction = 1
                player.flip = False
            if event.key == pygame.K_q:
                player.looking_up_right = True
                player.flip = True
                player.direction = -1
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                running = False

        # Keyboard keys released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                player.looking_up = False
            if event.key == pygame.K_e:
                player.looking_up_right = False
            if event.key == pygame.K_q:
                player.looking_up_right = False

            if event.key == pygame.K_g:
                grenade = False
                grenade_thrown = False
    # update display
    pygame.display.update()

pygame.quit()

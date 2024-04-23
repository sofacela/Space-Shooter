import pygame
import os
import random
pygame.font.init()

WIDTH, HEIGHT = 800, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Load images
# Enemies spaceships
BIRD_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "enemy_ship1.png")), (70, 70))
UFO_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "enemy_ship2.png")), (80, 60))
RED_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "enemy_ship3.png")), (70, 70))

# Player spaceship
PLAYER_SPACE_SHIP = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("assets", "player_ship.png")), (122, 122)), 90)

# Bullets
ENEMY_LASER = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("assets", "enemy_laser.png")), (30, 15)), 90)
PLAYER_LASER = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("assets", "player_laser.png")), (30, 15)), 90)

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.jpg")), (WIDTH, HEIGHT))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not 0 <= self.y <= height

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SPACE_SHIP
        self.laser_img = PLAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 7))
        pygame.draw.rect(window, (0, 255, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 7))

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+53, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Enemy(Ship):
    SHIP_MAP = {
                "bird": (BIRD_SPACE_SHIP, ENEMY_LASER),
                "ufo": (UFO_SPACE_SHIP, ENEMY_LASER),
                "red": (RED_SPACE_SHIP, ENEMY_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.SHIP_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 27, self.y + 23, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def img_darker(width, height, alpha, color, location):
    dark = pygame.Surface((width, height))
    dark.set_alpha(alpha)
    dark.fill(color)
    WIN.blit(dark, location)


def main():
    run = True
    fps = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("mvboli", 45)
    lost_font = pygame.font.SysFont("mvboli", 60)

    enemies = []
    wave_length = 3
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(WIDTH // 2 - 70, 530)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        img_darker(WIDTH, HEIGHT, 128, (0, 0, 0), (0, 0))
        '''dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 128))
        WIN.blit(dark, (0, 0))'''

        for each_enemy in enemies:
            each_enemy.draw(WIN)

        # Draw text
        level_label = main_font.render(f"Level: {level}", True, (255, 255, 255))
        lives_label = main_font.render(f"Lives: {lives}", True, (255, 255, 255))

        WIN.blit(level_label, (10, 10))
        WIN.blit(lives_label, (WIDTH - lives_label.get_width() - 10, 10))

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You lost!!!", True, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, HEIGHT/2 - lost_label.get_height()/2))

        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > fps * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 3
            for _ in range(wave_length):
                enemy = Enemy(random.randrange(85, WIDTH - 85), random.randrange(-1000, -100), random.choice(["bird", "ufo", "red"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player.get_width() + player_vel < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player.get_height() + player_vel + 20 < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 3*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            if enemy.y + enemy.get_height() >= HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("mvboli", 40)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", True, (255, 255, 255))
        WIN.blit(title_label, (WIDTH//2 - title_label.get_width()//2, HEIGHT//2 - title_label.get_height()//2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()

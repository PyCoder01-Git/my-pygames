import pygame
import sys
import random

# Başlat
pygame.init()
clock = pygame.time.Clock()

# Ekran
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Mania - Boss Fight")

# Renkler
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
PURPLE = (160, 0, 200)

# Kamera
camera_x = 0

# Oyuncu
player = pygame.Rect(100, 500, 40, 40)
vel_x = 0
vel_y = 0
acceleration = 0.5
max_speed = 8
friction = 0.3
on_ground = False
jump_power = -12
gravity = 0.6
lives = 3
score = 0

# Platformlar
platforms = []
for i in range(25):
    platforms.append(pygame.Rect(i * 200, 550, 200, 50))

platforms += [
    pygame.Rect(1200, 450, 100, 20),
    pygame.Rect(1500, 350, 100, 20),
    pygame.Rect(1900, 300, 100, 20),
    pygame.Rect(2200, 250, 100, 20)
]

# Yüzükler
rings = [pygame.Rect(random.randint(300, 2000), random.randint(200, 500), 20, 20) for _ in range(20)]

# Düşmanlar
enemies = [pygame.Rect(800 + i * 400, 520, 40, 40) for i in range(3)]

# Boss
boss = pygame.Rect(2400, 450, 80, 80)
boss_alive = True
boss_health = 3
boss_fireballs = []
boss_timer = 0
fight_started = False
win = False

# Fonksiyonlar
def reset_player():
    global vel_x, vel_y
    player.x, player.y = 100, 500
    vel_x = vel_y = 0

# Ana oyun döngüsü
while True:
    screen.fill(WHITE)

    # Etkinlikler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Tuşlar
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]: vel_x += acceleration
    elif keys[pygame.K_LEFT]: vel_x -= acceleration
    else:
        vel_x -= friction if vel_x > 0 else -friction if vel_x < 0 else 0

    vel_x = max(-max_speed, min(max_speed, vel_x))

    if keys[pygame.K_SPACE] and on_ground:
        vel_y = jump_power

    # Yerçekimi ve hareket
    vel_y += gravity
    player.x += vel_x
    player.y += vel_y
    on_ground = False

    for plat in platforms:
        if player.colliderect(plat):
            if vel_y > 0 and player.bottom <= plat.bottom:
                player.bottom = plat.top
                vel_y = 0
                on_ground = True

    # Kamera
    camera_x = player.x - WIDTH // 2

    # Yüzük toplama
    for ring in rings[:]:
        if player.colliderect(ring):
            rings.remove(ring)
            score += 1

    # Düşman
    for enemy in enemies:
        enemy.x += 2 if pygame.time.get_ticks() // 500 % 2 == 0 else -2
        if player.colliderect(enemy):
            lives -= 1
            reset_player()

    # Ölüm hattı
    if player.y > 1000:
        lives -= 1
        reset_player()

    # Boss savaş alanına giriş
    if player.x >= 2300:
        fight_started = True

    # Boss davranışı
    if fight_started and boss_alive:
        boss_timer += 1
        boss.x += 2 if boss_timer // 60 % 2 == 0 else -2

        # Ateş topları
        if boss_timer % 90 == 0:
            fireball = pygame.Rect(boss.centerx, boss.centery, 15, 15)
            boss_fireballs.append(fireball)

        # Ateş topu hareketi
        for fireball in boss_fireballs[:]:
            fireball.x -= 6
            if fireball.colliderect(player):
                boss_fireballs.remove(fireball)
                lives -= 1
                reset_player()
            elif fireball.x < player.x - 500:
                boss_fireballs.remove(fireball)

        # Oyuncu boss'a zıplarsa hasar
        if player.colliderect(boss) and vel_y > 0:
            vel_y = jump_power
            boss_health -= 1
            if boss_health <= 0:
                boss_alive = False
                win = True

    # Çizimler
    for plat in platforms:
        pygame.draw.rect(screen, GREEN, (plat.x - camera_x, plat.y, plat.width, plat.height))

    for ring in rings:
        pygame.draw.ellipse(screen, YELLOW, (ring.x - camera_x, ring.y, 20, 20))

    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy.x - camera_x, enemy.y, 40, 40))

    for fireball in boss_fireballs:
        pygame.draw.circle(screen, PURPLE, (fireball.x - camera_x, fireball.y), 8)

    pygame.draw.rect(screen, BLUE, (player.x - camera_x, player.y, 40, 40))

    if boss_alive and fight_started:
        pygame.draw.rect(screen, BLACK, (boss.x - camera_x, boss.y, boss.width, boss.height))
        # Boss canı
        pygame.draw.rect(screen, RED, (boss.x - camera_x, boss.y - 20, boss.width * boss_health / 3, 10))

    # UI
    font = pygame.font.SysFont(None, 30)
    screen.blit(font.render(f"Yüzük: {score}", True, BLACK), (10, 10))
    screen.blit(font.render(f"Can: {lives}", True, BLACK), (10, 40))

    if win:
        screen.blit(font.render("YOU WIN!", True, BLUE), (WIDTH // 2 - 60, HEIGHT // 2))
    if lives <= 0:
        screen.blit(font.render("GAME OVER", True, RED), (WIDTH // 2 - 80, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    clock.tick(60)

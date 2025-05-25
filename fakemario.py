import pygame
import sys

# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 450
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini Mario - Pygame Edition")

# Colors
COLOR_BG = (92, 148, 252)
COLOR_GROUND = (100, 50, 20)
COLOR_PLATFORM = (150, 75, 0)
COLOR_PLAYER = (230, 0, 18)
COLOR_ENEMY = (0, 0, 0)
COLOR_COIN = (255, 215, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_SHADOW = (50, 50, 50)

# Settings
GRAVITY = 0.6
PLAYER_SPEED = 5
JUMP_POWER = 14

FONT = pygame.font.SysFont("Consolas", 24)

clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 32
        self.height = 48
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(COLOR_PLAYER)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.vel_y = 0
        self.on_ground = False
        self.score = 0

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = PLAYER_SPEED

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 15:
            self.vel_y = 15
        dy = self.vel_y

        # Move horizontal
        self.rect.x += dx
        self.collide(dx, 0, platforms)

        # Move vertical
        self.rect.y += dy
        self.on_ground = False
        self.collide(0, dy, platforms)

    def collide(self, dx, dy, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dy > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif dy < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
                if dx > 0:
                    self.rect.right = platform.rect.left
                elif dx < 0:
                    self.rect.left = platform.rect.right

    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_POWER

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height=20):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(COLOR_PLATFORM)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_width):
        super().__init__()
        self.width = 32
        self.height = 32
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(COLOR_ENEMY)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.start_x = x
        self.patrol_width = patrol_width
        self.speed = 2

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > self.start_x + self.patrol_width:
            self.speed = -self.speed
        if self.rect.x < self.start_x:
            self.speed = -self.speed

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.radius = 10
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COLOR_COIN, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

def draw_text(surface, text, x, y):
    img = FONT.render(text, True, COLOR_TEXT)
    surface.blit(img, (x, y))

def main():
    player = Player(100, 300)

    # Create platforms
    platforms = pygame.sprite.Group()
    ground = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
    platforms.add(ground)
    platform1 = Platform(200, 320, 120)
    platform2 = Platform(400, 250, 100)
    platform3 = Platform(600, 180, 150)
    platforms.add(platform1, platform2, platform3)

    # Enemy
    enemy = Enemy(500, SCREEN_HEIGHT - 72, 100)

    # Coins
    coins = pygame.sprite.Group()
    coins.add(Coin(220, 290), Coin(430, 220), Coin(650, 150))

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP:
                    player.jump()

        player.update(platforms)
        enemy.update()

        # Check coin collection
        coin_hit = pygame.sprite.spritecollideany(player, coins)
        if coin_hit:
            player.score += 1
            coins.remove(coin_hit)

        # Check enemy collision
        if player.rect.colliderect(enemy.rect):
            # Simple reset on collision
            player.rect.topleft = (100, 300)
            player.score = 0

        # Draw everything
        SCREEN.fill(COLOR_BG)

        # Draw platforms
        for plat in platforms:
            SCREEN.blit(plat.image, plat.rect)

        # Draw coins
        for coin in coins:
            SCREEN.blit(coin.image, coin.rect)

        # Draw enemy shadow
        shadow_rect = pygame.Rect(enemy.rect.x+6, enemy.rect.y + enemy.height - 10, enemy.width-12, 8)
        pygame.draw.ellipse(SCREEN, COLOR_SHADOW, shadow_rect)

        # Draw enemy
        SCREEN.blit(enemy.image, enemy.rect)

        # Draw player shadow
        shadow_rect_p = pygame.Rect(player.rect.x+6, player.rect.y + player.height - 10, player.width-12, 8)
        pygame.draw.ellipse(SCREEN, COLOR_SHADOW, shadow_rect_p)

        # Draw player
        SCREEN.blit(player.image, player.rect)

        # Draw score
        draw_text(SCREEN, f"Score: {player.score}", 10, 10)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()



import pygame
import sys
import random

WIDTH, HEIGHT = 480, 640
FPS = 60
LANE_WIDTH = WIDTH // 3

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Çizimle Basit Araba Yarışı")
clock = pygame.time.Clock()

def draw_road():
    screen.fill((50, 50, 50))
    for i in range(1, 3):
        pygame.draw.line(screen, (255, 255, 255), (LANE_WIDTH * i, 0), (LANE_WIDTH * i, HEIGHT), 5)

class Car:
    def __init__(self, lane, color):
        self.lane = lane
        self.color = color
        self.width = 60
        self.height = 120
        self.x = LANE_WIDTH * lane + LANE_WIDTH // 2
        self.y = HEIGHT - self.height - 10
        self.rect = pygame.Rect(0,0,self.width,self.height)
        self.update_rect()

    def update_rect(self):
        self.rect.center = (self.x, self.y)

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.x = LANE_WIDTH * self.lane + LANE_WIDTH // 2
            self.update_rect()

    def move_right(self):
        if self.lane < 2:
            self.lane += 1
            self.x = LANE_WIDTH * self.lane + LANE_WIDTH // 2
            self.update_rect()

    def draw(self, surface):
        # Araba gövdesi
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        # Tekerlekler
        wheel_w, wheel_h = 15, 30
        offset_x = self.width//2 - wheel_w//2
        offset_y = 10
        # Sol ön tekerlek
        pygame.draw.rect(surface, (0,0,0), (self.rect.left, self.rect.top + offset_y, wheel_w, wheel_h), border_radius=5)
        # Sağ ön tekerlek
        pygame.draw.rect(surface, (0,0,0), (self.rect.right - wheel_w, self.rect.top + offset_y, wheel_w, wheel_h), border_radius=5)
        # Sol arka tekerlek
        pygame.draw.rect(surface, (0,0,0), (self.rect.left, self.rect.bottom - offset_y - wheel_h, wheel_w, wheel_h), border_radius=5)
        # Sağ arka tekerlek
        pygame.draw.rect(surface, (0,0,0), (self.rect.right - wheel_w, self.rect.bottom - offset_y - wheel_h, wheel_w, wheel_h), border_radius=5)

class EnemyCar(Car):
    def __init__(self, lane, speed, color):
        super().__init__(lane, color)
        self.y = -120
        self.speed = speed
        self.update_rect()

    def update(self):
        self.y += self.speed
        self.update_rect()

def main():
    player = Car(lane=1, color=(0,0,255))
    enemies = []
    obstacle_timer = 0
    obstacle_delay = 1500
    speed = 5

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move_left()
                elif event.key == pygame.K_RIGHT:
                    player.move_right()

        obstacle_timer += dt
        if obstacle_timer > obstacle_delay:
            obstacle_timer = 0
            lane = random.randint(0,2)
            enemy = EnemyCar(lane, speed, (255,0,0))
            enemies.append(enemy)

        # Güncelle
        for enemy in enemies[:]:
            enemy.update()
            if enemy.y > HEIGHT + 100:
                enemies.remove(enemy)

        # Çarpışma kontrolü
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                print("Çarpışma! Oyun bitti.")
                running = False

        # Çizimler
        draw_road()
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

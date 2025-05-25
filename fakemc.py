import pygame
import sys

# Initialize pygame
pygame.init()

# Window settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini Minecraft - Pygame Edition")

# Colors
COLOR_SKY = (135, 206, 235)
COLOR_GRASS = (80, 200, 120)
COLOR_DIRT = (134, 96, 67)
COLOR_STONE = (125, 125, 125)
COLOR_PLAYER = (255, 50, 50)
COLOR_UI_BG = (30, 30, 30, 180)
COLOR_TEXT = (220, 220, 220)
COLOR_HIGHLIGHT = (255, 255, 0)

# Grid settings
TILE_SIZE = 40
GRID_COLUMNS = SCREEN_WIDTH // TILE_SIZE
GRID_ROWS = SCREEN_HEIGHT // TILE_SIZE

# Block types
BLOCK_AIR = 0
BLOCK_GRASS = 1
BLOCK_DIRT = 2
BLOCK_STONE = 3

BLOCK_TYPES = {
    BLOCK_GRASS: COLOR_GRASS,
    BLOCK_DIRT: COLOR_DIRT,
    BLOCK_STONE: COLOR_STONE,
}

# Player movement speed (tiles per second)
PLAYER_SPEED = 5

# Fonts
FONT = pygame.font.SysFont("Consolas", 20)

class World:
    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows
        # Initialize grid with air blocks
        self.grid = [[BLOCK_AIR for _ in range(self.rows)] for _ in range(self.columns)]

        # Create some ground layers
        ground_height = self.rows // 3
        for x in range(self.columns):
            for y in range(self.rows - ground_height, self.rows):
                # Bottom layer stone, upper layers dirt, top dirt replaced by grass
                if y == self.rows - 1:
                    self.grid[x][y] = BLOCK_STONE
                elif y >= self.rows - ground_height + 2:
                    self.grid[x][y] = BLOCK_DIRT
                else:
                    self.grid[x][y] = BLOCK_GRASS
    
    def draw(self, surface):
        for x in range(self.columns):
            for y in range(self.rows):
                block = self.grid[x][y]
                if block != BLOCK_AIR:
                    color = BLOCK_TYPES.get(block, COLOR_GRASS)
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, color, rect)
                    # Draw block borders for nicer look
                    pygame.draw.rect(surface, (50, 50, 50), rect, 1)
        
    def in_bounds(self, x, y):
        return 0 <= x < self.columns and 0 <= y < self.rows
    
    def get_block(self, x, y):
        if not self.in_bounds(x, y):
            return None
        return self.grid[x][y]
    
    def set_block(self, x, y, block_type):
        if self.in_bounds(x, y):
            self.grid[x][y] = block_type

class Player:
    def __init__(self, world):
        # Start position on top of grass layer near center
        self.x = world.columns // 2
        self.y = 0
        # Find surface y position starting from top
        for y_check in range(world.rows):
            if world.get_block(self.x, y_check) != BLOCK_AIR:
                self.y = y_check - 1
                break

        self.world = world
        self.move_x = 0
        self.move_y = 0
        self.pos_x = self.x * TILE_SIZE
        self.pos_y = self.y * TILE_SIZE
        self.speed = PLAYER_SPEED * TILE_SIZE  # pixels per second

    def handle_input(self, keys):
        self.move_x = 0
        self.move_y = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.move_x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.move_x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.move_y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.move_y = 1

    def update(self, dt):
        if self.move_x != 0 or self.move_y != 0:
            target_x = self.x + self.move_x
            target_y = self.y + self.move_y
            # Check collision with blocks. Can only move if target block is air
            if self.world.in_bounds(target_x, target_y):
                target_block = self.world.get_block(target_x, target_y)
                below_block = self.world.get_block(target_x, target_y + 1)
                # Basic gravity support: Player can only move if the block below target is not air (we stand on blocks)
                # or player can move on block itself if the target_block is air
                if (target_block == BLOCK_AIR and (below_block != BLOCK_AIR or target_y == self.world.rows - 1)) or (target_block == BLOCK_AIR and target_y == self.y):
                    self.x = target_x
                    self.y = target_y

        # Smooth position update for nicer movement
        target_pos_x = self.x * TILE_SIZE
        target_pos_y = self.y * TILE_SIZE
        # lerp movement
        lerp_speed = 12
        self.pos_x += (target_pos_x - self.pos_x) * min(lerp_speed * dt, 1)
        self.pos_y += (target_pos_y - self.pos_y) * min(lerp_speed * dt, 1)

    def draw(self, surface):
        rect = pygame.Rect(self.pos_x, self.pos_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, COLOR_PLAYER, rect)
        # Draw subtle shadow
        shadow_rect = pygame.Rect(self.pos_x + 5, self.pos_y + TILE_SIZE - 8, TILE_SIZE - 10, 5)
        pygame.draw.ellipse(surface, (0, 0, 0, 100), shadow_rect)

def draw_grid(surface, columns, rows, tile_size):
    for x in range(columns):
        pygame.draw.line(surface, (200, 200, 200, 20), (x * tile_size, 0), (x * tile_size, rows * tile_size))
    for y in range(rows):
        pygame.draw.line(surface, (200, 200, 200, 20), (0, y * tile_size), (columns * tile_size, y * tile_size))

def draw_ui(surface, selected_block):
    # Panel background
    panel_height = 60
    panel_rect = pygame.Rect(0, SCREEN_HEIGHT - panel_height, SCREEN_WIDTH, panel_height)
    pygame.draw.rect(surface, COLOR_UI_BG, panel_rect)

    # Text: controls and selected block
    text1 = FONT.render("Arrow keys or WASD to move. Left-click to place block. Right-click to remove block.", True, COLOR_TEXT)
    surface.blit(text1, (10, SCREEN_HEIGHT - panel_height + 5))

    text2 = FONT.render(f"Selected block: {block_name(selected_block)} (press keys 1-3 to change)", True, COLOR_TEXT)
    surface.blit(text2, (10, SCREEN_HEIGHT - panel_height + 30))

def block_name(block_type):
    if block_type == BLOCK_GRASS:
        return "Grass"
    elif block_type == BLOCK_DIRT:
        return "Dirt"
    elif block_type == BLOCK_STONE:
        return "Stone"
    return "None"

def main():
    clock = pygame.time.Clock()
    world = World(GRID_COLUMNS, GRID_ROWS)
    player = Player(world)
    selected_block = BLOCK_GRASS

    running = True
    while running:
        dt = clock.tick(60) / 1000  # delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Change selected block
                if event.key == pygame.K_1:
                    selected_block = BLOCK_GRASS
                elif event.key == pygame.K_2:
                    selected_block = BLOCK_DIRT
                elif event.key == pygame.K_3:
                    selected_block = BLOCK_STONE
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // TILE_SIZE
                grid_y = mouse_y // TILE_SIZE
                # Left click to place block if space is empty and not player stands there
                if event.button == 1:
                    if world.in_bounds(grid_x, grid_y):
                        if world.get_block(grid_x, grid_y) == BLOCK_AIR and not (grid_x == player.x and grid_y == player.y):
                            world.set_block(grid_x, grid_y, selected_block)
                # Right click to remove block if block is not air and not under player
                elif event.button == 3:
                    if world.in_bounds(grid_x, grid_y):
                        if world.get_block(grid_x, grid_y) != BLOCK_AIR and not (grid_x == player.x and grid_y == player.y):
                            world.set_block(grid_x, grid_y, BLOCK_AIR)

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update(dt)
        
        # Draw everything
        SCREEN.fill(COLOR_SKY)
        world.draw(SCREEN)
        player.draw(SCREEN)
        draw_ui(SCREEN, selected_block)

        # Draw a highlight box under mouse on grid if in bounds
        mouse_grid_x, mouse_grid_y = pygame.mouse.get_pos()[0] // TILE_SIZE, pygame.mouse.get_pos()[1] // TILE_SIZE
        if world.in_bounds(mouse_grid_x, mouse_grid_y):
            highlight_rect = pygame.Rect(mouse_grid_x * TILE_SIZE, mouse_grid_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(SCREEN, COLOR_HIGHLIGHT, highlight_rect, 3)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


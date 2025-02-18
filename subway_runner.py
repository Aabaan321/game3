import pygame
import random
import json
from pathlib import Path

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game Constants
WIDTH = 800
HEIGHT = 600
FPS = 60
GRAVITY = 0.8
LANE_WIDTH = WIDTH // 3
LANES = [LANE_WIDTH // 2, LANE_WIDTH * 1.5, LANE_WIDTH * 2.5]

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Subway Runner")
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 40
        self.height = 60
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = LANES[1]
        self.rect.bottom = HEIGHT - 20
        self.speed = 8
        self.lane = 1
        self.jumping = False
        self.velocity = 0
        self.invincible = False
        self.invincible_timer = 0
        
    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.velocity = -15
            
    def update(self):
        if self.jumping:
            self.velocity += GRAVITY
            self.rect.y += self.velocity
            
            if self.rect.bottom >= HEIGHT - 20:
                self.rect.bottom = HEIGHT - 20
                self.jumping = False
                self.velocity = 0
        
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.image.fill(BLUE)
                
    def change_lane(self, direction):
        if direction == 'left' and self.lane > 0:
            self.lane -= 1
        elif direction == 'right' and self.lane < 2:
            self.lane += 1
        self.rect.centerx = LANES[self.lane]

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, lane):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = LANES[lane]
        self.rect.y = -50
        self.speed = random.randint(5, 8)
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Powerup(pygame.sprite.Sprite):
    def __init__(self, lane):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = LANES[lane]
        self.rect.y = -50
        self.speed = 5
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, lane):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = LANES[lane]
        self.rect.y = -30
        self.speed = 5
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Game:
    def __init__(self):
        self.high_score = 0
        self.reset_game()

    def reset_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        
        self.score = 0
        self.coins_collected = 0
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_interval = 60
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_LEFT:
                    self.player.change_lane('left')
                elif event.key == pygame.K_RIGHT:
                    self.player.change_lane('right')
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        return True
    
    def spawn_objects(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            
            lane = random.randint(0, 2)
            
            # Spawn obstacle
            if random.random() < 0.7:  # 70% chance for obstacle
                obstacle = Obstacle(lane)
                self.all_sprites.add(obstacle)
                self.obstacles.add(obstacle)
            
            # Spawn powerup
            if random.random() < 0.1:  # 10% chance for powerup
                powerup_lane = random.randint(0, 2)
                if powerup_lane != lane:
                    powerup = Powerup(powerup_lane)
                    self.all_sprites.add(powerup)
                    self.powerups.add(powerup)
            
            # Spawn coin
            if random.random() < 0.3:  # 30% chance for coin
                coin_lane = random.randint(0, 2)
                if coin_lane != lane:
                    coin = Coin(coin_lane)
                    self.all_sprites.add(coin)
                    self.coins.add(coin)
    
    def check_collisions(self):
        if not self.player.invincible:
            hits = pygame.sprite.spritecollide(self.player, self.obstacles, False)
            if hits:
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
        
        # Powerup collection
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            self.player.invincible = True
            self.player.invincible_timer = 180
            self.player.image.fill(YELLOW)
            self.score += 50
        
        # Coin collection
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        for coin in coin_hits:
            self.coins_collected += 1
            self.score += 10
    
    def update(self):
        if not self.game_over:
            self.all_sprites.update()
            self.spawn_objects()
            self.check_collisions()
            self.score += 1
            
            # Increase difficulty
            if self.score % 1000 == 0:
                self.spawn_interval = max(20, self.spawn_interval - 5)
    
    def draw(self):
        screen.fill(WHITE)
        
        # Draw lanes
        for x in LANES:
            pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT), 2)
        
        self.all_sprites.draw(screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, BLACK)
        coins_text = font.render(f'Coins: {self.coins_collected}', True, BLACK)
        high_score_text = font.render(f'High Score: {self.high_score}', True, BLACK)
        
        screen.blit(score_text, (10, 10))
        screen.blit(coins_text, (10, 50))
        screen.blit(high_score_text, (10, 90))
        
        if self.game_over:
            font = pygame.font.Font(None, 74)
            game_over_text = font.render('Game Over!', True, BLACK)
            restart_text = font.render('Press R to Restart', True, BLACK)
            screen.blit(game_over_text, (WIDTH//2 - 160, HEIGHT//2 - 50))
            screen.blit(restart_text, (WIDTH//2 - 200, HEIGHT//2 + 50))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.quit()

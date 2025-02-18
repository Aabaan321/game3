import pygame
import random
import os
import json

# Initialize Pygame and mixer for sounds
pygame.init()
pygame.mixer.init()

# Game Constants
WIDTH = 1024
HEIGHT = 768
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

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Subway Runner")
clock = pygame.time.Clock()

# Load high score
def load_high_score():
    try:
        with open('high_score.json', 'r') as f:
            return json.load(f)['high_score']
    except:
        return 0

def save_high_score(score):
    with open('high_score.json', 'w') as f:
        json.dump({'high_score': score}, f)

# Asset loading
def load_image(name):
    image = pygame.image.load(os.path.join('assets', name))
    return pygame.transform.scale(image, (60, 80))

# Sprite classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 60))
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
            self.velocity = -20
            
    def update(self):
        # Jumping physics
        if self.jumping:
            self.velocity += GRAVITY
            self.rect.y += self.velocity
            
            if self.rect.bottom >= HEIGHT - 20:
                self.rect.bottom = HEIGHT - 20
                self.jumping = False
                self.velocity = 0
        
        # Invincibility timer
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
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = LANES[lane]
        self.rect.y = -100
        self.speed = random.randint(5, 10)
        
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
        self.rect.y = -100
        self.speed = 5
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Game:
    def __init__(self):
        self.load_game_data()
        self.reset_game()
        
    def load_game_data(self):
        self.high_score = load_high_score()
        
    def reset_game(self):
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Game state
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_interval = 60
        self.difficulty_timer = 0
        self.difficulty_interval = 1000
        
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
            
            # Spawn obstacle
            lane = random.randint(0, 2)
            obstacle = Obstacle(lane)
            self.all_sprites.add(obstacle)
            self.obstacles.add(obstacle)
            
            # Sometimes spawn powerup
            if random.random() < 0.2:  # 20% chance
                powerup_lane = random.randint(0, 2)
                if powerup_lane != lane:  # Don't spawn powerup in same lane as obstacle
                    powerup = Powerup(powerup_lane)
                    self.all_sprites.add(powerup)
                    self.powerups.add(powerup)
    
    def increase_difficulty(self):
        self.difficulty_timer += 1
        if self.difficulty_timer >= self.difficulty_interval:
            self.difficulty_timer = 0
            self.spawn_interval = max(20, self.spawn_interval - 5)
    
    def check_collisions(self):
        if not self.player.invincible:
            hits = pygame.sprite.spritecollide(self.player, self.obstacles, False)
            if hits:
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    save_high_score(self.high_score)
        
        # Powerup collection
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            self.player.invincible = True
            self.player.invincible_timer = 180  # 3 seconds at 60 FPS
            self.player.image.fill(YELLOW)  # Visual feedback
            self.score += 50
    
    def update(self):
        if not self.game_over:
            self.all_sprites.update()
            self.spawn_objects()
            self.increase_difficulty()
            self.check_collisions()
            self.score += 1
    
    def draw(self):
        screen.fill(WHITE)
        
        # Draw lanes
        for x in LANES:
            pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT), 2)
        
        self.all_sprites.draw(screen)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, BLACK)
        high_score_text = font.render(f'High Score: {self.high_score}', True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 50))
        
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

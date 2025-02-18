import pygame
import random

# Initialize
pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Subway Runner")
clock = pygame.time.Clock()

# Colors and Settings
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LANES = [200, 400, 600]

class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.lane = 1
        self.x = LANES[self.lane]
        self.y = HEIGHT - 100
        self.jumping = False
        self.jump_speed = 0
        
    def move(self, direction):
        if direction == "left" and self.lane > 0:
            self.lane -= 1
        elif direction == "right" and self.lane < 2:
            self.lane += 1
        self.x = LANES[self.lane]
        
    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.jump_speed = -15
            
    def update(self):
        if self.jumping:
            self.y += self.jump_speed
            self.jump_speed += 0.8
            if self.y >= HEIGHT - 100:
                self.y = HEIGHT - 100
                self.jumping = False
                
    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x - 20, self.y, self.width, self.height))

class Obstacle:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.lane = random.randint(0, 2)
        self.x = LANES[self.lane]
        self.y = -50
        self.speed = 5
        
    def update(self):
        self.y += self.speed
        
    def draw(self):
        pygame.draw.rect(screen, RED, (self.x - 20, self.y, self.width, self.height))

def main():
    player = Player()
    obstacles = []
    score = 0
    game_over = False
    
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_LEFT:
                        player.move("left")
                    if event.key == pygame.K_RIGHT:
                        player.move("right")
                    if event.key == pygame.K_SPACE:
                        player.jump()
                if event.key == pygame.K_r and game_over:
                    # Reset game
                    player = Player()
                    obstacles = []
                    score = 0
                    game_over = False
        
        if not game_over:
            # Update game
            player.update()
            
            # Spawn obstacles
            if random.randint(1, 60) == 1:
                obstacles.append(Obstacle())
                
            # Update and check obstacles
            for obstacle in obstacles[:]:
                obstacle.update()
                
                # Collision check
                if (abs(obstacle.x - player.x) < 40 and 
                    abs(obstacle.y - player.y) < 50):
                    game_over = True
                    
                # Remove and score
                if obstacle.y > HEIGHT:
                    obstacles.remove(obstacle)
                    score += 1
            
            # Draw everything
            screen.fill(WHITE)
            
            # Draw lanes
            for x in LANES:
                pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT), 2)
                
            player.draw()
            for obstacle in obstacles:
                obstacle.draw()
                
            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Score: {score}', True, BLACK)
            screen.blit(score_text, (10, 10))
            
        else:
            # Game over screen
            font = pygame.font.Font(None, 74)
            text = font.render('Game Over!', True, BLACK)
            screen.blit(text, (WIDTH//2 - 160, HEIGHT//2 - 50))
            restart_text = font.render('Press R to Restart', True, BLACK)
            screen.blit(restart_text, (WIDTH//2 - 200, HEIGHT//2 + 50))
            
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

import pygame
import random

# Initialize Pygame
pygame.init()

# Initialize the mixer module for sound
pygame.mixer.init()

# Load background music
pygame.mixer.music.load("background_music.mp3")

# Play background music in a loop (-1 means loop indefinitely)
pygame.mixer.music.play(-1)

# Set the volume (between 0.0 and 1.0)
pygame.mixer.music.set_volume(0.5)

# Screen settings
screen_width = 1000
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Run and Collect")

# Load and resize the background image to match the screen size
background_image = pygame.image.load("background2.jpeg")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# Define a function to handle scrolling backgrounds
def update_background():
    global background_x
    
    # Move the background image to the left
    background_x -= background_speed
    
    # If the background image moves off screen, reset its position
    if background_x <= -screen_width:
        background_x = 0
    
    # Draw the background on the screen
    screen.blit(background_image, (background_x, 0))
    screen.blit(background_image, (background_x + screen_width, 0))

# Load and resize the player image
player_image = pygame.image.load("player.png")
player_image = pygame.transform.scale(player_image, (50, 150))

# Load item images and resize them
item_images = [
    pygame.image.load("apple.png"),
    pygame.image.load("banana.png"),
    pygame.image.load("orange.png"),
    pygame.image.load("cherry.png"),
]
item_images = [pygame.transform.scale(img, (30, 30)) for img in item_images]

# Load box image and resize it
box_image = pygame.image.load("box.png")
box_image = pygame.transform.scale(box_image, (50, 50))

# Load obstacle image and resize it
obstacle_image = pygame.image.load("obstacle.png")  # Provide your obstacle image file here
obstacle_image = pygame.transform.scale(obstacle_image, (50, 50))

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BASE_COLOR = (0, 128, 0)  # Color for the base (ground)

# Define fonts
font = pygame.font.Font(None, 36)
button_font = pygame.font.Font(None, 48)

# Define the base height
base_height = 75  # Height of the base (ground)

# Define the maximum jump height
MAX_JUMP_HEIGHT = 1  # Number of times the player can jump

# Background position and speed
background_x = 0
background_speed = 3  # Adjust the speed as desired

# Define Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        # Set starting position to the middle of the game screen
        self.rect.x = screen_width // 2 - self.rect.width // 2
        self.rect.y = screen_height - self.rect.height - base_height
        self.jump_power = 25  # Initial jump power
        self.gravity = 1  # Gravity effect on player
        self.velocity_y = 0  # Vertical velocity for player movement
        self.jump_count = 0  # Track the number of jumps performed
        self.collected_items = []  # List to keep track of collected items
        self.is_stopped = False  # Flag to check if player is stopped
        
    def update(self):
        # Apply gravity
        if not self.is_stopped:
            self.velocity_y += self.gravity
            self.rect.y += self.velocity_y

        # Check for landing on the ground
        if self.rect.y >= screen_height - self.rect.height - base_height:
            self.rect.y = screen_height - self.rect.height - base_height
            self.velocity_y = 0
            self.jump_count = 0  # Reset jump count when on the ground

        # Handle jumping
        if not self.is_stopped:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
                # Allow double jump (up to MAX_JUMP_HEIGHT jumps)
                if self.jump_count < MAX_JUMP_HEIGHT:
                    self.velocity_y = -self.jump_power
                    self.jump_count += 1
        
        # Handle stopping (player stops when the 's' key is pressed near a box)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.is_stopped = True
        else:
            self.is_stopped = False

# Define Item class
class Item(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = random.choice(item_images)
        self.rect = self.image.get_rect()
        self.rect.x = screen_width  # Starting x position
        self.rect.y = random.randint(base_height, screen_height - base_height - self.rect.height)  # Random y position

    def update(self):
        # Move item to the left
        self.rect.x -= 5
        
        # Remove item if it goes off screen
        if self.rect.x < -self.rect.width:
            self.kill()

# Define Box class
class Box(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = box_image
        self.rect = self.image.get_rect()
        self.rect.x = screen_width  # Starting x position
        self.rect.y = screen_height - base_height - self.rect.height  # Place box on the ground

    def update(self):
        # Move box to the left
        self.rect.x -= 5
        
        # Remove box if it goes off screen
        if self.rect.x < -self.rect.width:
            # Increment missed donations counter
            global missed_donations
            missed_donations += 1
            self.kill()

# Define Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = obstacle_image
        self.rect = self.image.get_rect()
        self.rect.x = screen_width  # Starting x position
        self.rect.y = screen_height - base_height - self.rect.height  # Place obstacle on the ground
        self.player = player  # Reference to the player object

    def update(self):
        global game_over
        
        # Move obstacle to the left
        self.rect.x -= 5
        
        # Check for collision with the player
        if self.rect.colliderect(self.player.rect):
            # End the game immediately if collision occurs
            game_over = True
        
        # Remove obstacle if it goes off screen
        if self.rect.x < -self.rect.width:
            self.kill()

# Create groups
all_sprites = pygame.sprite.Group()
item_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()  # New group for obstacles

# Create player
player = Player()
all_sprites.add(player)

# Game state flags
game_started = False
game_over = False

# Set up game clock
clock = pygame.time.Clock()

# Timer for spawning items, boxes, and obstacles
item_spawn_timer = 0
box_spawn_timer = 0
obstacle_spawn_timer = 0  # New timer for spawning obstacles

# Number of donations made
donations_made = 0

# Number of missed boxes
missed_donations = 0  # Counter to track missed donations

# Define the obstacle spawn timer
obstacle_spawn_timer = 0

# Main loop
running = True
while running:
    if not game_started:
        # Main menu screen
        screen.fill(WHITE)
        
        # Display "Run and Collect" title
        title_text = font.render("Run and Collect", True, BLACK)
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 100))

        # Display "Start" button
        start_text = button_font.render("Start", True, WHITE, GREEN)
        start_button = start_text.get_rect(center=(screen_width // 2, 200))
        screen.blit(start_text, start_button.topleft)

        # Event handling for main menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    game_started = True
        
        # Update display
        pygame.display.flip()
        
    elif game_over:
        # Stop the background music when the game is over
        pygame.mixer.music.stop()

        # Game over screen
        screen.fill(WHITE)
        
        # Display "Game Over" title
        game_over_text = font.render("Game Over", True, BLACK)
        screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 100))

        # Display "Donations Made" and "Collected Items" counts
        donations_text = font.render(f"Donations Made: {donations_made}", True, BLACK)
        screen.blit(donations_text, (screen_width // 2 - donations_text.get_width() // 2, 200))
        collected_text = font.render(f"Collected Items: {len(player.collected_items)}", True, BLACK)
        screen.blit(collected_text, (screen_width // 2 - collected_text.get_width() // 2, 300))

        # Display the number of missed donations on the game over screen
        missed_donations_text = font.render(f"Missed Donations: {missed_donations}", True, BLACK)
        screen.blit(missed_donations_text, (screen_width // 2 - missed_donations_text.get_width() // 2, 400))

        # Display "Press ESC to Exit" message
        exit_text = font.render("Press ESC to Exit", True, BLACK)
        screen.blit(exit_text, (screen_width // 2 - exit_text.get_width() // 2, 500))

        # Event handling for game over screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Update display
        pygame.display.flip()

    else:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Handle stopping near a box
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                # Check for player-box collision
                player_box_collisions = pygame.sprite.spritecollide(player, box_group, False)
                if player_box_collisions:
                    # Stop the player and donate collected items
                    player.is_stopped = True
                    donations_made += 1
                    player.collected_items = []  # Clear the list of collected items
                    
                    # Remove the box after donation
                    for box in player_box_collisions:
                        box.kill()
            # Reset stop flag after handling events
            player.is_stopped = False

        # Check for player-obstacle collision and stop player if it happens
        player_obstacle_collisions = pygame.sprite.spritecollide(player, obstacle_group, False)
        if player_obstacle_collisions:
            player.is_stopped = True  # Stop the player upon collision with an obstacle

        # Update player
        player.update()

        # Update items, boxes, and obstacles
        item_group.update()
        box_group.update()
        obstacle_group.update()  # Update obstacles

        # Spawn new item periodically
        item_spawn_timer += clock.get_time()
        if item_spawn_timer >= 2000:  # Every 2 seconds
            item = Item()
            all_sprites.add(item)
            item_group.add(item)
            item_spawn_timer = 0
        
        # Spawn new box periodically
        box_spawn_timer += clock.get_time()
        if box_spawn_timer >= 5000:  # Every 5 seconds
            box = Box()
            all_sprites.add(box)
            box_group.add(box)
            box_spawn_timer = 0
        
        # Spawn new obstacle periodically
        obstacle_spawn_timer += clock.get_time()
        if obstacle_spawn_timer >= 3000:  # Every 3 seconds (adjust as needed)
            obstacle = Obstacle(player)
            all_sprites.add(obstacle)
            obstacle_group.add(obstacle)
            obstacle_spawn_timer = 0

        # Check if the number of missed boxes has reached 3
        if missed_donations >= 3:
            game_over = True
        
        # Check for collisions between player and items
        collisions = pygame.sprite.spritecollide(player, item_group, True)
        if collisions:
            # Add collected items to player's collected_items list
            player.collected_items.extend(collisions)

        # Update the background
        update_background()

        # Draw all sprites
        all_sprites.draw(screen)
        
        # Draw the base (ground) as a green rectangle at the bottom of the screen
        pygame.draw.rect(screen, BASE_COLOR, (0, screen_height - base_height, screen_width, base_height))

        # Display collected items count on the left side of the screen
        collected_text = font.render(f"Collected: {len(player.collected_items)}", True, BLACK)
        screen.blit(collected_text, (10, 10))
        
        # Display the number of donations made on the right side of the screen
        donations_text = font.render(f"Donations Made: {donations_made}", True, BLACK)
        screen.blit(donations_text, (screen_width - donations_text.get_width() - 10, 10))
        
        # Display the number of missed donations on the right side of the screen
        missed_donations_text = font.render(f"Missed Donations: {missed_donations}", True, BLACK)
        screen.blit(missed_donations_text, (screen_width - missed_donations_text.get_width() - 10, 50))

        # Update display
        pygame.display.flip()
        
        # Set frame rate
        clock.tick(60)
        
pygame.quit()

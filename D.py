import pygame
import sys
import random
from button import Button

# Initialize Pygame and the mixer module for sound
pygame.init()
pygame.mixer.init()

# Screen settings
screen_width, screen_height = 1280, 720
SCREEN = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Run and Collect")

# Load images and resize them
background_image = pygame.image.load("background.jpeg")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

player_image = pygame.image.load("player.png")
player_image = pygame.transform.scale(player_image, (50, 150))

item_images = [pygame.image.load("apple.png"), pygame.image.load("banana.png"), pygame.image.load("orange.png"), pygame.image.load("cherry.png")]
item_images = [pygame.transform.scale(img, (30, 30)) for img in item_images]

box_image = pygame.image.load("box.png")
box_image = pygame.transform.scale(box_image, (50, 50))

obstacle_image = pygame.image.load("obstacle.png")
obstacle_image = pygame.transform.scale(obstacle_image, (50, 50))

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BASE_COLOR = (0, 128, 0)

# Define fonts
def get_font(size):
    return pygame.font.Font("font.ttf", size)

font = get_font(36)
button_font = get_font(48)

# Game settings and state variables
base_height = 75  # Height of the base (ground)
background_x = 0
background_speed = 3
MAX_JUMP_HEIGHT = 1

# Sound and music settings
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

# Define the base height
BASE_HEIGHT = 75

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

# Define a function to handle scrolling backgrounds
def update_background():
    global background_x
    
    # Move the background image to the left
    background_x -= background_speed
    
    # If the background image moves off screen, reset its position
    if background_x <= -screen_width:
        background_x = 0
    
    # Draw the background on the screen
    SCREEN.blit(background_image, (background_x, 0))
    SCREEN.blit(background_image, (background_x + screen_width, 0))

# Create groups for sprites
all_sprites = pygame.sprite.Group()
item_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()  # New group for obstacles

# Create player
player = Player()
all_sprites.add(player)

# Game state flags and variables
game_started = False
game_over = False
running = True

# Timer for spawning items, boxes, and obstacles
item_spawn_timer = 0
box_spawn_timer = 0
obstacle_spawn_timer = 0

# Number of donations made and missed boxes
donations_made = 0
missed_donations = 0

# Define main game loop
def play():
    global item_spawn_timer, box_spawn_timer, obstacle_spawn_timer, donations_made, missed_donations, game_over
    
    # Reset game state flags and variables
    game_over = False
    donations_made = 0
    missed_donations = 0
    player.collected_items = []
    
    # Start game loop
    while not game_over:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
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
        
        # Check for player-obstacle collision and end the game if it happens
        player_obstacle_collisions = pygame.sprite.spritecollide(player, obstacle_group, False)
        if player_obstacle_collisions:
            game_over = True
        
        # Update player
        player.update()
        
        # Update items, boxes, and obstacles
        item_group.update()
        box_group.update()
        obstacle_group.update()
        
        # Spawn new items, boxes, and obstacles at specified intervals
        spawn_intervals = {
            'item': 2000,  # Spawn an item every 2 seconds
            'box': 5000,   # Spawn a box every 5 seconds
            'obstacle': 3000  # Spawn an obstacle every 3 seconds
        }
        
        # Item spawn
        item_spawn_timer += clock.get_time()
        if item_spawn_timer >= spawn_intervals['item']:
            item = Item()
            all_sprites.add(item)
            item_group.add(item)
            item_spawn_timer = 0
        
        # Box spawn
        box_spawn_timer += clock.get_time()
        if box_spawn_timer >= spawn_intervals['box']:
            box = Box()
            all_sprites.add(box)
            box_group.add(box)
            box_spawn_timer = 0
        
        # Obstacle spawn
        obstacle_spawn_timer += clock.get_time()
        if obstacle_spawn_timer >= spawn_intervals['obstacle']:
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
        all_sprites.draw(SCREEN)
        
        # Draw the base (ground) as a green rectangle at the bottom of the screen
        pygame.draw.rect(SCREEN, BASE_COLOR, (0, screen_height - base_height, screen_width, base_height))
        
        # Display collected items count on the left side of the screen
        collected_text = font.render(f"Collected: {len(player.collected_items)}", True, BLACK)
        SCREEN.blit(collected_text, (10, 10))
        
        # Display the number of donations made on the right side of the screen
        donations_text = font.render(f"Donations Made: {donations_made}", True, BLACK)
        SCREEN.blit(donations_text, (screen_width - donations_text.get_width() - 10, 10))
        
        # Display the number of missed donations on the right side of the screen
        missed_donations_text = font.render(f"Missed Donations: {missed_donations}", True, BLACK)
        SCREEN.blit(missed_donations_text, (screen_width - missed_donations_text.get_width() - 10, 50))
        
        # Update display
        pygame.display.flip()
        
        # Set frame rate
        clock.tick(60)

    # If game is over, display game over screen
    pygame.mixer.music.stop()
    game_over_screen()

# Define game over screen
def game_over_screen():
    while True:
        SCREEN.fill(WHITE)
        
        # Display "Game Over" title
        game_over_text = font.render("Game Over", True, BLACK)
        SCREEN.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 100))
        
        # Display "Donations Made" and "Collected Items" counts
        donations_text = font.render(f"Donations Made: {donations_made}", True, BLACK)
        SCREEN.blit(donations_text, (screen_width // 2 - donations_text.get_width() // 2, 200))
        
        collected_text = font.render(f"Collected Items: {len(player.collected_items)}", True, BLACK)
        SCREEN.blit(collected_text, (screen_width // 2 - collected_text.get_width() // 2, 300))
        
        # Display the number of missed donations on the game over screen
        missed_donations_text = font.render(f"Missed Donations: {missed_donations}", True, BLACK)
        SCREEN.blit(missed_donations_text, (screen_width // 2 - missed_donations_text.get_width() // 2, 400))
        
        # Display "Press ESC to Exit" message
        exit_text = font.render("Press ESC to Exit", True, BLACK)
        SCREEN.blit(exit_text, (screen_width // 2 - exit_text.get_width() // 2, 500))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        
        pygame.display.flip()
        
# Define options screen
def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        
        SCREEN.fill("white")
        
        OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(screen_width // 2, 260))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)
        
        OPTIONS_BACK = Button(image=None, pos=(screen_width // 2, 460), 
                            text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")
        
        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()
        
        pygame.display.update()

# Define the main menu
def main_menu():
    while True:
        # Load and scale the background image
        bg_image = pygame.image.load("GB.jpeg")
        bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
        SCREEN.blit(bg_image, (0, 0))
        
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        
        MENU_TEXT = get_font(100).render("RUN AND COLLECT", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(screen_width // 2, 100))
        
        PLAY_BUTTON = Button(image=pygame.image.load("play.jpeg"), pos=(screen_width // 2, 250), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        OPTIONS_BUTTON = Button(image=pygame.image.load("options.jpeg"), pos=(screen_width // 2, 400), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        QUIT_BUTTON = Button(image=pygame.image.load("quit.jpeg"), pos=(screen_width // 2, 550), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        SCREEN.blit(MENU_TEXT, MENU_RECT)
        
        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()
        
        pygame.display.update()

# Set up game clock
clock = pygame.time.Clock()

# Start the main menu
main_menu()

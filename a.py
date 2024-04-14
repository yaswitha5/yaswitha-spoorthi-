import pygame
import random

# Initialize Pygame
pygame.init()

# Screen settings
screen_width = 1000
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Run and Collect")

# Load and resize background images to match the screen size
background1_image = pygame.image.load("background1.jpeg")
background1_image = pygame.transform.scale(background1_image, (screen_width, screen_height))

background2_image = pygame.image.load("background2.jpeg")
background2_image = pygame.transform.scale(background2_image, (screen_width, screen_height))

# Load images and resize them
player_image = pygame.image.load("player.png")
player_image = pygame.transform.scale(player_image, (50, 150))

person_image = pygame.image.load("person.png")
person_image = pygame.transform.scale(person_image, (50, 150))

# Load item images and resize them
item_images = [
    pygame.image.load("apple.png"),
    pygame.image.load("banana.png"),
    pygame.image.load("orange.png"),
    pygame.image.load("cherry.png"),
]
item_images = [pygame.transform.scale(img, (30, 30)) for img in item_images]

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BASE_COLOR = (0, 128, 0)  # Color for the base (ground)

# Define fonts
font = pygame.font.Font(None, 36)
button_font = pygame.font.Font(None, 48)

# Define the base height
base_height = 100  # Height of the base (ground)

# Define the maximum jump height
MAX_JUMP_HEIGHT = 2  # Number of times the player can jump

# Define Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x = 50  # Starting x position
        self.rect.y = screen_height - self.rect.height - base_height  # Starting y position
        self.jump_power = 15  # Initial jump power
        self.gravity = 1  # Gravity effect on player
        self.velocity_y = 0  # Vertical velocity for player movement
        self.jump_count = 0  # Track the number of jumps performed
        self.collected_items = []  # List to keep track of collected items
        self.humanity_score = 0  # Humanity score for the player

    def update(self):
        # Apply gravity
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Check for landing on the ground
        if self.rect.y >= screen_height - self.rect.height - base_height:
            self.rect.y = screen_height - self.rect.height - base_height
            self.velocity_y = 0
            self.jump_count = 0  # Reset jump count when on the ground

        # Handle jumping
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Allow double jump (up to MAX_JUMP_HEIGHT jumps)
            if self.jump_count < MAX_JUMP_HEIGHT:
                self.velocity_y = -self.jump_power
                self.jump_count += 1
        
        # Handle stopping (player stops when the 's' key is pressed)
        if keys[pygame.K_s]:
            self.velocity_y = 0  # Stop the player if 's' key is pressed

    def give_items(self, person):
        # Give collected items to the person and increase humanity score
        items_given = len(self.collected_items)
        if items_given > 0:
            self.humanity_score += items_given  # Increase humanity score
            self.collected_items = []  # Clear the list of collected items

# Define Person class
class Person(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = person_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(screen_width - 300, screen_width)  # Random x position in the right side
        self.rect.y = screen_height - base_height - self.rect.height  # Make the person stand on the ground
        self.speed = 2  # Speed of the person moving towards the player

    def update(self, player):
        # Move towards the player if they are on the ground
        if player.rect.y == screen_height - player.rect.height - base_height:
            if self.rect.x > player.rect.x:
                self.rect.x -= self.speed  # Move left towards the player

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

# Create groups
all_sprites = pygame.sprite.Group()
item_group = pygame.sprite.Group()
person_group = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Game state flags
game_started = False

# Set up game clock
clock = pygame.time.Clock()

# Timer for background change
time_elapsed = 0

# Variable to keep track of the current background
current_background = 1

# Timer for spawning items
item_spawn_timer = 0

# Timer for spawning persons
person_spawn_timer = 0

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
        
    else:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update player
        player.update()

        # Update persons and items
        person_group.update(player)
        item_group.update()
        
        # Spawn new item periodically
        item_spawn_timer += clock.get_time()
        if item_spawn_timer >= 2000:  # Every 2 seconds
            item = Item()
            all_sprites.add(item)
            item_group.add(item)
            item_spawn_timer = 0
        
        # Spawn new person periodically
        person_spawn_timer += clock.get_time()
        if person_spawn_timer >= 10000:  # Every 10 seconds
            person = Person()
            all_sprites.add(person)
            person_group.add(person)
            person_spawn_timer = 0
        
        # Check for collisions between player and items
        collisions = pygame.sprite.spritecollide(player, item_group, True)
        if collisions:
            # Add collected items to player's collected_items list
            player.collected_items.extend(collisions)
        
        # Check for collisions between player and person
        person_collisions = pygame.sprite.spritecollide(player, person_group, False)
        if person_collisions:
            # Stop the player and give items to the person
            player.velocity_y = 0  # Stop the player
            for person in person_collisions:
                player.give_items(person)  # Give items to the person

        # Draw the current background
        if current_background == 1:
            screen.blit(background1_image, (0, 0))
        else:
            screen.blit(background2_image, (0, 0))
        
        # Draw all sprites
        all_sprites.draw(screen)
        
        # Draw the base (ground) as a green rectangle at the bottom of the screen
        pygame.draw.rect(screen, BASE_COLOR, (0, screen_height - base_height, screen_width, base_height))
        
        # Display collected items count on the left side of the screen
        collected_text = font.render(f"Collected: {len(player.collected_items)}", True, BLACK)
        screen.blit(collected_text, (10, 10))
        
        # Display humanity score on the right side of the screen
        humanity_text = font.render(f"Humanity Score: {player.humanity_score}", True, BLACK)
        screen.blit(humanity_text, (screen_width - humanity_text.get_width() - 10, 10))
        
        # Update display
        pygame.display.flip()
        
        # Set frame rate
        clock.tick(60)

        # Update the timer and switch background every 2 minutes (120 seconds)
        time_elapsed += clock.get_time() / 1000  # Update time elapsed in seconds
        if time_elapsed >= 120:
            # Switch background
            current_background = 2 if current_background == 1 else 1
            time_elapsed = 0
        
# Quit Pygame
pygame.quit()

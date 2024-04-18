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

item_images = [pygame.image.load("apple.png"), pygame.image.load("banana.png"), pygame.image.load("orange.png"), pygame.image.load("cherry.png")]
item_images = [pygame.transform.scale(img, (30, 30)) for img in item_images]

box_closed_image = pygame.image.load("box_closed.png")
box_opened_image = pygame.image.load("box_opened.png")
box_closed_image = pygame.transform.scale(box_closed_image, (50, 50))
box_opened_image = pygame.transform.scale(box_opened_image, (50, 50))

# Load obstacle images and resize them
obstacle_images = [pygame.image.load("obstacle1.png"), pygame.image.load("obstacle2.png"), pygame.image.load("obstacle3.png"), pygame.image.load("obstacle4.png") ]
obstacle_images = [pygame.transform.scale(img, (50, 50)) for img in obstacle_images]


# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BASE_COLOR = (0, 128, 0)

# Define fonts
def get_font(size):
    return pygame.font.Font("font.ttf", size)

font = get_font(36)
button_font = get_font(48)

# Game settings and state variables
base_height = 75 # Height of the base (ground)
background_x = 0
background_speed = 3
MAX_JUMP_HEIGHT = 1

# Sound and music settings
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

# Define Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, run_sprite_sheet, jump_sprite_sheet):
        super().__init__()
        # Load sprite sheets and resize them
        run_sprite_sheet = pygame.image.load(run_sprite_sheet)
        jump_sprite_sheet = pygame.image.load(jump_sprite_sheet)
        
        # Resize sprite sheets for larger player sprite
        new_width = 1 * run_sprite_sheet.get_width()  # Scale the width by 2 (change this as needed)
        new_height = 1 * run_sprite_sheet.get_height()  # Scale the height by 2 (change this as needed)
        run_sprite_sheet = pygame.transform.scale(run_sprite_sheet, (new_width, new_height))
        jump_sprite_sheet = pygame.transform.scale(jump_sprite_sheet, (new_width, new_height))
        
        # Load animation frames
        self.run_frames = self.load_animation_frames(run_sprite_sheet, 8)
        self.jump_frames = self.load_animation_frames(jump_sprite_sheet, 11)
        
        self.current_frames = self.run_frames
        self.image_index = 0
        self.image = self.current_frames[self.image_index]
        self.rect = self.image.get_rect()
        
        # Set starting position (adjust as needed)
        self.rect.x = screen_width // 2 - self.rect.width // 2
        self.rect.y = screen_height - self.rect.height - base_height
        
        # Other player attributes...
        self.jump_power = 30  # Adjust as needed
        self.gravity = 1  # Adjust as needed
        self.velocity_y = 0
        self.jump_count = 0
        self.is_stopped = False

    def load_animation_frames(self, sprite_sheet, num_frames):
        # Define the dimensions of each frame in the sprite sheet
        frame_width = sprite_sheet.get_width() // num_frames
        frame_height = sprite_sheet.get_height()
        frames = []
        # Extract individual frames from sprite sheet
        for i in range(num_frames):
            frame = sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            frames.append(frame)
        return frames

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
                    # Set jumping animation
                    self.current_frames = self.jump_frames
                    # Reset animation index
                    self.image_index = 0

        # Handle running animation
        if not self.is_stopped:
            self.current_frames = self.run_frames

        # Update animation frames
        self.play_animation()

    def play_animation(self):
        # Implement logic to play animation by cycling through frames
        animation_speed = 0.1  # Adjust this value to control animation speed (in seconds)

        # Calculate frame index based on animation speed and current time
        frame_index = int((pygame.time.get_ticks() // (animation_speed * 1000)) % len(self.current_frames))

        # Update self.image_index to change frames
        self.image_index = frame_index
        self.image = self.current_frames[self.image_index]

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
        self.closed_image = box_closed_image
        self.opened_image = box_opened_image
        self.image = self.closed_image
        self.rect = self.image.get_rect()
        self.rect.x = screen_width  # Starting x position
        self.rect.y = screen_height - base_height - self.rect.height  # Place box on the ground
        self.opened = False  # Flag to track whether the box is opened or closed

    def update(self):
        # Move box to the left
        self.rect.x -= 5
        
        # Remove box if it goes off screen
        if self.rect.x < -self.rect.width:
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        # Choose a random obstacle image from the list of obstacle images
        self.image = random.choice(obstacle_images)
        self.rect = self.image.get_rect()
        
        # Starting x position
        self.rect.x = screen_width
        
        # Calculate y-coordinate to be just above the ground
        # The y-coordinate should be such that the obstacle sits just above the base height
        self.rect.y = screen_height - base_height - self.rect.height
        
        self.player = player  # Reference to the player object

    def update(self):
        # Move the obstacle to the left
        self.rect.x -= 5
        
        # Check for collision with the player
        if self.rect.colliderect(self.player.rect):
            # End the game immediately if collision occurs
            global game_over
            game_over = True
        
        # Remove the obstacle if it goes off-screen
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
player = Player("run.png", "jump.png")
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

def is_overlapping(sprite, groups):
    for group in groups:
        if pygame.sprite.spritecollideany(sprite, group):
            return True
    return False

# Define play function
def play():
    global item_spawn_timer, box_spawn_timer, obstacle_spawn_timer, donations_made, missed_donations, game_over
    
    # Reset game state flags and variables
    game_over = False
    donations_made = 0
    missed_donations = 0
    player.collected_items = []
    
    # Variable to track the current box the player has encountered
    current_box = None
    
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
                
                # Only allow the box to be opened if the player has collected items
                if player_box_collisions and len(player.collected_items) > 0:
                    # Stop the player and donate collected items
                    player.is_stopped = True
                    donations_made += 1
                    player.collected_items = []  # Clear the list of collected items
                    
                    # Open the box
                    opened_box = player_box_collisions[0]
                    opened_box.opened = True
                    opened_box.image = opened_box.opened_image
                    
                    # Reset the current box since it's opened
                    current_box = None
            
            # Reset stop flag after handling events
            player.is_stopped = False
        
        # Check if the player passes the current box
        if current_box and player.rect.right > current_box.rect.right:
            # Check if the box was not opened
            if not current_box.opened:
                # Increment missed donations if the box was not opened
                missed_donations += 1
            
            # Reset the current box to avoid counting the same box multiple times
            current_box = None
        
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
            # Check if the item overlaps with existing boxes or obstacles
            if not is_overlapping(item, [box_group, obstacle_group]):
                all_sprites.add(item)
                item_group.add(item)
            else:
                # If the item overlaps, skip adding it to the game and destroy it
                item.kill()
            item_spawn_timer = 0
        
        # Box spawn
        box_spawn_timer += clock.get_time()
        if box_spawn_timer >= spawn_intervals['box']:
            box = Box()
            # Check if the box overlaps with existing items or obstacles
            if not is_overlapping(box, [item_group, obstacle_group]):
                all_sprites.add(box)
                box_group.add(box)
                
                # Set the current_box variable to track the newly spawned box
                current_box = box
            else:
                # If the box overlaps, skip adding it to the game and destroy it
                box.kill()
            box_spawn_timer = 0
        
        # Obstacle spawn
        obstacle_spawn_timer += clock.get_time()
        if obstacle_spawn_timer >= spawn_intervals['obstacle']:
            obstacle = Obstacle(player)
            # Check if the obstacle overlaps with existing items or boxes
            if not is_overlapping(obstacle, [item_group, box_group]):
                all_sprites.add(obstacle)
                obstacle_group.add(obstacle)
            else:
                # If the obstacle overlaps, skip adding it to the game and destroy it
                obstacle.kill()
            obstacle_spawn_timer = 0

        # Check if the number of missed boxes has reached 3
        if missed_donations >= 3:
            game_over = True    
        
        # Check for player-obstacle collisions and end the game if it happens
        player_obstacle_collisions = pygame.sprite.spritecollide(player, obstacle_group, False)
        if player_obstacle_collisions:
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

def game_over_screen():
    # Load and scale the background image
    bg_image = pygame.image.load("background1.png")  # Replace "game_over_background.jpeg" with your image file
    bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))

    # Create a button to return to the main menu
    menu_button = Button(
        image=None,  # You can use a specific image for the button if you want
        pos=(screen_width // 2, 600),
        text_input="MENU",
        font=get_font(48),  # Use your desired font size
        base_color="Black",
        hovering_color="Green"
    )

    while True:
        # Draw the background image on the screen
        SCREEN.blit(bg_image, (0, 0))

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

        # Draw the menu button and check for hover interactions
        menu_button.changeColor(pygame.mouse.get_pos())
        menu_button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the menu button was clicked
                if menu_button.checkForInput(pygame.mouse.get_pos()):
                    # If the button is clicked, return to the main menu
                    main_menu()
                    return  # Return to exit the game over loop

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

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

# Start the main menu
main_menu()
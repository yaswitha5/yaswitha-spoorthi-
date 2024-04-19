import pygame
import sys
import random
from button import Button

# Initialize Pygame and the mixer module for sound
pygame.init()
pygame.mixer.init()

base_height = 100

# Screen settings
screen_width, screen_height = 1280, 720
SCREEN = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("collect and donation")

# Load images and resize them
background_image = pygame.image.load("background.jpeg")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

item_images = [pygame.image.load("apple.png"), pygame.image.load("banana.png"), pygame.image.load("coins.png"), pygame.image.load("cherry.png")]
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

# Define fonts
def get_font(size):
    return pygame.font.Font("font.ttf", size)

font = get_font(36)
button_font = get_font(48)

# Game settings and state variables
background_x = 0
background_speed = 3
MAX_JUMP_HEIGHT = 1

# Sound and music settings
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

# Load the sound file when the player is out
player_out_sound = pygame.mixer.Sound("background_music.mp3")

# Set the volume for the sound (optional)
player_out_sound.set_volume(0.5)  # Adjust volume as needed


# Global variable to track the state of the music
music_playing = True

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
        #self.rect.y = screen_height - self.rect.height - base_height
        self.rect.y = 0
        
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

def is_overlapping(sprite, groups):
    for group in groups:
        if pygame.sprite.spritecollideany(sprite, group):
            return True
    return False

def reset_game():
    global player, all_sprites, item_group, box_group, obstacle_group, game_over, donations_made

    # Reset player position and state
    player.rect.x = screen_width // 2 - player.rect.width // 2
    player.rect.y = screen_height - player.rect.height
    player.jump_count = 0
    player.velocity_y = 0
    player.is_stopped = False
    player.current_frames = player.run_frames
    player.image_index = 0
    player.image = player.current_frames[player.image_index]
    player.collected_items = []

    # Reset game state flags and variables
    game_over = False
    donations_made = 0
    item_spawn_timer = 0
    box_spawn_timer = 0
    obstacle_spawn_timer = 0

    # Clear existing sprites and create new sprite groups
    all_sprites.empty()
    item_group.empty()
    box_group.empty()
    obstacle_group.empty()

    # Re-add the player sprite
    all_sprites.add(player)

    # Start a new game
    play()   

# Define play function
def play():
    global item_spawn_timer, box_spawn_timer, obstacle_spawn_timer, donations_made, game_over, donations_score

    clock = pygame.time.Clock()
    
    # Check the state of the music before starting the game
    if music_playing:
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)
    else:
        pygame.mixer.music.pause()
    
    # Reset game state flags and variables
    game_over = False
    donations_made = 0
    donations_score = 0
    player.collected_items = []
    
    # Variable to track the current box the player has encountered
    current_box = None

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
                    donations_score += len(player.collected_items)
                    player.collected_items = []  # Clear the list of collected items
                    
                    # Open the box
                    opened_box = player_box_collisions[0]
                    opened_box.opened = True
                    opened_box.image = opened_box.opened_image
                    
                    # Reset the current box since it's opened
                    current_box = None
            
            # Reset stop flag after handling events
            player.is_stopped = False
        

        # Update player
        player.update()

        # Update items, boxes, and obstacles
        item_group.update()
        box_group.update()
        obstacle_group.update()

        # Spawn new items, boxes, and obstacles at specified intervals
        spawn_intervals = {
            'item': 2000,  # Spawn an item every 2 seconds
            'box': 6000,   # Spawn a box every 6 seconds
            'obstacle': 4000  # Spawn an obstacle every 4 seconds
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

        # Check if the number of missed donations has reached 3
           

        # Check for player-obstacle collisions and end the game if it happens
        player_obstacle_collisions = pygame.sprite.spritecollide(player, obstacle_group, False)
        if player_obstacle_collisions:
            # Play the player out sound
            player_out_sound.play()
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

        # Display collected items count on the left side of the screen
        collected_text = font.render(f"Collected: {len(player.collected_items)}", True, BLACK)
        SCREEN.blit(collected_text, (10, 10))

        # Display the number of donations made on the right side of the screen
        donations_made_text = font.render(f"Donations Made: {donations_made}", True, BLACK)
        donations_score_text = font.render(f"Donations Score: {donations_score}", True, BLACK)

        # Display Donations Made at the top right corner
        SCREEN.blit(donations_made_text, (screen_width - donations_made_text.get_width() - 10, 10))

        # Display Donations Score slightly below Donations Made
        SCREEN.blit(donations_score_text, (screen_width - donations_score_text.get_width() - 10, 50))

        # Update display
        pygame.display.flip()

        # Set frame rate
        clock.tick(60)

    # If game is over, display game over screen
    pygame.mixer.music.stop()
    game_over_screen()

def game_over_screen():
    # Load and scale the background image
    bg_image = pygame.image.load("GB.jpeg")
    bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))

    # Create buttons for returning to the menu and quitting the game
    restart_button = Button(
        image=pygame.image.load("text_box.jpeg"),
        pos=(screen_width // 2, 325),
        text_input="PLAY AGAIN",
        font=get_font(48),
        base_color="White",
        hovering_color="Green"
    )

    # Display the score (number of donations made) as text
    score_text = font.render(f"Donations Made: {donations_made}", True, BLACK)
    score_rect = score_text.get_rect(center=(screen_width // 2, 200))

    quotation_text = font.render(f"Happiness doesn't result from what we get, but from what we give", True, BLACK)
    quotation_rect = quotation_text.get_rect(center=(screen_width // 2, 75))

    # Create a quit button
    quit_button = Button(image=pygame.image.load("text_box.jpeg"),pos=(screen_width // 2, 500),text_input="QUIT",
                            font=get_font(48),base_color="White",hovering_color="Green")

    while True:
        # Draw the background image on the screen
        SCREEN.blit(bg_image, (0, 0))

        # Display the score (number of donations made)
        SCREEN.blit(score_text, score_rect)

        SCREEN.blit(quotation_text, quotation_rect)

        # Draw the buttons and check for hover interactions
        restart_button.changeColor(pygame.mouse.get_pos())
        restart_button.update(SCREEN)

        quit_button.changeColor(pygame.mouse.get_pos())
        quit_button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the menu button was clicked
                if restart_button.checkForInput(pygame.mouse.get_pos()):
                    reset_game()  # Reset the game and start a new game
                    return  # Return from the game over screen to allow the player to start a new game
                # Check if the quit button was clicked
                elif quit_button.checkForInput(pygame.mouse.get_pos()):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

# Define options screen
def options():
    global music_playing  # Reference the global music_playing variable
    
    # Load the background image and scale it to fit the screen
    bg_image = pygame.image.load("background.jpg")
    bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
    
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        
        # Display the background image
        SCREEN.blit(bg_image, (0, 0))

        # Define the back button
        OPTIONS_BACK = Button(image=None, pos=(screen_width // 2, 450), 
                              text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")

        # Define the music toggle button
        if music_playing:
            music_button_text = "MUSIC: ON"
        else:
            music_button_text = "MUSIC: OFF"
        MUSIC_BUTTON = Button(image=None, pos=(screen_width // 2, 300),
                              text_input=music_button_text, font=get_font(75), base_color="Black", hovering_color="Green")

        # Update buttons and check for hover interactions
        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        MUSIC_BUTTON.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)
        MUSIC_BUTTON.update(SCREEN)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()
                elif MUSIC_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    # Toggle the music state
                    music_playing = not music_playing
                    if music_playing:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
        
        pygame.display.update()

def help_screen():
    # Load and scale the background image
    bg_image = pygame.image.load("background.jpg")
    bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))

    # Define the instructions text (update as needed)
    instructions_text = (
        "Game Instructions:\n\n"
        "1. Press SPACE BAR to jump.\n"
        "2. Collect items by running into them.\n"
        "3. Press S  to donate near a box.\n"
        "4. If there are no collected items then you cannot donate.\n"
        "4. Avoid obstacles to stay alive.\n"
        "5. Keep an eye on the bottom of the screen for incoming obstacles.\n"
        "6. Reach the highest score possible!"
    )

    # Create a font for the instructions text
    instructions_font = get_font(36)

    # Create a list to store rendered text lines
    rendered_text_lines = []
    # Split the instructions text into lines and render each line
    for line in instructions_text.split('\n'):
        text_surface = instructions_font.render(line, True, BLACK)
        rendered_text_lines.append(text_surface)

    # Define the back button
    back_button = Button(
        image=None,
        pos=(screen_width // 2, 600),
        text_input="BACK",
        font=get_font(75),
        base_color="Black",
        hovering_color="Green"
    )

    while True:
        # Display the background image
        SCREEN.blit(bg_image, (0, 0))

        # Display the instructions text
        y_offset = 150  # Initial vertical offset for displaying the text lines
        for line in rendered_text_lines:
            SCREEN.blit(line, (50, y_offset))
            y_offset += line.get_height() + 10  # Adjust the vertical position for each line

        # Update the back button and handle hover interactions
        back_button.changeColor(pygame.mouse.get_pos())
        back_button.update(SCREEN)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.checkForInput(pygame.mouse.get_pos()):
                    # Return to the main menu when the back button is clicked
                    main_menu()
                    return
        
        pygame.display.flip()

# Define the main menu
def main_menu():
    while True:
        # Load and scale the background image
        bg_image = pygame.image.load("GB.jpeg")
        bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
        SCREEN.blit(bg_image, (0, 0))
        
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        
        MENU_TEXT = get_font(100).render("COLLECT AND DONATE", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(screen_width // 2, 100))
        
        PLAY_BUTTON = Button(image=pygame.image.load("text_box.jpeg"), pos=(screen_width // 2, 225), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        OPTIONS_BUTTON = Button(image=pygame.image.load("text_box.jpeg"), pos=(screen_width // 2, 350), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        HELP_BUTTON = Button(image=pygame.image.load("text_box.jpeg"),pos=(screen_width // 2, 475),
                            text_input="HELP",font=get_font(75),base_color="#d7fcd4",hovering_color="White")

        QUIT_BUTTON = Button(image=pygame.image.load("text_box.jpeg"), pos=(screen_width // 2, 600), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        SCREEN.blit(MENU_TEXT, MENU_RECT)
        
        for button in [PLAY_BUTTON, OPTIONS_BUTTON, HELP_BUTTON, QUIT_BUTTON]:
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
                if HELP_BUTTON.checkForInput(MENU_MOUSE_POS):
                    help_screen()  # Call the help screen function
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()
                    
        pygame.display.update()


# Start the main menu
main_menu()  
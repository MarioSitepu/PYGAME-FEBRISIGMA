import pygame
from settings import *
from timer import Timer
import json
import os
from datetime import datetime  # Add this import

class PauseMenu:
    def __init__(self, player, toggle_menu):
        # general setup
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 40)
        
        # Add timer for input control
        self.timer = Timer(200)
        
        # Create dark overlay surface
        self.dark_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.dark_surf.fill((0,0,0))
        self.dark_surf.set_alpha(128)  # 128 for 50% transparency
    
        # Button background
        self.button = pygame.image.load('../graphics/menu/pausemenu/button.png').convert_alpha()
        
        # Create darker version of button for selected state
        self.button_selected = self.button.copy()
        dark_surface = pygame.Surface(self.button.get_size(), flags=pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, 100))  # Semi-transparent black
        self.button_selected.blit(dark_surface, (0, 0))
        
        # Menu states - replace 'Main Menu' with 'Quit Game'
        self.menu_states = {
            'main': ['Continue', 'Options', 'Save Game', 'Load Game', 'Quit Game'],
            'save': ['Save 1', 'Save 2', 'Save 3', 'Save 4', 'Back'],
            'load': ['Save 1', 'Save 2', 'Save 3', 'Save 4', 'Back']  # Add load state
        }
        self.current_state = 'main'
        self.index = 0
        
        # Layout
        self.padding = 20
        self.button_height = 80
        self.input_cooldown = 200  # milliseconds
        self.last_input_time = 0
        
        # Add save directory path
        self.save_dir = '../savefile/'
        # Create directory if it doesn't exist
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        # Add save dates dictionary
        self.save_dates = {}
        self.load_save_dates()
        
        # Add this line to track pause menu state
        self.is_open = False  

    def load_save_dates(self):
        """Load all existing save dates"""
        self.save_dates = {}
        for slot in range(1, 5):
            filename = os.path.join(self.save_dir, f'save{slot}.txt')
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        save_data = json.load(f)
                        self.save_dates[slot] = save_data.get('save_date', 'No date')
                except:
                    self.save_dates[slot] = 'Error'

    def get_save_data(self):
        return {
            'money': self.player.money,
            'item_inventory': self.player.item_inventory,
            'seed_inventory': self.player.seed_inventory,
            'position': [self.player.pos.x, self.player.pos.y],
            'save_date': datetime.now().strftime("%Y-%m-%d %H:%M")  # Add save date
        }

    def save_game(self, save_slot):
        save_data = self.get_save_data()
        filename = os.path.join(self.save_dir, f'save{save_slot}.txt')
        
        try:
            with open(filename, 'w') as f:
                json.dump(save_data, f)
            self.save_dates[save_slot] = save_data['save_date']  # Update save dates
            print(f"Game saved successfully to {filename}")
        except Exception as e:
            print(f"Error saving game: {e}")
            
    def load_game(self, save_slot):
        filename = os.path.join(self.save_dir, f'save{save_slot}.txt')
        
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    save_data = json.load(f)
                
                # Load the saved data
                self.player.money = save_data['money']
                self.player.item_inventory = save_data['item_inventory']
                self.player.seed_inventory = save_data['seed_inventory']
                self.player.pos.x = save_data['position'][0]
                self.player.pos.y = save_data['position'][1]
                
                print(f"Game loaded successfully from {filename}")
            else:
                print(f"No save file found at {filename}")
        except Exception as e:
            print(f"Error loading game: {e}")

    def input(self):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        current_options = self.menu_states[self.current_state]

        if current_time - self.last_input_time > self.input_cooldown:
            # Add UP/DOWN navigation
            if keys[pygame.K_UP]:
                self.index = (self.index - 1) if self.index > 0 else len(current_options) - 1
                self.last_input_time = current_time

            if keys[pygame.K_DOWN]:
                self.index = (self.index + 1) if self.index < len(current_options) - 1 else 0
                self.last_input_time = current_time

            # Add escape key to return to main menu or close
            if keys[pygame.K_ESCAPE]:
                if self.current_state != 'main':
                    self.current_state = 'main'
                    self.index = 0
                else:
                    self.toggle_menu()
                self.last_input_time = current_time

            if keys[pygame.K_RETURN]:
                self.last_input_time = current_time
                if self.current_state == 'main':
                    if current_options[self.index] == 'Continue':
                        self.toggle_menu()
                    elif current_options[self.index] == 'Save Game':
                        self.current_state = 'save'
                        self.index = 0
                    elif current_options[self.index] == 'Load Game':
                        self.current_state = 'load'
                        self.index = 0
                    elif current_options[self.index] == 'Quit Game':
                        pygame.quit()
                        import sys
                        sys.exit()
            
                elif self.current_state == 'save':
                    if current_options[self.index] == 'Back':
                        self.current_state = 'main'
                        self.index = 0
                    else:
                        save_slot = self.index + 1
                        self.save_game(save_slot)
                        self.current_state = 'main'
                        self.index = 0

                elif self.current_state == 'load':
                    if current_options[self.index] == 'Back':
                        self.current_state = 'main'
                        self.index = 0
                    else:
                        save_slot = self.index + 1
                        if os.path.exists(os.path.join(self.save_dir, f'save{save_slot}.txt')):
                            self.load_game(save_slot)
                            self.toggle_menu()
                            return True

    def display(self):
        # Draw dark overlay
        self.display_surface.blit(self.dark_surf, (0,0))
        
        current_options = self.menu_states[self.current_state]
        
        # Calculate total height and menu top position
        total_height = (self.button_height + self.padding) * len(current_options)
        menu_top = SCREEN_HEIGHT/2 - total_height/2
        
        # Draw title
        title_text = 'Pause Menu'
        if self.current_state == 'save':
            title_text = 'Save Game'
        elif self.current_state == 'load':
            title_text = 'Load Game'
            
        title = self.font.render(title_text, False, 'white')
        title_rect = title.get_rect(midtop = (SCREEN_WIDTH/2, menu_top - 60))
        self.display_surface.blit(title, title_rect)
        
        # Draw buttons
        for i, option in enumerate(current_options):
            button_y = menu_top + (self.button_height + self.padding) * i
            button_rect = pygame.Rect(SCREEN_WIDTH/2 - 150, button_y, 300, self.button_height)
            
            # Draw button background
            button_img = self.button_selected if i == self.index else self.button
            scaled_button = pygame.transform.scale(button_img, (300, self.button_height))
            self.display_surface.blit(scaled_button, button_rect)
            
            # Draw text
            if option.startswith('Save ') and option != 'Save Game' and self.current_state in ['save', 'load']:
                slot_num = int(option.split()[1])
                if slot_num in self.save_dates:
                    # Draw save slot text
                    text_surf = self.font.render(f"Slot {slot_num}", False, 'white')
                    text_rect = text_surf.get_rect(midleft=(button_rect.left + 20, button_rect.centery))
                    self.display_surface.blit(text_surf, text_rect)
                    
                    # Draw date with smaller font
                    date_font = pygame.font.Font('../font/LycheeSoda.ttf', 20)
                    date_surf = date_font.render(self.save_dates[slot_num], False, 'white')
                    date_rect = date_surf.get_rect(midright=(button_rect.right - 20, button_rect.centery))
                    self.display_surface.blit(date_surf, date_rect)
                else:
                    # Empty save slot
                    text_surf = self.font.render(f"Empty Slot {slot_num}", False, 'white')
                    text_rect = text_surf.get_rect(center=button_rect.center)
                    self.display_surface.blit(text_surf, text_rect)
            else:
                # Regular menu option
                text_surf = self.font.render(option, False, 'white')
                text_rect = text_surf.get_rect(center=button_rect.center)
                self.display_surface.blit(text_surf, text_rect)
            
    def update(self):
        self.input()
        self.display()

    def show(self):
        """Show pause menu"""
        self.is_open = True
        self.update()

    def toggle_state(self):
        """Toggle pause menu state"""
        self.is_open = not self.is_open
        if self.is_open:
            self.show()
        return True

    def get_state(self):
        """Get current menu state"""
        return self.is_open
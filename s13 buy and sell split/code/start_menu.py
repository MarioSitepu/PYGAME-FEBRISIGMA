import pygame
from settings import *
from timer import Timer
import json
import os
from datetime import datetime

class StartMenu:
    def __init__(self):
        # General setup
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 40)
        
        # Add timer for input control
        self.timer = Timer(200)
        
        # Background and buttons
        self.background = pygame.image.load('../graphics/menu/startmenu/bg.png').convert_alpha()
        self.button = pygame.image.load('../graphics/menu/startmenu/button.png').convert_alpha()
        
        # Create darker version of button for selected state
        self.button_selected = self.button.copy()
        dark_surface = pygame.Surface(self.button.get_size(), flags=pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, 100))  # Semi-transparent black
        self.button_selected.blit(dark_surface, (0, 0))
        
        # Menu states
        self.menu_states = {
            'main': ['New Game', 'Continue', 'Options', 'Quit Game'],
            'continue': ['Save 1', 'Save 2', 'Save 3', 'Save 4', 'Back']
        }
        self.current_state = 'main'
        self.index = 0
        
        # Layout
        self.padding = 20
        self.button_height = 80
        self.input_cooldown = 200
        self.last_input_time = 0
        
        # Save directory
        self.save_dir = '../savefile/'
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
        # Save dates
        self.save_dates = {}
        self.load_save_dates()
        
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
                    
    def load_game(self, save_slot):
        filename = os.path.join(self.save_dir, f'save{save_slot}.txt')
        
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    save_data = json.load(f)
                return save_data
            else:
                print(f"No save file found at {filename}")
                return None
        except Exception as e:
            print(f"Error loading game: {e}")
            return None

    def input(self):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        current_options = self.menu_states[self.current_state]

        if current_time - self.last_input_time > self.input_cooldown:
            if keys[pygame.K_ESCAPE] and self.current_state == 'continue':
                self.current_state = 'main'
                self.index = 0
                self.last_input_time = current_time
            
            if keys[pygame.K_UP]:
                self.index = (self.index - 1) if self.index > 0 else len(current_options) - 1
                self.last_input_time = current_time

            if keys[pygame.K_DOWN]:
                self.index = (self.index + 1) if self.index < len(current_options) - 1 else 0
                self.last_input_time = current_time
                
            if keys[pygame.K_RETURN]:
                self.last_input_time = current_time
                selected_option = current_options[self.index]
                
                if self.current_state == 'main':
                    if selected_option == 'New Game':
                        return 'new_game'
                    elif selected_option == 'Continue':
                        self.current_state = 'continue'
                        self.index = 0
                    elif selected_option == 'Options':
                        pass  # Add options functionality
                    elif selected_option == 'Quit Game':
                        return 'quit'
                        
                elif self.current_state == 'continue':
                    if selected_option == 'Back':
                        self.current_state = 'main'
                        self.index = 0
                    else:
                        save_slot = self.index + 1
                        save_data = self.load_game(save_slot)
                        if save_data:
                            return ('load_game', save_data)
        return None

    def display(self):
        # Draw background
        scaled_bg = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display_surface.blit(scaled_bg, (0, 0))
        
        current_options = self.menu_states[self.current_state]
        
        # Calculate total height and menu top position
        total_height = (self.button_height + self.padding) * len(current_options)
        menu_top = SCREEN_HEIGHT/2 - total_height/2
        
        # Draw title
        title_text = ''
        if self.current_state == 'continue':
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
            if option.startswith('Save ') and self.current_state == 'continue':
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
        result = self.input()
        self.display()
        return result
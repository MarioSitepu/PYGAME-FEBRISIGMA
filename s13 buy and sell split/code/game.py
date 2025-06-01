import pygame
from settings import *
from level import Level
from start_menu import StartMenu

class Game:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.start_menu = StartMenu()
        self.level = None
        self.game_state = 'start_menu'
        self.inventory_open = False

    def handle_load_game(self, save_data):
        """Handle loading a saved game"""
        self.level = Level(self.toggle_inventory)
        
        # Load player data
        self.level.player.money = save_data['money']
        self.level.player.item_inventory = save_data['item_inventory']
        self.level.player.seed_inventory = save_data['seed_inventory']
        self.level.player.pos.x = save_data['position'][0]
        self.level.player.pos.y = save_data['position'][1]
        
        # Update player position
        self.level.player.rect.center = self.level.player.pos
        self.level.player.hitbox.center = self.level.player.rect.center

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.level:
                        if self.level.shop_active:
                            self.level.toggle_shop()
                            self.inventory_open = False
                        else:
                            self.level.toggle_pause()
                elif event.key == pygame.K_BACKSPACE:
                    if self.level and self.level.shop_active:
                        self.level.toggle_shop()
                        self.inventory_open = False
        return True

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            
            if not self.handle_input():
                break

            if self.game_state == 'start_menu':
                result = self.start_menu.update()
                if result == 'new_game':
                    self.level = Level(self.toggle_inventory)
                    self.game_state = 'running'
                elif result == 'quit':
                    break
                elif isinstance(result, tuple) and result[0] == 'load_game':
                    save_data = result[1]
                    if save_data:  # Only handle load if we have valid save data
                        self.handle_load_game(save_data)
                        self.game_state = 'running'

            elif self.game_state == 'running':
                if self.level:
                    result = self.level.run(dt)
                    if result == 'start_menu':  # Handle return to start menu
                        self.game_state = 'start_menu'
                        self.inventory_open = False  # Reset inventory state
                        self.level = None  # Clear current level
                        self.start_menu = StartMenu()  # Reset start menu

            pygame.display.update()

    def toggle_inventory(self):
        if self.level:
            self.inventory_open = not self.inventory_open
            if self.inventory_open:
                self.level.shop_menu.show()
            else:
                self.level.shop_menu.is_open = False
                self.level.shop_active = False
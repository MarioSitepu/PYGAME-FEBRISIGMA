import pygame
from settings import *
from timer import Timer

class ShopMenu:
    def __init__(self, player, toggle_menu):
        # general setup
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)

        # options
        self.width = 400
        self.space = 10
        self.padding = 10

        # Adjust indicator variables for lower positioning
        self.indicator_height = 40
        self.indicator_padding = 20  # Increased from 20 to 60 to move indicators lower
        self.indicator_width = 100

        # entries
        self.options = []
        self.menu_type = 'sell'
        self.sell_options = list(self.player.item_inventory.keys())
        self.buy_options = list(self.player.seed_inventory.keys())
        self.options = self.sell_options
        self.setup()  # Now setup() can access indicator variables

        # movement
        self.index = 0
        self.timer = Timer(200)

        # button background for items
        self.button_surf = pygame.image.load('../graphics/menu/shop/button.png').convert_alpha()
        self.button_surf_selected = self.button_surf.copy()
        self.button_surf_selected.fill((0,0,0,100), special_flags=pygame.BLEND_RGBA_MULT)

        # menu state
        self.is_open = False

        # dark overlay
        self.dark_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.dark_surf.fill((0,0,0))
        self.dark_surf.set_alpha(128)

        # Add display window variables
        self.max_display_items = 10
        self.scroll_start = 0
        self.visible_half = self.max_display_items // 2  # For centering

    def setup(self):
        self.text_surfs = []
        self.total_height = 0

        # Calculate max items between buy and sell menus
        max_items = max(len(self.buy_options), len(self.sell_options))
        
        # Calculate fixed height based on max items
        item_height = self.font.get_height() + (self.padding * 2)
        self.total_height = (item_height + self.space) * max_items
        
        # Add current menu items
        for item in self.options:
            text_surf = self.font.render(item, False, 'Black')
            self.text_surfs.append(text_surf)

        self.total_height += 60  # Money display height
        
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2, self.menu_top, self.width, self.total_height)

        # background - adjust height for indicators with more padding
        self.bg_rect = pygame.image.load('../graphics/menu/shop/shop.png').convert_alpha()
        extra_height = self.indicator_height + (self.indicator_padding * 2) + 80  # Increased from 40 to 80
        self.bg_rect = pygame.transform.scale(self.bg_rect, (self.width + 100, self.total_height + 160 + extra_height)) 
        self.bg_rect_rect = self.bg_rect.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

        # buy / sell text surfaces with larger font for indicators
        self.buy_text = self.font.render('BUY', False, 'Black')
        self.sell_text = self.font.render('SELL', False, 'Black')

    def switch_menu(self):
        """Switch between buy and sell menus"""
        if self.menu_type == 'sell':
            self.menu_type = 'buy'
            self.options = self.buy_options
        else:
            self.menu_type = 'sell'
            self.options = self.sell_options
        
        self.index = 0
        self.scroll_start = 0
        self.setup()

    def update_scroll(self):
        """Update scroll position only at edges"""
        # If we reached the bottom and there are more items
        if self.index >= self.scroll_start + self.max_display_items:
            self.scroll_start = self.index - self.max_display_items + 1
        # If we reached the top
        elif self.index < self.scroll_start:
            self.scroll_start = self.index
        # If we wrapped around to the end
        elif self.index == len(self.options) - 1:
            self.scroll_start = max(0, len(self.options) - self.max_display_items)
        # If we wrapped around to the start
        elif self.index == 0:
            self.scroll_start = 0

    def input(self):
        keys = pygame.key.get_pressed()
        self.timer.update()

        if not self.timer.active:
            if keys[pygame.K_BACKSPACE] or keys[pygame.K_ESCAPE]:  # Add escape key as alternative
                self.is_open = False
                self.toggle_menu()
                self.timer.activate()
                return 'close'

            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:  # Switch menus
                self.switch_menu()
                self.timer.activate()

            if keys[pygame.K_UP]:
                self.index = (self.index - 1) if self.index > 0 else len(self.options) - 1
                self.update_scroll()  # Center the selection
                self.timer.activate()

            if keys[pygame.K_DOWN]:
                self.index = (self.index + 1) if self.index < len(self.options) - 1 else 0
                self.update_scroll()  # Center the selection
                self.timer.activate()

            if keys[pygame.K_SPACE]:
                self.timer.activate()
                current_item = self.options[self.index]

                # sell
                if self.menu_type == 'sell':
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += SALE_PRICES[current_item]
                # buy
                else:
                    seed_price = PURCHASE_PRICES[current_item]
                    if self.player.money >= seed_price:
                        self.player.seed_inventory[current_item] += 1
                        self.player.money -= seed_price

    def show_entry(self, text_surf, amount, top, selected):
        # background with rounded corners
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))

        # Draw button background
        button_scaled = pygame.transform.scale(self.button_surf, (self.width, text_surf.get_height() + (self.padding * 2)))
        button_surface = pygame.Surface(button_scaled.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, (255,255,255,255), button_surface.get_rect(), 0, 10)
        button_scaled.blit(button_surface, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
        self.display_surface.blit(button_scaled, bg_rect)

        # Draw darker overlay for selected item
        if selected:
            button_selected = pygame.transform.scale(self.button_surf_selected, (self.width, text_surf.get_height() + (self.padding * 2)))
            button_selected.blit(button_surface, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
            self.display_surface.blit(button_selected, bg_rect)

        # text
        text_rect = text_surf.get_rect(midleft = (self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        # amount
        amount_surf = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surf.get_rect(midright = (self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)

        # selected options (buy/sell text)
        if selected:
            if self.menu_type == 'sell':
                pos_rect = self.sell_text.get_rect(midleft = (self.main_rect.left + 150, bg_rect.centery))
                self.display_surface.blit(self.sell_text, pos_rect)
            else:
                pos_rect = self.buy_text.get_rect(midleft = (self.main_rect.left + 150, bg_rect.centery))
                self.display_surface.blit(self.buy_text, pos_rect)

    def display_money(self):
        text_surf = self.font.render(f'${self.player.money}', False, 'Black')
        text_rect = text_surf.get_rect(midbottom = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))
        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10,10), 0, 4)
        self.display_surface.blit(text_surf, text_rect)

    def draw_menu_indicators(self):
        """Draw the buy/sell indicators at the top of the menu"""
        # Calculate positions relative to menu items
        item_height = self.text_surfs[0].get_height() + (self.padding * 2) + self.space
        total_menu_height = item_height * self.max_display_items
        menu_start_y = (SCREEN_HEIGHT/2 - total_menu_height/2) + 20
        
        # Position indicators 50 pixels above the first menu item
        indicator_y = menu_start_y - 70
        left_x = SCREEN_WIDTH / 2 - self.indicator_width - 10
        right_x = SCREEN_WIDTH / 2 + 10

        # Draw indicators
        for pos_x, text, is_active in [
            (left_x, self.buy_text, self.menu_type == 'buy'),
            (right_x, self.sell_text, self.menu_type == 'sell')
        ]:
            # Background rectangle
            indicator_rect = pygame.Rect(pos_x, indicator_y, self.indicator_width, self.indicator_height)
            
            # Draw button background
            button_surf = pygame.transform.scale(self.button_surf, (self.indicator_width, self.indicator_height))
            self.display_surface.blit(button_surf, indicator_rect)

            # If this is the active menu, draw darker overlay
            if is_active:
                button_selected = pygame.transform.scale(self.button_surf_selected, 
                    (self.indicator_width, self.indicator_height))
                self.display_surface.blit(button_selected, indicator_rect)

            # Draw text
            text_rect = text.get_rect(center=indicator_rect.center)
            self.display_surface.blit(text, text_rect)

    def update(self):
        if self.is_open:
            self.display_surface.blit(self.dark_surf, (0,0))
            self.display_surface.blit(self.bg_rect, self.bg_rect_rect)
            self.input()
            self.display_money()
            self.draw_menu_indicators()  # Add this line

            # Adjust menu title position to be even lower
            menu_title = self.font.render(f"{self.menu_type.upper()} MENU", False, 'Black')
            title_rect = menu_title.get_rect(midtop = (SCREEN_WIDTH / 2, 
                self.bg_rect_rect.top + self.indicator_height + (self.indicator_padding * 2) + 40))  # Increased from 20 to 40
            self.display_surface.blit(menu_title, title_rect)

            # Adjust menu start position to be slightly lower
            item_height = self.text_surfs[0].get_height() + (self.padding * 2) + self.space
            total_menu_height = item_height * self.max_display_items
            menu_start_y = (SCREEN_HEIGHT/2 - total_menu_height/2) + 20  # Added +20

            # Only display visible items within the scroll window
            display_range = range(self.scroll_start, min(self.scroll_start + self.max_display_items, len(self.text_surfs)))
            
            for i, text_index in enumerate(display_range):
                text_surf = self.text_surfs[text_index]
                top = menu_start_y + (i * item_height)
                
                # Get amount based on current menu type
                item_name = self.options[text_index]
                if self.menu_type == 'sell':
                    amount = self.player.item_inventory[item_name]
                else:
                    amount = self.player.seed_inventory[item_name]
                    
                self.show_entry(text_surf, amount, top, self.index == text_index)

            # Add scroll indicators if needed
            if self.scroll_start > 0:
                self.draw_scroll_indicator('up', menu_start_y)
            if self.scroll_start + self.max_display_items < len(self.options):
                self.draw_scroll_indicator('down', menu_start_y + total_menu_height)

    def draw_scroll_indicator(self, direction, position):
        """Draw scroll indicators when there are more items"""
        arrow_color = 'Black'
        arrow_size = 20
        arrow_padding = 10
        
        if direction == 'up':
            points = [(SCREEN_WIDTH/2 - arrow_size, position),
                     (SCREEN_WIDTH/2, position - arrow_padding),
                     (SCREEN_WIDTH/2 + arrow_size, position)]
        else:  # down
            points = [(SCREEN_WIDTH/2 - arrow_size, position),
                     (SCREEN_WIDTH/2, position + arrow_padding),
                     (SCREEN_WIDTH/2 + arrow_size, position)]
            
        pygame.draw.polygon(self.display_surface, arrow_color, points)

    def show(self):
        """Show the shop menu"""
        self.is_open = True
        self.timer.activate()  # Reset timer to prevent immediate closing
        self.update()  # Force an immediate update to show the menu

    def toggle_state(self):
        """Toggle shop menu state"""
        self.is_open = not self.is_open
        if self.is_open:
            self.show()
        return True

    def get_state(self):
        """Get current menu state"""
        return self.is_open
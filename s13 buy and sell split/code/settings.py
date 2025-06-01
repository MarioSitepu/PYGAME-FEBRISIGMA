from pygame.math import Vector2
# screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64
FPS = 60

# overlay positions 
OVERLAY_POSITIONS = {
	'tool' : (40, SCREEN_HEIGHT - 15), 
	'seed': (70, SCREEN_HEIGHT - 5)}

PLAYER_TOOL_OFFSET = {
	'left': Vector2(-50,40),
	'right': Vector2(50,40),
	'up': Vector2(0,-10),
	'down': Vector2(0,50)
}

LAYERS = {
	'water': 0,
	'ground': 1,
	'soil': 2,
	'soil water': 3,
	'rain floor': 4,
	'house bottom': 5,
	'ground plant': 6,
	'main': 7,
	'house top': 8,
	'fruit': 9,
	'rain drops': 10
}

APPLE_POS = {
	'Small': [(18,17), (30,37), (12,50), (30,45), (20,30), (30,10)],
	'Large': [(30,24), (60,65), (50,50), (16,40),(45,50), (42,70)]
}

GROW_SPEED = {
    'corn': 1,
    'tomato': 0.7,
    'potato': 0.6,
    'melon': 0.5,
    'pumpkin': 0.5,    # sama seperti melon
    'catplant': 0.3
}

SALE_PRICES = {
    'wood': 10,
    'apple': 5,
    'corn': 10,
    'tomato': 20,
    'potato': 30,
    'melon': 50,
    'pumpkin': 40,
    'catplant': 100
}

PURCHASE_PRICES = {
    'corn': 20,
    'tomato': 40,
    'potato': 50,
    'melon': 80,
    'pumpkin': 50,
    'catplant': 150
}
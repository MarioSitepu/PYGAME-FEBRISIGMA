import pygame
from settings import *
from game import Game

pygame.init()
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Nyan Village')

game = Game()
game.run()
pygame.quit()
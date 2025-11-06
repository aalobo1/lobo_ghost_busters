from pygame.sprite import Sprite
from settings import *
import pygame as pg
import time


# Object or class
# creates a class that reads the text file and converts it into a list.
class Map:
    def __init__(self, filename): # Initializing properties that can be inserted
        # creates empty list for map data
        self.data = []
        # open a specific file and close with  'with'
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())
        #properties of Map that allow us to define length and width 
        # also allows for 
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * 32
        self.height = self.tileheight * 32


# this creates a cooldown
class Cooldown:
    def __init__(self, time):
        self.start_time = 0
        self.time = time
    def start(self):
        self.start_time = pg.time.get_ticks()
    def ready(self):
        current_time = pg.time.get_ticks()
        if current_time - self.start_time >= self.time:
            return True
        return False

# loads an image file and creates an image surface for blitting or drawing images on the surface
# class Spritesheet:
#     def __init__(self, filename):
#         self.spritesheet = pg.image.load(filename).convert()

#     def get_image(self, x, y, width, height):
#         image = pg.Surfae((width, height))
#         image.blit(self.spritesheet, (0, 0), (x, y, width, height))
#         image = pg.transform.scale(image, (width, height))
#         return image
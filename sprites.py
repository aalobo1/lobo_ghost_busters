# # File created by: Aaron Lobo

# sprites module, to keep everything separated and organized


import pygame as pg
from pygame.sprite import Sprite
from settings import *
from random import randint
from utils import Cooldown
vec = pg.math.Vector2
from random import choice
# from utils import Spritesheet
from os import path
from math import *

# The sprites module contains all the sprites
# Sprites incldue: player, mob - moving object

#Creates player by creating a class
class Player(Sprite):
    def __init__(self, game, x, y,):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        # self.spritesheet = Spritesheet(path.join(self.game.img_folder, "New Piskel (3).png"))
        # self.load_images()
        self.image = pg.Surface((32, 32))

        # self.image.fill((GREEN))
        self.image = game.player_img
        self.rect = self.image.get_rect()
        # self.rect.x = x * TILESIZE[0]
        # self.rect.y = y * TILESIZE[1]
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE[0]
        self.speed = 300
        self.health = 100
        self.score = 0
        self.cd = Cooldown(1000)
        self.bcd = Cooldown(250)
        self.lastdir = "up"
        self.walking = False
        self.jumping = False
        self.last_update = 0
        self.current_frame = 0
        self.jump_power = 100
    def jump(self):
        self.rect.y += 1
        hits = pg.spritecollide(self, self.game.all_walls, False)
        self.rect.y += -1
        if hits:
            self.vel.y = -self.jump_power
    # def load_images(self):
    #     self.standing_frames = [self.spritesheet.get_image(0, 0, 32, 32),
    #                             self.spritesheet.get_image(32, 32, 32, 32)]
    #     for frame in self.standing_frames:
    #         frame.set_colorkey(BLACK)
    #     #self.walk_frames_r
    #     #self.walk_frames_l
    #     #pg.transform.flip

    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.walking:
            #switches the frame every 350 milliseconds
            if now - self.last_update > 350:
                print(now)
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
    def update(self):
        pass
    def get_keys(self):
        
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE]:
            self.jump()
        if keys[pg.K_e]:
            if self.bcd.ready():
                self.bcd.start()
                Bullet(self.game, self.rect.x, self.rect.y, self.lastdir)
        if keys[pg.K_w]:
            self.vel.y = -self.speed*self.game.dt
            self.lastdir = "up"
            # self.rect.y -= self.speed
        if keys[pg.K_a]:
            self.vel.x = -self.speed*self.game.dt
            self.lastdir = "left"
            # self.rect.x -= self.speed
        if keys[pg.K_s]:
            self.vel.y = self.speed*self.game.dt
            self.lastdir = "down"
            # self.rect.y += self.speed
        if keys[pg.K_d]:
            self.vel.x = self.speed*self.game.dt
            self.lastdir = "right"
            # self.rect.x += self.speed
        # accounting for diagonal movement
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                #creates condition to check if an object is collidable, and if yes then moving it
                if self.vel.x > 0:
                    if hits[0].state == "moveable":
                        print("i hit a moveable block")
                        hits[0].pos.x += self.vel.x
                        if hits[1]:
                            print("second element")
                    else:
                        self.pos.x = hits[0].rect.left - self.rect.width
                        
                if self.vel.x < 0:
                    if hits[0].state == "moveable":
                        print("i hit a moveable block")
                        hits[0].pos.x += self.vel.x
                    else:
                        self.pos.x = hits[0].rect.left - self.rect.width
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                #hits[0].vel.x = 0
                self.rect.x = self.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y


    def collide_with_stuff(self, group, kill):
        #constantly checking whether a spirte has collided with a certain group
        hits = pg.sprite.spritecollide(self, group, kill)
        if hits: 
            if str(hits[0].__class__.__name__) == "Mob":
                print("i collided with a mob")
                if self.cd.ready():
                    self.health -= 10
                    self.cd.start()

                if self.health == 0:
                    pg.quit()
            if str(hits[0].__class__.__name__) == "Coin":
                self.score += 1    
    def update(self):
        self.get_keys()
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        self.collide_with_stuff(self.game.all_mobs, False)
        self.collide_with_stuff(self.game.all_coins, True)
        # if not self.cd.ready():
        #     self.image = self.game.player_img
        # #     print("not ready")
        # else:
        #     self.image.fill(GREEN)
        # #     print("ready")

#Creates Mob using same code as player but not controllable with keys
class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
        # mob is able to move in all directions
        self.connections = [vec(1,0), vec(-1,0), vec(0,1), vec(0,-1)]


    def in_bounds(self, node):
        # finds which nodes are inside the grid
        return 0 <= node.x < self.width and 0 <= node.y < self.height
    
    def passable(self, node):
        return node not in self.walls



    def find_neighbors(self, node):
        #finds the neghboring areas which the Mob can travel to
        neighbors = [node + connection for connection in self.connections]
        neighbors = filter(self.in_bounds, neighbors) # makes sure that the nodes are all in bounds
        neighbors = filter(self.passable, neighbors)
        return neighbors
    def bfs_pathfinding(grid, start, goal):
        if start == goal:
            return[]
        
        frontier = deque()
        frontier.append(start)
        came_from = {start: None}
        
        while frontier:
            current = frontier.popleft()

            if current == goal:
                break

            for next_node in grid.find.neighbors(current):
                if next_node not in came_from:
                    frontier.append(next_node)
                    came_from[next_node] = current

        if goal not in came_from:
            return[]
        
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()

        return path
        
    




        

class Mob(Sprite):
    def __init__(self, game, x, y):
        Sprite.__init__(self)
        self.game = game
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)  
        self.vel = vec(choice([-10, 10]),choice([-10, 10]))
        self.pos = vec(x*TILESIZE[0], y*TILESIZE[1])
        self.image = pg.Surface((32, 32))
        self.image.fill((RED))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE[0]
        self.rect.y = y * TILESIZE[1]
        self.speed = 10
        self.path = []
        self.path_update_cooldown = Cooldown(500) # update path every 500 ms
        self.path_update_cooldown.start()

        #create grid for pathing
        self.grid = SquareGrid(TILES_W, TILES_H)
        self.update_grid()

    def update_grid(self):
        # update grid with positions of walls
        self.grid.walls = []
        for wall in self.game.all_walls:
            wall_tile = vec(wall.rect.x // TILESIZE[0], wall.rect.y // TILESIZE[1])
            self.grid.walls.append(wall_tile)
    
    def get_tile_pos(self):
        # gets current tile of Mob
        return vec(int(self.rect.x // TILESIZE[0]), int(self.rect.y // TILESIZE[1]))
    



    def chase_player(self):
        # use pathfinding to chase player
        if self.path_update_cooldown.ready():
            self.path_update_cooldown.start()
            
            # Get current positions in tile coordinates
            mob_tile = self.get_tile_pos()
            player_tile = vec(int(self.game.player.rect.x // TILESIZE[0]), 
                            int(self.game.player.rect.y // TILESIZE[1]))
            
            # Calculate new path
            self.path = bfs_pathfinding(self.grid, mob_tile, player_tile)
        
        # Follow the path
        if self.path:
            target_tile = self.path[0]
            target_pos = vec(target_tile.x * TILESIZE[0], target_tile.y * TILESIZE[1])
            
            # Calculate direction to target
            direction = target_pos - self.pos
            if direction.length() > 0:
                direction = direction.normalize()
                self.vel = direction * self.speed * self.game.dt
                
                # Remove waypoint if reached
                if self.pos.distance_to(target_pos) < 5:
                    self.path.pop(0)
            else:
                self.vel = vec(0, 0)
        else:
            self.vel = vec(0, 0)

        

        
    def collide_with_walls(self, dir):
            if dir == 'x':
                hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
                if hits:
                    if self.vel.x > 0:
                        self.pos.x = hits[0].rect.left - self.rect.width
                    if self.vel.x < 0:
                        self.pos.x = hits[0].rect.right
                    #self.vel.x = 0
                    self.rect.x = self.pos.x
                    self.vel.x *= choice([-1, 1])
            if dir == 'y':
                hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
                if hits:
                    if self.vel.y > 0:
                        self.pos.y = hits[0].rect.top - self.rect.height
                    if self.vel.y < 0:
                        self.pos.y = hits[0].rect.bottom
                    #self.vel.y = 0
                    self.rect.y = self.pos.y
                    self.vel.y *= choice([-1, 1])
        

    def update(self):
        #mob behavior
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
        if self.game.player.vel.x > self.vel.x:
            #print ("I ned to chase the player")
            pass
        else:
           # print ('I dont need to chase the player x')
           pass
#Creates coins usingthe same mechanism as mobs but unmoving
class Coin(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)  
        self.image = pg.Surface(TILESIZE)
        self.image.fill((YELLOW))
        self.rect = self.image.get_rect()
        self.rect.x = x* TILESIZE[0]
        self.rect.y = y* TILESIZE[1]
        
class Wall(Sprite):
    #creates walls that will be able to be collided with
    def __init__(self, game, x, y, state):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        
        self.image = pg.Surface(TILESIZE)
        self.image.fill(GREY)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE[0]
        self.state = state
    def update(self):
        # wall
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

#creates the Bullet class    
class Bullet(Sprite):
    def __init__(self, game, x, y, direction):
        self.game = game
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.image = pg.Surface(TILESIZE)
        self.image.fill((255, 192, 203))
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.dir = direction
        self.pos = vec(x,y)
        self.pos = vec(x+(TILESIZE[0]/4), y+(TILESIZE[0]/4))
        self.speed = 500

    def update(self):
        if self.dir == "up":
            self.vel.y = -self.speed*self.game.dt
        elif self.dir == "down":
            self.vel.y = self.speed*self.game.dt
        elif self.dir == "right":
            self.vel.x = self.speed*self.game.dt
        elif self.dir == "left":
            self.vel.x = -self.speed*self.game.dt
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
    def collide(self):
        hits = pg.sprite.spritecollide(self, self.game.all_walls, True)
        if hits:
            self.kill()

    
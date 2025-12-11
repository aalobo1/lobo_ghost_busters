# # File created by: Aaron Lobo

# sprites module, to keep everything separated and organized

import pygame as pg
from pygame.sprite import Sprite
from settings import *
from random import randint
from utils import Cooldown
vec = pg.math.Vector2
from random import choice
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
        self.image = pg.Surface((32, 32))
        self.image = game.player_img
        self.rect = self.image.get_rect()
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

    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.walking:
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
        if keys[pg.K_a]:
            self.vel.x = -self.speed*self.game.dt
            self.lastdir = "left"
        if keys[pg.K_s]:
            self.vel.y = self.speed*self.game.dt
            self.lastdir = "down"
        if keys[pg.K_d]:
            self.vel.x = self.speed*self.game.dt
            self.lastdir = "right"
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
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
        self.speed = 5
    def collide_with_walls(self, dir):
            if dir == 'x':
                hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
                if hits:
                    if self.vel.x > 0:
                        self.pos.x = hits[0].rect.left - self.rect.width
                    if self.vel.x < 0:
                        self.pos.x = hits[0].rect.right
                    self.rect.x = self.pos.x
                    self.vel.x = 0
                    # makes the mobs bounce randomly off wall using vectors
                    # self.rect.x = self.pos.x
                    # self.vel.x *= choice([-1, 1])
                   
            if dir == 'y':
                hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
                if hits:
                    if self.vel.y > 0:
                        self.pos.y = hits[0].rect.top - self.rect.height
                    if self.vel.y < 0:
                        self.pos.y = hits[0].rect.bottom
                    self.rect.y = self.pos.y
                    self.vel.y = 0
                    # makes the mobs bounce randomly off wall using vectors
                    # self.rect.y = self.pos.y
                    # self.vel.y *= choice([-1, 1])
    def chase_player(self):
        # use A* to actually chase player with grid based movement and only when not moving
        if not self.moving:
            if self.path_update_cooldown.ready() or len(self.path) == 0:
                self.path_update_cooldown.start()

                # Get current positions in tile coordinates
                mob_tile = self.get_tile_pos()
                player_tile = (int(self.game.player.rect.x // TILESIZE[0]), 
                              int(self.game.player.rect.y // TILESIZE[1]))




        
    def get_wall_positions(self):
        # get list of all wall tile positions
        walls = []
        for wall in self.game.all_walls:
            wall_tile = (int(wall.rect.x // TILESIZE[0]), int(wall.rect.y // TILESIZE[1]))
            walls.append(wall_tile)
        return walls
        
       
 
    def update(self):
        #mob behavior
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.chase_player('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
        self.chase_player('y')
        # if self.game.player.vel.x > self.vel.x:
        #     self.vel.x = self.game.player.vel.x
        #  Pacman tunnel through sides
        if self.rect.left > WIDTH:
            self.pos.x = -self.rect.width
            self.rect.x = self.pos.x
 
        if self.rect.right < 0:
            self.pos.x = WIDTH
            self.rect.x = self.pos.x

# A* Pathfinding Node class
class Node:
    def __init__(self, position):
        self.position = position  # (x, y) tile coordinates
        self.parent = None
        self.gx = 0  # Cost from start to this node
        self.hx = 0  # Heuristic cost from this node to goal
        self.fx = 0  # Total cost (gx + hx)
    # gx + hx = fx
    """
    gx = 30 (traveled 3 tiles, 10 cost each)
    hx = 50 (5 tiles away: |5-2| + |5-3| = 5, times 10 = 50)
    fx = 80 (total estimated cost)
    """
    def __eq__(self, other):
        return self.position == other.position


# A* Pathfinding Algorithm
def astar_pathfinding(start_pos, end_pos, walls):
    """
    A* pathfinding algorithm
    start_pos: (x, y) tile position
    end_pos: (x, y) tile position  
    walls: list of (x, y) tile positions that are walls
    """
    # If already at goal, return empty path
    if start_pos == end_pos:
        return []
    
    # Define possible movements (4 dirs only so it doesnt clip thru walls and moves like pac man)
    ADJACENTS = [
        (-1, 0),  # Left
        (1, 0),   # Right
        (0, -1),  # Up
        (0, 1)    # Down
    ]
    
    # Create start and end nodes
    start_node = Node(start_pos)
    end_node = Node(end_pos)
    
    # Initialize open and closed lists
    open_list = [start_node]
    closed_list = []
    # Loop until end is found
    while len(open_list) > 0:
        # Get node with lowest fx
        current_node = open_list[0]
        current_index = 0
        for index, node in enumerate(open_list):
            if node.fx < current_node.fx:
                current_node = node
                current_index = index
        
        # Move current node from open to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)
        
        # goal found!!!!!
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            path.reverse()
            # Remove the starting position
            if len(path) > 0 and path[0] == start_pos:
                path.pop(0)
            return path
        
        # Generate children (neighbors)
        children = []
        for new_position in ADJACENTS:
            # Get node position
            node_position = (current_node.position[0] + new_position[0],
                           current_node.position[1] + new_position[1])
            
            # Check if within bounds
            if node_position[0] < 0 or node_position[0] >= TILES_W:
                continue
            if node_position[1] < 0 or node_position[1] >= TILES_H:
                continue
            
            # Check if walkable (not a wall)
            if node_position in walls:
                continue
            
            # Create new node
            new_node = Node(node_position)
            new_node.parent = current_node
            children.append(new_node)
            # Loop through children
        for child in children:
            # Child is already in closed list
            if child in closed_list:
                continue
            
            # Calculate costs
            # All movements cost 10 (no diagonals)
            child.gx = current_node.gx + 10
            
            # Heuristic: Manhattan distance * 10
            child.hx = (abs(child.position[0] - end_node.position[0]) + 
                       abs(child.position[1] - end_node.position[1])) * 10
            
            child.fx = child.gx + child.hx
            
            # Check if child is already in open list with better path
            skip_child = False
            for open_node in open_list:
                if child == open_node and child.gx > open_node.gx:
                    skip_child = True
                    break
            
            if skip_child:
                continue
            
            # Add child to open list
            open_list.append(child)
    
    # No path found
    return []





    
   
                
                
            
           


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
        self.image = game.coin_img
        

class Wall(Sprite):
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
        self.image = game.wall_img
    
    def update(self):
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

# class Wall(Sprite):
#     def __init__(self, game, x, y, state):
#         self.groups = game.all_sprites, game.all_walls
#         Sprite.__init__(self, self.groups)
#         self.game = game
#         self.image = pg.Surface(TILESIZE)
#         self.image.fill(GREY)
#         self.rect = self.image.get_rect()
#         self.vel = vec(0,0)
#         self.pos = vec(x,y) * TILESIZE[0]
#         self.state = state
#         self.image = game.bgwall_img
    
#     def update(self):
#         self.pos += self.vel
#         self.rect.x = self.pos.x
#         self.rect.y = self.pos.y

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


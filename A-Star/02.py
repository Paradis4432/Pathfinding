from ast import Lambda
import random
import re
from turtle import width
import pygame
import math
from queue import PriorityQueue

win = pygame.display.set_mode((800,800))

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
#YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
    
    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neig(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def rebuild_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def wait():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_n or pygame.key.get_pressed()[pygame.K_n]:
                return
        

def algorithm(draw, grid, start, end):
    # pseudocode https://en.wikipedia.org/wiki/A*_search_algorithm#:~:text=x).-,Pseudocode,-%5Bedit%5D
    draw()
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0

    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    ite_count = 0

    while not open_set.empty():
        print("\n" + "-" * 20 + "iteration: " + str(ite_count) + "-" * 20 + "\n")
        wait()
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            rebuild_path(came_from, end, draw)
            return True

        for nei in current.neighbors:
            print("\nROW:COL : " + str(nei.row) + ":" + str(nei.col))
            temp_g_score = g_score[current] + 1
            print("temp_g_score: " + str(temp_g_score))
            print("g_score[nei]: " + str(g_score[nei]))
            if temp_g_score < g_score[nei]:
                came_from[nei] = current
                g_score[nei] = temp_g_score
                f_score[nei] = temp_g_score + h(nei.get_pos(), end.get_pos())
                print("\ttemp_g_score < g_score[nei]")
                print("\th(nei.get_pos(), end.get_pos()): " + str(h(nei.get_pos(), end.get_pos())))
                print("\tg_score[nei]: " + str(g_score[nei]))
                print("\tf_score[nei]: " + str(f_score[nei]))
                if nei not in open_set_hash:
                    print("\t\tnei not in open_set_hash")
                    count += 1
                    open_set.put((f_score[nei], count, nei))
                    open_set_hash.add(nei)
                    nei.make_open()
                    print("\t\tmade nei open")
        
        draw()

        if current != start:
            current.make_closed()
        ite_count += 1
    return False




def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

pygame.font.init()
def draw_grid(win, rows, width):
    gap = width // rows
    font = pygame.font.SysFont('Comic Sans MS', 20)
    
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))

        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))
            text = font.render(str(i) + ":" + str(j), True, BLUE)
            win.blit(text, (i * gap, j * gap))


def draw(win, grid, rows, width):
    win.fill(WHITE)
    
    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap 

    return row, col

def main(win, width):
    ROWS = 15
    grid = make_grid(ROWS, width)

    start = None
    end = None
    
    run = True
    started = False
    
    while run:
        draw(win, grid, ROWS, width)
        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                run = False
            
            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row , col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()

                elif not end and node != start:
                    end = node
                    end.make_end()

                elif node != end and node != start:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row , col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                if node == end:
                    end = None

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.update_neig(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    start.make_start()
                    end.make_end()

                if e.key == pygame.K_c:
                    win.fill(WHITE)
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
                if e.key == pygame.K_b:
                    for row in grid:
                        for node in row:
                            if node.color != WHITE:
                                if not node.is_start() and not node.is_end() and not node.is_barrier():
                                    node.color = WHITE
                if e.key == pygame.K_r:
                    for row in grid:
                        for node in row:
                            if random.randint(0,100) < 20:
                                node.color = BLACK
                                
                            
    pygame.quit()

main(win, 800)

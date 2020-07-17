import pygame
import math
from queue import PriorityQueue

WIDTH = 600
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Visualisation")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Block:
    def __init__(self, row, col, width, totalRows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbours = []
        self.width = width
        self.totalRows = totalRows

    def getPos(self):
        return self.row, self.col

    def isClosed(self):
        return self.color == RED

    def isOpen(self):
        return self.color == GREEN

    def isBarrier(self):
        return self.color == BLACK

    def isStart(self):
        return self.color == ORANGE

    def isEnd(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def makeClosed(self):
        self.color = RED

    def makeOpen(self):
        self.color = GREEN

    def makeBarrier(self):
        self.color = BLACK

    def makeStart(self):
        self.color = ORANGE

    def makeEnd(self):
        self.color = TURQUOISE

    def makePath(self):
        self.color = PURPLE

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

    def updateNeighbours(self, grid):
        self.neighbours = []
        if self.row < self.totalRows - 1 and not grid[self.row+1][self.col].isBarrier(): # DOWN
            self.neighbours.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].isBarrier(): # UP
            self.neighbours.append(grid[self.row-1][self.col])

        if self.col < self.totalRows - 1 and not grid[self.row][self.col+1].isBarrier(): # RIGHT
            self.neighbours.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col-1].isBarrier(): # LEFT
            self.neighbours.append(grid[self.row][self.col-1])

    def __lt__(self, other):
        return False


def HeuristicFunction(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x2-x1) + abs(y2-y1)

def reconstructPath(cameFrom, end, draw):
    while end in cameFrom:
        end = cameFrom[end]
        end.makePath()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    openSet = PriorityQueue()
    openSet.put((0, count, start))
    cameFrom = {}
    gScore = {block: float("inf") for row in grid for block in row}
    gScore[start] = 0
    fScore = {block: float("inf") for row in grid for block in row}
    fScore[start] = HeuristicFunction(start.getPos(), end.getPos())
    openSetHash = {start}

    while not openSet.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.QUIT()

        current = openSet.get()[2]
        openSetHash.remove(current)

        if current == end:
            reconstructPath(cameFrom, end, draw)
            end.makeEnd()
            start.makeStart()
            return True

        for neighbour in current.neighbours:
            tempGScore = gScore[current] + 1
            if tempGScore < gScore[neighbour]:
                cameFrom[neighbour] = current
                gScore[neighbour] = tempGScore
                fScore[neighbour] = tempGScore+HeuristicFunction(neighbour.getPos(), end.getPos())
                if neighbour not in openSetHash:
                    count += 1
                    openSet.put((fScore[neighbour], count, neighbour))
                    openSetHash.add(neighbour)
                    neighbour.makeOpen()

        draw()

        if current != start:
            current.makeClosed()

    return False



def makeGrid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            block = Block(i, j, gap, rows)
            grid[i].append(block)
    return grid


def drawGrid(win, rows, width): # Draws grid lines
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for block in row:
            block.draw(win)

    drawGrid(win, rows, width)
    pygame.display.update()


def getClickPosition(mousePos, rows, width):
    gap = width // rows
    y, x = mousePos
    row = y // gap
    col = x // gap
    return row, col


def main(win, width):
    ROWS = 25
    grid = makeGrid(ROWS, width)

    start = None
    end = None

    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]: # Left
                position = pygame.mouse.get_pos()
                row, col = getClickPosition(position, ROWS, width)
                block = grid[row][col]
                if not start and block != end:
                    start = block
                    start.makeStart()
                elif not end and block != start:
                    end = block
                    end.makeEnd()
                elif block != end and block != start:
                    block.makeBarrier()

            elif pygame.mouse.get_pressed()[2]: # Right
                position = pygame.mouse.get_pos()
                row, col = getClickPosition(position, ROWS, width)
                block = grid[row][col]
                block.reset()
                if block == start:
                    start = None
                elif block == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for block in row:
                            block.updateNeighbours(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_r:
                    start = None
                    end = None
                    grid = makeGrid(ROWS, width)

    pygame.quit()


main(WINDOW, WIDTH)
'''
Pytris - A version of modern tetris written in python

Author - Gillom McNeil
Based off of the tutorial provided by ...

Features to be added:
- change message after game over depending on result, eg Reward a new highscore
- should be able to rotate a piece when touching the wall (currently blocked)
- add a leaderboard displayed in the main menu
- fix random pieces to be less random and more evenly distributed
    - possibly add a weight to the probability of drawing each piece
    - probability weight will change based on recent pieces, last 5 pieces?

'''
import os
import pygame
import random

from pygame.display import update

"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""
 
pygame.font.init()
 
# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per block
block_size = 30
 
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height
 
 
# SHAPE FORMATS
 
S = [['.....',
      '......',
      '..00..',
      '.00...',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]
 
Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]
 
I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]
 
O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]
 
J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]
 
L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]
 
T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]
 
shapes = [S, Z, I, O, L, J, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represents shape
shape_shadows = [(0, 64, 0), (64, 0, 0), (0, 64, 64), (64, 64, 0), (64, 41, 0), (0, 0, 64), (32, 0, 32)]
 
'''
A Piece can be one of the 7 possible shapes in tetris, each shape type has one
color. A piece will have a location given by an x and y value. Pieces can be
rotated multiple times.
'''
class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.shadow = shape_shadows[shapes.index(shape)]
        self.rotation = 0

'''
create_grid takes a dictionary of x, y pairs as keys and colors as values
eg. {(1,1):(255,255,255)} the block at x, y = 1 is white
returns the grid
'''
def create_grid(locked_pos={}):
    #set up a 2d array of 3 value tuples, with width of 10 and length of 20
    #set each element in the array to be black (0,0,0)
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]

    #rows are represented by i (y value)
    for i in range(len(grid)):
        #columns are represented by j (x value)
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)] #get the color of the block at (i,j)
                grid[i][j] = c #insert the color at the right space in the grid
    return grid

'''
Take a shape format that we can view easily and turn it into something that the computer can use
'''
def convert_shape_format(shape):
    #this list will contain all the locations that are occupied by a block
    positions = []
    
    #find out which orientation the shape is in
    #e.g. T shape with rotation = 2 => picks out 2%4=2
    #we don't need to worry about the value of rotation
    format = shape.shape[shape.rotation % len(shape.shape)]

    #look through every row and column
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                #shape location at top left, i, j is relative to shape location
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        #shift all elements left and up to be more accurate to the screen
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions
        
'''
check if each of the blocks containing shapes are also in the list of
acceptable block locations
'''
def valid_space(shape, grid):
    #accepted positions are those without a shape currently (color = black)
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    #take 2d array and flatten it to 1d
    #[[(0,1),
    #   [(1,1)]] -> [(0,1), (1,1)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    #now we have another list of positions containing a shape
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            #only ask once the piece is on screen (starts above the y=0 line)
            if pos[1] > -1:
                return False
    return True
'''
If any of the pieces are resting above the screen, you lose
'''
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

'''
Return a randomly selected shape from the list of shapes
'''
def get_shape():
    # picks a random shape from the given array
    return Piece(5, 0, random.choice(shapes))
 
'''
Draw some white text to the middle of the screen
''' 
def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont("microsoftsansserif", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - (label.get_height()/2) - 100))

'''
draw the gray lines between blocks
surface : pygame window being drawn on
grid : 2d array containing the colours (r,g,b) of the blocks at that location
'''
def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        #draw 20 horizontal lines
        pygame.draw.line(surface, (128,128,128), (sx, sy + i*block_size), (sx+play_width, sy+ i*block_size))
        #draw 10 vertical lines
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128,128,128), (sx + j*block_size, sy), (sx+ j*block_size, sy+ play_height))

'''
Check for completed rows and delete those blocks from locked_positions
Shift the remaining rows down by the number of rows completed
Return the number of rows completed
'''
def clear_rows(grid, locked):
    #number of rows to be cleared
    inc = 0
    cleared_rows = []
    #need to check rows for completion from bottom to top (19 to 0)
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        #if no blocks are black in a row, then the row is complete
        if (0,0,0) not in row:  
            cleared_rows.append(i)
            inc += 1
            ind = i #this will be the row closest to the top to be cleared
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if inc > 0:
        #sort by y values of the key, in reverse
        for key in sorted(list(locked), key = lambda x: x[1])[::-1]:
            x, y = key
            #these are the pieces below the top completed row
            if y > ind:
                rows = 0
                #find number of rows below current row
                for i in cleared_rows:
                    if i > y:
                        rows += 1
                #move piece down by number of rows completed below it
                newKey = (x, y + rows)
                locked[newKey] = locked.pop(key)
            #these are the pieces above the top comleted row
            else:
                #shift each block down by number of rows completed
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc
        
'''
Draw the next tetromino to fall after the current piece. 
'''
def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('microsoftsansserif', 30)
    label = font.render("Next shape:", 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 200

    format = shape.shape[shape.rotation % len(shape.shape)]
    
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == "0":
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))

'''
Draws the piece that is currently being held. This is called when the user presses the shift key.
'''
def draw_hold_piece(shape, surface):
    font = pygame.font.SysFont('microsoftsansserif', 30)
    label = font.render("Hold:", 1, (255,255,255))

    sx = top_left_x - 200
    sy = top_left_y + play_height/2 - 180

    if (shape != None):
        format = shape.shape[shape.rotation % len(shape.shape)]
        
        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == "0":
                    pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx - 25, sy - 50))

'''
Draws each of the elements in the game window:
Black background,
Title, 
Current Score,
Highscore,
Current level/speed,
game grid,
the tetromino pieces using the locations in grid.
'''
def draw_window(surface, grid, score=0, last_score=0, level_disp=1):
    #start of with a filled black canvas
    surface.fill((0,0,0))

    #Initialize fonts and render a label as a title
    pygame.font.init()
    font = pygame.font.SysFont('microsoftsansserif', 60)
    label = font.render('Pytris', 1, (255,255,255))

    #put the label at the middle top
    surface.blit(label, (top_left_x + play_width/2 - label.get_width()/2, 15))

    #draw the current score
    font = pygame.font.SysFont('microsoftsansserif', 30)
    label = font.render("Score: " + str(score), 1, (255,255,255))

    sx = top_left_x + play_width 
    sy = top_left_y + play_height/2

    surface.blit(label, (sx + 60, sy - 350))

    #draw the highscore
    label = font.render("Highscore: " + str(last_score), 1, (255,255,255))

    sx = top_left_x - 230
    sy = top_left_y - 60

    surface.blit(label, (sx, sy))

    #draw the current level/speed
    label = font.render("Level: " + str(level_disp), 1, (255,255,255))

    sx = top_left_x - 230
    sy = top_left_y

    surface.blit(label, (sx, sy))


    #loop through each block location and fill a block of size block_size and of the appropriate color from grid[i][j]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    #draw the red border around the play area
    pygame.draw.rect(surface, (255,0,0), (top_left_x, top_left_y, play_width, play_height), 4)
    
    draw_grid(surface, grid)

def update_score(new_score, win):
    score = max_score()

    with open(os.path.join(os.sys.path[0], "scores.txt"), "w") as f:
        if int(score) > new_score:
            f.write(str(score))
        else:
            f.write(str(new_score))
            win.fill((0,0,0))
            draw_text_middle("HighScore!", 80, (255,255,255), win)
            pygame.display.update()


def max_score():
    with open(os.path.join(os.sys.path[0], "scores.txt"), "r") as f:
        lines = f.readlines()
        score = lines[0].strip()
        return score

def main(win):
    
    locked_positions ={}
    #grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    hold_piece = None
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    level_disp = 1
    score = 0
    last_score = max_score()
    paused = False
    stop_timer = 0
    piece_held = False
    button_held = 0
    score_factor = 1

    while run:
        grid = create_grid(locked_positions)
        left_right_pressed = False

        if not paused:
            #make the pieces fall at the same speed regardless of machine
            #based the clock off of how long the while loop takes
            fall_time += clock.get_rawtime() #millisec
            level_time += clock.get_rawtime() #millisec
            clock.tick()

            if level_time/1000 > 20:
                level_time = 0
                if fall_speed > 0.12:
                    fall_speed -= 0.001
                    level_disp += 1

            #move down at rate of fall_speed
            if fall_time/1000 > fall_speed:
                fall_time = 0
                current_piece.y += 1
                if not(valid_space(current_piece, grid) and current_piece.y > 0):
                    #this means we've hit the bottom and should stop moving
                    if stop_timer > 1:
                        current_piece.y -=1
                        change_piece = True
                        stop_timer = 0
                    else:
                        current_piece.y -=1
                        stop_timer += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                #pygame.display.quit() getting an error here

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    left_right_pressed = True
                    button_held = 0
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    left_right_pressed = True
                    button_held = 0
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
                if event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True
                if event.key == pygame.K_LSHIFT:
                    if not piece_held:
                        if (hold_piece != None):
                            temp = current_piece
                            current_piece = hold_piece
                            hold_piece = temp
                            hold_piece.y = 0
                            hold_piece.x = 5
                            hold_piece.rotation = 0
                            piece_held = True
                        else:
                            hold_piece = current_piece
                            hold_piece.x = 5
                            hold_piece.y = 0
                            hold_piece.rotation = 0
                            current_piece = next_piece
                            next_piece = get_shape()
                            piece_held = True

                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    if paused:
                        paused = False
                    else:
                        paused = True
        keys = pygame.key.get_pressed() 
        if keys[pygame.K_DOWN]:
            button_held += clock.get_rawtime()
            if button_held/1000 > fall_time/2:
                button_held = 0
                current_piece.y += 1
                if not(valid_space(current_piece, grid)):
                    current_piece.y -= 1
        if not left_right_pressed and keys[pygame.K_LEFT]:
            button_held += clock.get_rawtime()
            if button_held/1000 > fall_speed/2:
                button_held = 0
                current_piece.x -= 1
                if not(valid_space(current_piece, grid)):
                    current_piece.x += 1
        if not left_right_pressed and keys[pygame.K_RIGHT]:
            button_held += clock.get_rawtime()
            if button_held/1000 > fall_speed/2:
                button_held = 0
                current_piece.x += 1
                if not(valid_space(current_piece, grid)):
                    current_piece.x -= 1
        
        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        #if we've hit the bottom
        if change_piece:
            #update locked_pos
            for pos in shape_pos:
                #place the key value pair ((x,y):color) into the dict of locked pos
                #for each pos containing the stopped shape
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            #shift next into current and get a new next piece
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            #once everything is settled, clear the completed rows
            #if num of cleared rows = 4 (tetris), increase multiplicative factor
            num_cleared_rows = clear_rows(grid, locked_positions)
            if num_cleared_rows == 4:
                score_factor += 1
                score += num_cleared_rows * 10 * score_factor
            else:
                score_factor = 1
                score += num_cleared_rows * 10
            piece_held = False
        
        #draw the game window and the next piece and update display
        #draw_level()
        draw_window(win, grid, score, last_score, level_disp)
        draw_next_shape(next_piece, win)
        draw_hold_piece(hold_piece, win)
        if paused:
            draw_text_middle("Paused", 80, (255,255,255), win)
        pygame.display.update()

        #if a piece is resting above the top row, the game is over
        if check_lost(locked_positions):
            draw_text_middle("Game Over!", 80, (255,255,255), win)
            pygame.display.update()
            pygame.time.delay(800)
            update_score(score, win)
            pygame.time.delay(1400)
            run = False


def main_menu(win):
    run = True
    while run:
        win.fill((0,0,0))
        draw_text_middle('Press any key to play', 60, (255,255,255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)

    pygame.display.quit()

win = pygame.display.set_mode((s_width,s_height))
pygame.display.set_caption('Pytris')
main_menu(win)  # start game

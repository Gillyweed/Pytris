Welcome to PyTris!

Author : Gillom McNeil A00450414

Created following the tutorial : Python and Pygame Tutorial - Build Tetris! Full GameDev Course
Link : https://www.youtube.com/watch?v=zfvxp7PgQ6c
Written in : Python 3.10.0 , Pygame 2.1.0

TODO:

-Break function draw_window into multiple functions for ease of readability
-Include the draw_hold_piece and draw_next_piece functions in draw_window 
-Add a property to the Piece class, shadow which will contain the shadow color
-Change the pause functionality to access a menu

Features added on after tutorial:
- the ability to hold a piece and move onto the next (can only switch once per new piece)
- the ability to hard drop a piece to the bottom using spacebar
- fixed a bug causing lines to clear wrong
- reversed the colors of the "L" and "J" pieces to be true to original
- added the display for the increasing speed/level
- added a short window of time before a piece 'sticks' to the bottom, allowing 
    pieces to slide briefly
- added a pause button with popup text, access with 'P' or 'esc'
- added ability to hold down left/right/down without needing to tap buttons


Possible upgrades:
-fix scoring to be more accurate
    - combo multiplier for number of rows cleared at one time
    - score multiplier for higher speeds / difficulties
    - combo multiplier for repeated tetris' (4 rows cleared = tetris)
- keep track of multiple users scores
- display leaderboard of scores
- toggle shadow piece along bottom for beginners
- fix bug where the "I" piece can be moved out of bounds, causing loss
- fix awkward spacing around hold pieces/ next pieces


Controls: 

Move left    - left arrow
Move right   - right arrow
Move down    - down arrow
Rotate       - up arrow
Hard drop    - spacebar
Hold piece   - L shift
Pause        - P
Exit         - esc


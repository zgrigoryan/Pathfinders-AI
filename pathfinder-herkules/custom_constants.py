# Description: Custom constants for the game

# Global _________________________________

GRID_SIZE = 20
HIDRA_ENABLED = True

WINDOW_SIZE = 800
SIDEBAR_WIDTH = 140
PYGAME_FONT = 27
GRID_WIDTH = 1
RESULT_FONT_SIZE = 20

EMPTY_CELL_ID = 0
WALL_ID = 1
PLAYER_ID = 2
KID1_ID = 3
KID2_ID = 4
WIFEY_ID = 5
LAVA_ID = 6
MOUNTAIN_ID = 7
HIDRA_ID = 8
DEAD_HIDRA_ID = 'dead_hidra'

CELL_COSTS = {
    EMPTY_CELL_ID: 1,
    WALL_ID: float('inf'),  # Walls are impassable
    LAVA_ID: float('inf'),  # Lava is impassable
    HIDRA_ID: float('inf'),  # Hidra is impassable until you kill it
    MOUNTAIN_ID: 10,
    PLAYER_ID: 1,
    WIFEY_ID: 1,
    DEAD_HIDRA_ID: 1
}

# COLORS _________________________________

LIGHT_GREY = (200, 200, 200)
GREY = (150, 150, 150)
DARK_GREY = (100, 100, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

RED_WITH_TRANSPARENCY_ALPHA = (255, 0, 0, 100)
GREEN_WITH_TRANSPARENCY_ALPHA = (0, 255, 0, 100)

# SIDEBAR ________________________________

BUTTON_WIDTH = 100
BUTTON_HEIGHT = 40
BUTTON_X = WINDOW_SIZE + 10
BUTTON_TEXT_X = WINDOW_SIZE + 20

BUTTON_LABELS = ["Wall", "Eraser", "Player", "Wifey", "Lava", "Mountain"]
BUTTON_SPACING = 20  # Spacing between buttons
SIDEBAR_PADDING = 10  # Padding from top and bottom of the sidebar

MAP_CHECK_Y = WINDOW_SIZE - 160
RUN_BUTTON_Y = WINDOW_SIZE - 80

# CREATING A DEFAULT MAP ___________________

MAX_ATTEMPTS = 20 # Attempt to place obstacles while ensuring a path exists

# ________________________________________

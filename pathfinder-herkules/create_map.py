import pygame
import sys

from pygame import Rect

import custom_constants as c
from typing import List
# from utils import ask_input

from collections import deque


class Grid:
    def __init__(self, grid_size: int):
        self.grid_size = grid_size
        self.cell_size = c.WINDOW_SIZE // grid_size
        self.grid = [[c.EMPTY_CELL_ID for _ in range(grid_size)] for _ in range(grid_size)]
        self.player_in_the_game = False
        self.goal_in_the_game = False
        self.valid_map = False

        self.violating_cells = set()

        self.wall_image = self.upload_and_scale_image("./images/wall.jpeg")
        self.player_image = self.upload_and_scale_image("./images/hercules.jpeg")
        self.wifey_image = self.upload_and_scale_image("./images/wifey.jpeg")
        self.kid1_image = self.upload_and_scale_image("./images/kid1.jpeg")
        self.kid2_image = self.upload_and_scale_image("./images/kid2.jpeg")
        self.hera_image = self.upload_and_scale_image("./images/hera.jpeg")
        self.lava_image = self.upload_and_scale_image("./images/lava.jpg")

    def upload_and_scale_image(self, image_path: str) -> pygame.Surface:
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (self.cell_size, self.cell_size))

        return image

    def update_violating_cells(self) -> None:
        """
        Update the set of violating cells by performing a BFS from the edges of the grid.
        Also, validate that the player and goal are fully enclosed by walls.
        """
        self.violating_cells.clear()
        visited = set()
        queue = deque()
        grid_size = self.grid_size

        # Start BFS from the edges and enqueue non-wall cells
        for x in range(grid_size):
            for y in [0, grid_size - 1]:
                if self.grid[y][x] != c.WALL_ID and (x, y) not in visited:
                    queue.append((x, y))
                    visited.add((x, y))

        for y in range(grid_size):
            for x in [0, grid_size - 1]:
                if self.grid[y][x] != c.WALL_ID and (x, y) not in visited:
                    queue.append((x, y))
                    visited.add((x, y))

        # Perform BFS to find all reachable cells from edges
        while queue:
            x, y = queue.popleft()
            self.violating_cells.add((x, y))

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    if (nx, ny) not in visited and self.grid[ny][nx] != c.WALL_ID:
                        visited.add((nx, ny))
                        queue.append((nx, ny))

        # Initialize flags
        player_enclosed = False
        goal_enclosed = False

        # Locate player and goal positions
        player_pos = None
        goal_pos = None
        for y in range(grid_size):
            for x in range(grid_size):
                if self.grid[y][x] == c.PLAYER_ID:
                    player_pos = (x, y)
                elif self.grid[y][x] == c.WIFEY_ID:
                    goal_pos = (x, y)
                # Early exit if both are found
                if player_pos and goal_pos:
                    break
            if player_pos and goal_pos:
                break

        # Check if player and goal are enclosed
        if player_pos and goal_pos:
            # Player is enclosed if not in violating_cells
            player_enclosed = player_pos not in self.violating_cells
            # Goal is enclosed if not in violating_cells
            goal_enclosed = goal_pos not in self.violating_cells

        self.valid_map = player_enclosed and goal_enclosed and self.player_in_the_game and self.goal_in_the_game
        if self.valid_map:
            self.violating_cells.clear()

    def draw(self, screen: pygame.Surface, check_map: bool) -> None:
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)

                if self.grid[y][x] == c.WALL_ID:
                    screen.blit(self.wall_image, rect.topleft)
                elif self.grid[y][x] == c.PLAYER_ID:
                    screen.blit(self.player_image, rect.topleft)
                elif self.grid[y][x] == c.WIFEY_ID:
                    screen.blit(self.wifey_image, rect.topleft)
                elif self.grid[y][x] == c.LAVA_ID:
                    screen.blit(self.lava_image, rect.topleft)

                if check_map and (x, y) in self.violating_cells:
                    s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    s.fill((255, 0, 0, 100))  # Red color with alpha for transparency
                    screen.blit(s, rect.topleft)

                pygame.draw.rect(screen, c.GREY, rect, c.GRID_WIDTH)

    def update_cell(self, x: int, y: int, tool: str) -> None:
        """
        :param x: x coordinate of the cell
        :param y: y coordinate of the cell
        :param tool: what is selected on sidebar
        :return: None
        """
        # Overwrite the player/goal if it is already in the game
        if self.grid[y][x] == c.PLAYER_ID:
            self.player_in_the_game = False
        if self.grid[y][x] == c.WIFEY_ID:
            self.goal_in_the_game = False
        if tool == "wall":
            self.grid[y][x] = c.WALL_ID
        elif tool == "eraser":
            self.grid[y][x] = c.EMPTY_CELL_ID
        # Add player to the game only if there is no player in the game
        elif tool == "player" and not self.player_in_the_game:
            self.grid[y][x] = c.PLAYER_ID
            self.player_in_the_game = True
        elif tool == "wifey" and not self.goal_in_the_game:
            self.grid[y][x] = c.WIFEY_ID
            self.goal_in_the_game = True
        elif tool == "lava":
            self.grid[y][x] = c.LAVA_ID

        self.update_violating_cells()


class Sidebar:
    def __init__(self):
        self.selected_tool = "wall"
        self.check_map = False

    def draw(self, screen: pygame.Surface, valid_map: bool) -> List[Rect]:
        """
        Draws a sidebar with "Wall" and "Eraser" buttons on the screen.

        :param screen: pygame screen surface
        :return: wall_button and eraser_button as Rect objects for collision detection
        """

        font = pygame.font.Font(None, c.PYGAME_FONT)  # Set font for button labels

        # Draw the sidebar initialization and background
        sidebar_rect = pygame.Rect(c.WINDOW_SIZE, 0, c.SIDEBAR_WIDTH, c.WINDOW_SIZE)
        pygame.draw.rect(screen, c.LIGHT_GREY, sidebar_rect)

        # Draw "Wall" button
        wall_button = pygame.Rect(c.BUTTON_X, c.WALL_Y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)  # Button rectangle
        wall_color = c.BLACK if self.selected_tool == "wall" else c.DARK_GREY  # Highlight if selected
        pygame.draw.rect(screen, wall_color, wall_button)
        wall_text = font.render("Wall", True, c.WHITE)  # antialiasing -> making the text smoother
        screen.blit(wall_text, (c.BUTTON_TEXT_X, c.WALL_TEXT_Y))  # Position text on the button

        # Draw "Eraser" button
        eraser_button = pygame.Rect(c.BUTTON_X, c.ERASER_Y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
        eraser_color = c.BLACK if self.selected_tool == "eraser" else c.DARK_GREY  # Highlight if selected
        pygame.draw.rect(screen, eraser_color, eraser_button)
        eraser_text = font.render("Eraser", True, c.WHITE)  # antialiasing -> making the text smoother
        screen.blit(eraser_text, (c.BUTTON_TEXT_X, c.ERASER_TEXT_Y))  # Position text on the button

        # Draw "Player" button
        player_button = pygame.Rect(c.BUTTON_X, c.PLAYER_Y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
        player_color = c.BLACK if self.selected_tool == "player" else c.DARK_GREY  # Highlight if selected
        pygame.draw.rect(screen, player_color, player_button)
        player_text = font.render("Player", True, c.WHITE)  # antialiasing -> making the text smoother
        screen.blit(player_text, (c.BUTTON_TEXT_X, c.PLAYER_TEXT_Y))  # Position text on the button

        # Draw the wifey button
        wifey_button = pygame.Rect(c.BUTTON_X, c.WIFEY_Y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
        wifey_color = c.BLACK if self.selected_tool == "wifey" else c.DARK_GREY  # Highlight if selected
        pygame.draw.rect(screen, wifey_color, wifey_button)
        wifey_text = font.render("Wifey", True, c.WHITE)  # antialiasing -> making the text smoother
        screen.blit(wifey_text, (c.BUTTON_TEXT_X, c.WIFEY_TEXT_Y))  # Position text on the button

        # Draw the lava button
        lava_button = pygame.Rect(c.BUTTON_X, c.LAVA_Y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
        lava_color = c.BLACK if self.selected_tool == "lava" else c.DARK_GREY  # Highlight if selected
        pygame.draw.rect(screen, lava_color, lava_button)
        lava_text = font.render("Lava", True, c.WHITE)  # antialiasing -> making the text smoother
        screen.blit(lava_text, (c.BUTTON_TEXT_X, c.LAVA_TEXT_Y))  # Position text on the button

        # Draw "Check Map" slider
        slider_rect = pygame.Rect(c.BUTTON_X, c.SLIDER_Y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
        pygame.draw.rect(screen, c.DARK_GREY, slider_rect, border_radius=20)
        circle_x = c.BUTTON_X + 20 if not self.check_map else c.BUTTON_X + c.BUTTON_WIDTH - 20
        circle_y = c.SLIDER_Y + c.BUTTON_HEIGHT // 2
        if self.check_map:
            circle_color = c.GREEN if valid_map else c.RED
        else:
            circle_color = c.WHITE
        pygame.draw.circle(screen, circle_color, (circle_x, circle_y), c.BUTTON_WIDTH // 4)
        slider_text = font.render("Check Map", True, c.BLACK)
        screen.blit(slider_text, (c.BUTTON_X - 10, c.SLIDER_Y - 20))

        button_list = [wall_button, eraser_button, player_button, wifey_button, slider_rect, lava_button]

        return button_list

    def toggle_check_map(self) -> None:
        self.check_map = not self.check_map  # Toggle the state

    def select_tool(self, tool: str) -> None:
        self.selected_tool = tool


class Game:
    def __init__(self):
        pygame.init()
        # self.grid_size = ask_input()
        self.grid_size = 10

        # Extend window width to fit the sidebar
        self.screen = pygame.display.set_mode((c.WINDOW_SIZE + c.SIDEBAR_WIDTH, c.WINDOW_SIZE))
        pygame.display.set_caption("Hercules finds his path underworld")
        self.grid = Grid(self.grid_size)
        self.sidebar = Sidebar()
        self.running = True
        self.mouse_held = False

        self.grid.update_violating_cells()

    def run(self) -> None:
        while self.running:
            self.screen.fill(c.WHITE)

            # Draw the grid and sidebar
            self.grid.draw(self.screen, self.sidebar.check_map)
            wall_button, eraser_button, player_button, wifey_button, slider_rect, lava_button = (
                self.sidebar.draw(self.screen, self.grid.valid_map))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_held = True
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # Check if a tool button is clicked
                    if wall_button.collidepoint(mouse_x, mouse_y):  # If click on "Wall" button
                        self.sidebar.select_tool("wall")
                    elif eraser_button.collidepoint(mouse_x, mouse_y):  # If click on "Eraser" button
                        self.sidebar.select_tool("eraser")
                    elif player_button.collidepoint(mouse_x, mouse_y):  # If click on "Player" button
                        self.sidebar.select_tool("player")
                    elif wifey_button.collidepoint(mouse_x, mouse_y):  # If click on "Wifey" button
                        self.sidebar.select_tool("wifey")
                    elif lava_button.collidepoint(mouse_x, mouse_y):  # If click on "Lava" button
                        self.sidebar.select_tool("lava")
                    elif slider_rect.collidepoint(mouse_x, mouse_y):  # If "Check Map" button is clicked
                        self.sidebar.toggle_check_map()

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_held = False

            # Handle drawing or erasing on the grid
            if self.mouse_held:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_x < c.WINDOW_SIZE:  # Only interact within the grid area, not the sidebar
                    grid_x, grid_y = mouse_x // self.grid.cell_size, mouse_y // self.grid.cell_size
                    if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                        self.grid.update_cell(grid_x, grid_y, self.sidebar.selected_tool)

            pygame.display.flip()  # Refresh the screen to show updates

        pygame.quit()  # Close the window and quit the game
        sys.exit()  # Exit the program


if __name__ == "__main__":
    game = Game()
    game.run()

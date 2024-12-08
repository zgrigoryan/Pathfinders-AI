import pygame
import sys
from pygame import Rect
import custom_constants as c
from typing import List, Tuple
from collections import deque
import time
import random
import csv
from utils import ask_input


class Grid:
    """
    Class to represent the grid and its properties.
    """

    def __init__(self, grid_size: int):
        self.monster_enabled = None
        self.hydra_heads = None
        self.hydra_position = None
        self.grid_size = grid_size
        self.cell_size = c.WINDOW_SIZE // grid_size
        self.grid = [[c.EMPTY_CELL_ID for _ in range(grid_size)] for _ in range(grid_size)]
        self.player_in_the_game = False
        self.goal_in_the_game = False
        self.valid_map = False
        self.violating_cells = set()

        self.path_to_display = None

        self.wall_image = self.upload_and_scale_image("./images/wall.jpeg")
        self.player_image = self.upload_and_scale_image("./images/hercules.jpeg")
        self.wifey_image = self.upload_and_scale_image("./images/wifey.jpeg")
        self.lava_image = self.upload_and_scale_image("./images/lava.jpg")
        self.mountain_image = self.upload_and_scale_image("./images/mountain.jpg")
        self.hidra_image = self.upload_and_scale_image("./images/hidra.jpg")

    def upload_and_scale_image(self, image_path: str) -> pygame.Surface:
        """
        Load and scale the image to the cell size.
        :param image_path: path to the image file
        :return: pygame object
        """
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (self.cell_size, self.cell_size))
        return image

    def update_violating_cells(self) -> None:
        """
        Highlight with red all the violations and check if the map is valid.
        :return: None
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
            player_enclosed = player_pos not in self.violating_cells
            goal_enclosed = goal_pos not in self.violating_cells

        self.valid_map = player_enclosed and goal_enclosed and self.player_in_the_game and self.goal_in_the_game
        if self.valid_map:
            self.violating_cells.clear()

    def draw(self, screen: pygame.Surface, check_map: bool, killed_hidras: List[Tuple[int, int]]) -> None:
        """
        Draw the grid on the screen, with all the elements.
        :param screen: pygame object
        :param check_map: if map is valid or no
        :param killed_hidras: list of positions where hydras were killed
        :return: None
        """
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
                elif self.grid[y][x] == c.MOUNTAIN_ID:
                    screen.blit(self.mountain_image, rect.topleft)
                elif self.grid[y][x] == c.HIDRA_ID:
                    screen.blit(self.hidra_image, rect.topleft)

                if check_map and (x, y) in self.violating_cells:
                    s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    s.fill(c.RED_WITH_TRANSPARENCY_ALPHA)  # Red color with alpha for transparency
                    screen.blit(s, rect.topleft)

                if self.path_to_display and (x, y) in self.path_to_display:
                    s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    s.fill(c.GREEN_WITH_TRANSPARENCY_ALPHA)  # Green overlay for the path
                    screen.blit(s, rect.topleft)

                pygame.draw.rect(screen, c.GREY, rect, c.GRID_WIDTH)

        # Draw killed hydras
        for hx, hy in killed_hidras:
            rect = pygame.Rect(hx * self.cell_size, hy * self.cell_size, self.cell_size, self.cell_size)
            screen.blit(self.hidra_image, rect.topleft)

    def display_path(self, path):
        self.path_to_display = path

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
        elif tool == "player" and not self.player_in_the_game:
            self.grid[y][x] = c.PLAYER_ID
            self.player_in_the_game = True
        elif tool == "wifey" and not self.goal_in_the_game:
            self.grid[y][x] = c.WIFEY_ID
            self.goal_in_the_game = True
        elif tool == "lava":
            self.grid[y][x] = c.LAVA_ID
        elif tool == "mountain":
            self.grid[y][x] = c.MOUNTAIN_ID
        elif tool == "hidra":  # Optional: allow placing hydra manually
            self.grid[y][x] = c.HIDRA_ID
            # Initialize hydra state
            self.hydra_position = (x, y)
            self.hydra_heads = 3

        self.update_violating_cells()

    def bfs(self, start, goal):
        """
        Perform BFS search from start to goal.
        :param start: (x, y) tuple
        :param goal: (x, y) tuple
        :return: path, runtime
        """
        from collections import deque
        start_time = time.perf_counter()
        queue = deque()
        queue.append((start, [start]))
        visited = set()
        visited.add(start)
        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == goal:
                runtime = time.perf_counter() - start_time
                return path, runtime
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    cell_id = self.grid[ny][nx]
                    if (nx, ny) not in visited and cell_id != c.WALL_ID and cell_id != c.HIDRA_ID:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + [(nx, ny)]))
        runtime = time.perf_counter() - start_time
        return None, runtime  # No path found

    def dfs(self, start, goal):
        """
        Perform DFS search from start to goal.
        :param start: (x, y) tuple
        :param goal: (x, y) tuple
        :return: path, runtime
        """
        start_time = time.perf_counter()
        stack = [(start, [start])]
        visited = set()
        visited.add(start)
        while stack:
            (x, y), path = stack.pop()
            if (x, y) == goal:
                runtime = time.perf_counter() - start_time
                return path, runtime
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    cell_id = self.grid[ny][nx]
                    if (nx, ny) not in visited and cell_id != c.WALL_ID and cell_id != c.HIDRA_ID:
                        visited.add((nx, ny))
                        stack.append(((nx, ny), path + [(nx, ny)]))
        runtime = time.perf_counter() - start_time
        return None, runtime  # No path found

    def ucs(self, start, goal):
        """
        Perform Uniform Cost Search from start to goal.
        :param start: (x, y) tuple
        :param goal: (x, y) tuple
        :return: path, runtime
        """
        import heapq
        start_time = time.perf_counter()
        heap = []
        heapq.heappush(heap, (0, start, [start]))
        visited = {start: 0}
        while heap:
            cost, (x, y), path = heapq.heappop(heap)
            if (x, y) == goal:
                runtime = time.perf_counter() - start_time
                return path, runtime
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    cell_id = self.grid[ny][nx]
                    cell_cost = c.CELL_COSTS.get(cell_id, 1)
                    if cell_cost == float('inf'):
                        continue  # Skip impassable cells
                    new_cost = cost + cell_cost
                    if (nx, ny) not in visited or new_cost < visited[(nx, ny)]:
                        visited[(nx, ny)] = new_cost
                        heapq.heappush(heap, (new_cost, (nx, ny), path + [(nx, ny)]))
        runtime = time.perf_counter() - start_time
        return None, runtime  # No path found

    def astar(self, start, goal):
        """
        Perform A* Search from start to goal using Manhattan distance heuristic.
        :param start: (x, y) tuple
        :param goal: (x, y) tuple
        :return: path, runtime
        """
        import heapq
        start_time = time.perf_counter()
        heap = []
        h = lambda x, y: abs(x - goal[0]) + abs(y - goal[1])
        heapq.heappush(heap, (h(*start), 0, start, [start]))
        visited = {start: 0}
        while heap:
            estimated_total_cost, cost_so_far, (x, y), path = heapq.heappop(heap)
            if (x, y) == goal:
                runtime = time.perf_counter() - start_time
                return path, runtime
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    cell_id = self.grid[ny][nx]
                    cell_cost = c.CELL_COSTS.get(cell_id, 1)
                    if cell_cost == float('inf'):
                        continue  # Skip impassable cells
                    new_cost_so_far = cost_so_far + cell_cost
                    if (nx, ny) not in visited or new_cost_so_far < visited[(nx, ny)]:
                        visited[(nx, ny)] = new_cost_so_far
                        estimated_total_cost = new_cost_so_far + h(nx, ny)
                        heapq.heappush(heap, (estimated_total_cost, new_cost_so_far, (nx, ny), path + [(nx, ny)]))
        runtime = time.perf_counter() - start_time
        return None, runtime

    def create_auto_map(self,
                        player_pos: Tuple[int, int],
                        goal_pos: Tuple[int, int],
                        place_obstacles: bool = True,
                        monster_enabled: bool = c.HIDRA_ENABLED) -> None:
        """
        Automatically create a map with:
        1. Walls on boundaries.
        2. Player and goal at given positions.
        3. Optionally place obstacles ensuring a path remains possible.
        """
        # Clear grid
        self.grid = [[c.EMPTY_CELL_ID for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.player_in_the_game = False
        self.goal_in_the_game = False
        self.monster_enabled = monster_enabled

        # Place boundary walls
        for x in range(self.grid_size):
            self.grid[0][x] = c.WALL_ID
            self.grid[self.grid_size - 1][x] = c.WALL_ID
        for y in range(self.grid_size):
            self.grid[y][0] = c.WALL_ID
            self.grid[y][self.grid_size - 1] = c.WALL_ID

        # Place player and goal
        px, py = player_pos
        gx, gy = goal_pos
        self.grid[py][px] = c.PLAYER_ID
        self.player_in_the_game = True
        self.grid[gy][gx] = c.WIFEY_ID
        self.goal_in_the_game = True

        # Update after placing player and goal
        self.update_violating_cells()

        if place_obstacles:
            # Attempt to place obstacles while ensuring a path exists
            obstacle_types = [c.LAVA_ID, c.MOUNTAIN_ID]
            attempts = 0
            max_attempts = c.MAX_ATTEMPTS
            path_exists = False

            while attempts < max_attempts:
                # Clear internal cells first
                for yy in range(1, self.grid_size - 1):
                    for xx in range(1, self.grid_size - 1):
                        if (xx, yy) not in [player_pos, goal_pos]:
                            self.grid[yy][xx] = c.EMPTY_CELL_ID

                num_internal_cells = (self.grid_size - 2) * (self.grid_size - 2)
                num_obstacles = num_internal_cells // 2  # 50% of internal cells are obstacles

                placed = 0
                while placed < num_obstacles:
                    ox = random.randint(1, self.grid_size - 2)
                    oy = random.randint(1, self.grid_size - 2)
                    if (ox, oy) not in [player_pos, goal_pos] and self.grid[oy][ox] == c.EMPTY_CELL_ID:
                        self.grid[oy][ox] = random.choice(obstacle_types)
                        placed += 1

                # Check if a path exists
                path, _ = self.bfs(player_pos, goal_pos)
                if path:
                    path_exists = True
                    break
                else:
                    attempts += 1

            if not path_exists:
                # Clear obstacles if no path found
                for yy in range(1, self.grid_size - 1):
                    for xx in range(1, self.grid_size - 1):
                        if (xx, yy) not in [player_pos, goal_pos]:
                            self.grid[yy][xx] = c.EMPTY_CELL_ID
        if self.monster_enabled:
            # Place Hydra in a random internal cell not occupied by player/goal/obstacle
            while True:
                hx = random.randint(1, self.grid_size - 2)
                hy = random.randint(1, self.grid_size - 2)
                if self.grid[hy][hx] == c.EMPTY_CELL_ID:
                    self.grid[hy][hx] = c.HIDRA_ID
                    # Store hydra state
                    self.hydra_position = (hx, hy)
                    self.hydra_heads = 3
                    break
        else:
            self.hydra_position = None
            self.hydra_heads = 0

        # Place water bottle always
        # while True:
        #     wx = random.randint(1, self.grid_size - 2)
        #     wy = random.randint(1, self.grid_size - 2)
        #     if self.grid[wy][wx] == c.EMPTY_CELL_ID:
        #         self.grid[wy][wx] = c.WATER_ID
        #         self.water_position = (wx, wy)
        #         break

        self.update_violating_cells()


class Sidebar:
    def __init__(self):
        self.selected_tool = "wall"
        self.check_map = False

    def draw(self, screen: pygame.Surface, valid_map: bool, search_results=None, current_algorithm=None) -> Tuple[
        List[Rect], Rect, Rect]:
        """
        Draws a sidebar with tool buttons and a "Check Map" slider.

        :param screen: pygame screen surface
        :param valid_map: whether the current map is valid
        :param search_results: dictionary of search algorithm runtimes
        :param current_algorithm: the current algorithm being displayed
        :return: wall_button and eraser_button as Rect objects for collision detection
        """
        font = pygame.font.Font(None, c.PYGAME_FONT)  # Set font for button labels

        # Draw the sidebar background
        sidebar_rect = pygame.Rect(c.WINDOW_SIZE, 0, c.SIDEBAR_WIDTH, c.WINDOW_SIZE)
        pygame.draw.rect(screen, c.LIGHT_GREY, sidebar_rect)

        # Draw tool buttons
        tool_buttons = []
        current_y = c.SIDEBAR_PADDING
        for label in c.BUTTON_LABELS:
            button_rect = pygame.Rect(c.BUTTON_X, current_y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
            button_color = c.BLACK if self.selected_tool == label.lower() else c.DARK_GREY
            pygame.draw.rect(screen, button_color, button_rect)

            button_text = font.render(label, True, c.WHITE)
            text_x = c.BUTTON_X + (c.BUTTON_WIDTH - button_text.get_width()) // 2
            text_y = current_y + (c.BUTTON_HEIGHT - button_text.get_height()) // 2
            screen.blit(button_text, (text_x, text_y))

            tool_buttons.append(button_rect)
            current_y += c.BUTTON_HEIGHT + c.BUTTON_SPACING

        # Draw "Check Map" slider
        slider_rect = self.draw_slider(screen, font, valid_map)
        current_y += c.BUTTON_SPACING + c.BUTTON_HEIGHT  # Move y-position below the slider

        # Draw "RUN" button always, but change its appearance based on validity
        run_button_rect = pygame.Rect(c.BUTTON_X, c.RUN_BUTTON_Y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
        if self.check_map and valid_map:
            run_button_color = c.BLUE  # Active RUN button color
            run_button_text_color = c.WHITE
        else:
            run_button_color = c.DARK_GREY  # Inactive RUN button color
            run_button_text_color = c.LIGHT_GREY

        pygame.draw.rect(screen, run_button_color, run_button_rect, border_radius=5)

        run_button_text = font.render("RUN", True, run_button_text_color)
        text_x = run_button_rect.x + (c.BUTTON_WIDTH - run_button_text.get_width()) // 2
        text_y = run_button_rect.y + (c.BUTTON_HEIGHT - run_button_text.get_height()) // 2
        screen.blit(run_button_text, (text_x, text_y))

        # Add a border to indicate it's clickable when active
        if self.check_map and valid_map:
            pygame.draw.rect(screen, c.GREEN, run_button_rect, 2, border_radius=5)

        if search_results:
            result_font = pygame.font.Font(None, c.RESULT_FONT_SIZE)
            for alg_name, runtime in search_results.items():
                result_text = f"{alg_name}: {runtime}"  # runtime is already formatted
                result_surface = result_font.render(result_text, True, c.BLACK)
                text_x = c.BUTTON_X
                screen.blit(result_surface, (text_x, current_y))
                current_y += result_surface.get_height() + 5  # Adjust spacing as needed

        current_y += 10  # Add some padding before displaying the current algorithm
        if current_algorithm:
            algorithm_font = pygame.font.Font(None, c.RESULT_FONT_SIZE)
            algorithm_text = f"Displaying {current_algorithm}"
            algorithm_surface = algorithm_font.render(algorithm_text, True, c.BLACK)
            text_x = c.BUTTON_X
            screen.blit(algorithm_surface, (text_x, current_y))
            current_y += algorithm_surface.get_height() + 5  # Adjust spacing as needed

            # Instruction to the user
            instruction_font = pygame.font.Font(None, c.RESULT_FONT_SIZE)
            instruction_text = "Press SPACE"
            instruction_surface = instruction_font.render(instruction_text, True, c.BLACK)
            screen.blit(instruction_surface, (text_x, current_y))
            current_y += instruction_surface.get_height() + 5

        return tool_buttons, slider_rect, run_button_rect

    def draw_slider(self, screen: pygame.Surface, font: pygame.font.Font, valid_map: bool) -> Rect:
        """
        Draws the "Check Map" slider below the tool buttons.

        :param screen: pygame screen surface
        :param font: pygame font object
        :param valid_map: whether the current map is valid
        :return: slider Rect for collision detection
        """

        slider_rect = pygame.Rect(c.BUTTON_X, c.MAP_CHECK_Y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
        pygame.draw.rect(screen, c.DARK_GREY, slider_rect, border_radius=20)

        circle_x = slider_rect.x + 20 if not self.check_map else slider_rect.x + c.BUTTON_WIDTH - 20
        circle_y = slider_rect.y + c.BUTTON_HEIGHT // 2

        # Set circle color based on the state and map validity
        if self.check_map:
            circle_color = c.GREEN if valid_map else c.RED
        else:
            circle_color = c.WHITE

        pygame.draw.circle(screen, circle_color, (circle_x, circle_y), c.BUTTON_WIDTH // 4)

        # Draw slider label
        slider_text = font.render("Check Map", True, c.BLACK)
        text_x = slider_rect.x + (c.BUTTON_WIDTH - slider_text.get_width()) // 2
        text_y = slider_rect.y - 25  # Adjust as needed for spacing
        screen.blit(slider_text, (text_x, text_y))

        return slider_rect

    def toggle_check_map(self) -> None:
        self.check_map = not self.check_map  # Toggle the state

    def select_tool(self, tool: str) -> None:
        self.selected_tool = tool


class Game:
    ALGORITHM_METHOD_MAPPING = {
        'UCS': 'ucs',
        'A*': 'astar'
    }

    def __init__(self, auto_map: bool = True, experiment: bool = False):
        self.search_paths = None
        self.search_results = None
        pygame.init()
        self.grid_size = c.GRID_SIZE
        # Ask for grid size if not in experiment mode
        if not experiment:
            self.grid_size = ask_input()

        # Extend window width to fit the sidebar
        self.screen = pygame.display.set_mode((c.WINDOW_SIZE + c.SIDEBAR_WIDTH, c.WINDOW_SIZE))
        pygame.display.set_caption("Hercules finds his path underworld")
        self.grid = Grid(self.grid_size)
        self.sidebar = Sidebar()
        self.running = True
        self.mouse_held = False
        self.experiment = experiment

        # Initialize hydra_killed flag and list of killed hydras
        self.hydra_killed = False
        self.killed_hidras = []

        # Helper function to generate random internal positions
        def random_internal_position(grid_size):
            return random.randint(1, grid_size - 2), random.randint(1, grid_size - 2)

        if not experiment:
            # Automatically create map with random player and goal positions if auto_map is True
            if auto_map:
                player_pos = random_internal_position(self.grid_size)
                goal_pos = random_internal_position(self.grid_size)
                while goal_pos == player_pos:
                    goal_pos = random_internal_position(self.grid_size)

                self.grid.create_auto_map(player_pos, goal_pos, place_obstacles=True)

            self.grid.update_violating_cells()
            self.search_paths = None
            self.search_results = None

        self.displaying_paths = False
        self.algorithms_list = ['BFS', 'DFS', 'UCS', 'A*']
        self.current_algorithm_index = 0
        self.search_paths = {}

    def run(self) -> None:
        if self.experiment:
            self.run_experiments()
            return

        while self.running:
            self.screen.fill(c.WHITE)
            self.grid.draw(self.screen, self.sidebar.check_map, self.killed_hidras)

            current_algorithm = None
            if self.displaying_paths:
                current_algorithm = self.algorithms_list[self.current_algorithm_index]

            # Draw the sidebar and get tool buttons, slider_rect, and run_button_rect
            if hasattr(self, 'search_results'):
                tool_buttons, slider, run_button = self.sidebar.draw(
                    self.screen,
                    self.grid.valid_map,
                    self.search_results,
                    current_algorithm
                )
            else:
                tool_buttons, slider, run_button = self.sidebar.draw(
                    self.screen,
                    self.grid.valid_map,
                    current_algorithm=current_algorithm
                )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.displaying_paths:
                        # Proceed to the next algorithm's path
                        self.current_algorithm_index += 1
                        if self.current_algorithm_index < len(self.algorithms_list):
                            current_algorithm = self.algorithms_list[self.current_algorithm_index]
                            self.grid.display_path(self.search_paths.get(current_algorithm))
                        else:
                            # No more algorithms; stop displaying paths
                            self.displaying_paths = False
                            self.grid.display_path(None)  # Clear the path

                        # If hydra was killed, remove it from the grid
                        if self.hydra_killed and self.current_algorithm_index > 1:
                            self.remove_dead_hidras()
                            self.hydra_killed = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_held = True
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # Check if a tool button is clicked
                    tool_clicked = False
                    for index, button_rect in enumerate(tool_buttons):
                        if button_rect.collidepoint(mouse_x, mouse_y):
                            selected_tool = c.BUTTON_LABELS[index].lower()
                            self.sidebar.select_tool(selected_tool)
                            tool_clicked = True
                            break  # Exit after handling the button click

                    if not tool_clicked:
                        # Check if slider was clicked
                        if slider.collidepoint(mouse_x, mouse_y):
                            self.sidebar.toggle_check_map()
                        # Check if RUN button was clicked and is active
                        elif run_button.collidepoint(mouse_x, mouse_y):
                            if self.sidebar.check_map and self.grid.valid_map:
                                self.run_game()
                            else:
                                print("RUN button is inactive. Please ensure the map is valid and checked.")

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_held = False

            # Handle drawing/erasing on the grid
            if self.mouse_held:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_x < c.WINDOW_SIZE:  # Only interact within the grid area
                    grid_x, grid_y = mouse_x // self.grid.cell_size, mouse_y // self.grid.cell_size
                    if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                        self.grid.update_cell(grid_x, grid_y, self.sidebar.selected_tool)
                        # Clear the displayed path and reset variables
                        self.displaying_paths = False
                        self.grid.display_path(None)
                        if hasattr(self, 'search_results'):
                            del self.search_results

            pygame.display.flip()  # Refresh the screen to show updates

        pygame.quit()  # Close the window and quit the game
        sys.exit()  # Exit the program

    # After generating map, compute energy:
    def run_game(self):
        print("RUN button clicked! Starting the game...")

        # Get the player and goal positions
        player_pos = None
        goal_pos = None
        for y in range(self.grid.grid_size):
            for x in range(self.grid.grid_size):
                if self.grid.grid[y][x] == c.PLAYER_ID:
                    player_pos = (x, y)
                elif self.grid.grid[y][x] == c.WIFEY_ID:
                    goal_pos = (x, y)
                if player_pos and goal_pos:
                    break
            if player_pos and goal_pos:
                break

        if not player_pos or not goal_pos:
            print("Player or goal not found.")
            return

        # Compute the initial energy:
        # energy = grid_size²
        self.energy = self.grid_size ** 2

        # Store energy for UCS and A*
        self.search_energy = {}  # { 'UCS': leftover_energy or None, 'A*': leftover_energy or None }

        self.perform_searches(player_pos, goal_pos)

    def compute_path_cost(self, path):
        # path is a list of (x,y)
        # sum the CELL_COSTS for each cell in path
        cost = 0
        for (x, y) in path:
            cell_id = self.grid.grid[y][x]
            cost += c.CELL_COSTS.get(cell_id, 1)
        return cost

    # In the Sidebar draw method, we will show energy only for UCS or A* if available.
    # Modify the draw method or create a method to show energy when current algorithm is UCS or A*.

    def draw(self, screen: pygame.Surface, valid_map: bool, search_results=None, current_algorithm=None) -> Tuple[
        List[Rect], Rect, Rect]:
        font = pygame.font.Font(None, c.PYGAME_FONT)  # Set font for button labels
        sidebar_rect = pygame.Rect(c.WINDOW_SIZE, 0, c.SIDEBAR_WIDTH, c.WINDOW_SIZE)
        pygame.draw.rect(screen, c.LIGHT_GREY, sidebar_rect)

        tool_buttons = []
        current_y = c.SIDEBAR_PADDING
        for label in c.BUTTON_LABELS:
            button_rect = pygame.Rect(c.BUTTON_X, current_y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
            button_color = c.BLACK if self.selected_tool == label.lower() else c.DARK_GREY
            pygame.draw.rect(screen, button_color, button_rect)

            button_text = font.render(label, True, c.WHITE)
            text_x = c.BUTTON_X + (c.BUTTON_WIDTH - button_text.get_width()) // 2
            text_y = current_y + (c.BUTTON_HEIGHT - button_text.get_height()) // 2
            screen.blit(button_text, (text_x, text_y))

            tool_buttons.append(button_rect)
            current_y += c.BUTTON_HEIGHT + c.BUTTON_SPACING

        # Draw "Check Map" slider
        slider_rect = self.draw_slider(screen, font, valid_map)
        current_y += c.BUTTON_SPACING + c.BUTTON_HEIGHT

        run_button_rect = pygame.Rect(c.BUTTON_X, c.RUN_BUTTON_Y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
        if self.check_map and valid_map:
            run_button_color = c.BLUE  # Active RUN button color
            run_button_text_color = c.WHITE
        else:
            run_button_color = c.DARK_GREY  # Inactive RUN button color
            run_button_text_color = c.LIGHT_GREY

        pygame.draw.rect(screen, run_button_color, run_button_rect, border_radius=5)
        run_button_text = font.render("RUN", True, run_button_text_color)
        text_x = run_button_rect.x + (c.BUTTON_WIDTH - run_button_text.get_width()) // 2
        text_y = run_button_rect.y + (c.BUTTON_HEIGHT - run_button_text.get_height()) // 2
        screen.blit(run_button_text, (text_x, text_y))

        if self.check_map and valid_map:
            pygame.draw.rect(screen, c.GREEN, run_button_rect, 2, border_radius=5)

        if search_results:
            result_font = pygame.font.Font(None, c.RESULT_FONT_SIZE)
            for alg_name, result in search_results.items():
                # If current_algorithm is UCS or A*, and we are currently displaying that algorithm,
                # we show energy or "Energy < 0". For BFS/DFS, we show time as before.

                result_text = f"{alg_name}: {result}"
                result_surface = result_font.render(result_text, True, c.BLACK)
                text_x = c.BUTTON_X
                screen.blit(result_surface, (text_x, current_y))
                current_y += result_surface.get_height() + 5

        current_y += 10
        if current_algorithm:
            algorithm_font = pygame.font.Font(None, c.RESULT_FONT_SIZE)
            algorithm_text = f"Displaying {current_algorithm}"
            algorithm_surface = algorithm_font.render(algorithm_text, True, c.BLACK)
            text_x = c.BUTTON_X
            screen.blit(algorithm_surface, (text_x, current_y))
            current_y += algorithm_surface.get_height() + 5

            # Instruction to the user
            instruction_font = pygame.font.Font(None, c.RESULT_FONT_SIZE)
            instruction_text = "Press SPACE"
            instruction_surface = instruction_font.render(instruction_text, True, c.BLACK)
            screen.blit(instruction_surface, (text_x, current_y))
            current_y += instruction_surface.get_height() + 5

        return tool_buttons, slider_rect, run_button_rect

    # When space is pressed and we cycle through algorithms, after finishing, we must clear energy display.
    # In the event loop:
    # After finishing viewing all paths (self.displaying_paths = False), we no longer show energy.
    # This is already handled since we show energy only while displaying_paths = True and have current_algorithm.

    # Also, when RUN button is clicked again (run_game called again), we recalculate energy and reset search_results
    # and search_energy.
    # This will ensure a fresh start each time.

    def perform_searches(self, player_pos, goal_pos):
        # Run BFS and DFS as before
        bfs_path, bfs_runtime = self.grid.bfs(player_pos, goal_pos)
        dfs_path, dfs_runtime = self.grid.dfs(player_pos, goal_pos)

        # BFS/DFS store runtime results
        self.search_results = {
            'BFS': f"{bfs_runtime * 1000:.2f} ms" if bfs_runtime is not None else "FAIL",
            'DFS': f"{dfs_runtime * 1000:.2f} ms" if dfs_runtime is not None else "FAIL",
            'UCS': "FAIL",
            'A*': "FAIL"
        }

        self.search_paths = {
            'BFS': bfs_path,
            'DFS': dfs_path,
            'UCS': None,
            'A*': None
        }

        # For UCS and A*, we consider energy and might need to kill the hydra if no path is found.
        for algorithm in ['UCS', 'A*']:
            method_name = self.ALGORITHM_METHOD_MAPPING.get(algorithm)
            if not method_name:
                continue
            search_method = getattr(self.grid, method_name, None)
            if not search_method:
                continue

            path, runtime = search_method(player_pos, goal_pos)
            if path:
                # Compute the path cost
                path_cost = self.compute_path_cost(path)
                leftover_energy = self.energy - path_cost
                if leftover_energy >= 0:
                    # Success: Show leftover energy AND time
                    self.search_results[algorithm] = f"Energy: {leftover_energy}, Time: {runtime * 1000:.2f} ms"
                    self.search_paths[algorithm] = path
                    self.search_energy[algorithm] = leftover_energy
                else:
                    # Path found but not enough energy
                    self.search_results[algorithm] = f"Energy < 0, Time: {runtime * 1000:.2f} ms"
                    self.search_paths[algorithm] = None
                    self.search_energy[algorithm] = None
            else:
                # No path found initially, attempt to kill hydra multiple times
                print(f"{algorithm} failed to find a path. Attempting to kill the Hydra...")
                attempts = 0
                success = False
                while attempts < 10:
                    killed = self.try_kill_hydra()
                    if killed:
                        print(f"Hydra killed on attempt {attempts + 1}. Re-running {algorithm}...")
                        # Re-run the search after killing hydra
                        path, runtime = search_method(player_pos, goal_pos)
                        if path:
                            path_cost = self.compute_path_cost(path)
                            leftover_energy = self.energy - path_cost
                            if leftover_energy >= 0:
                                self.search_results[
                                    algorithm] = f"Energy: {leftover_energy}, Time: {runtime * 1000:.2f} ms"
                                self.search_paths[algorithm] = path
                                self.search_energy[algorithm] = leftover_energy
                            else:
                                self.search_results[algorithm] = f"Energy < 0, Time: {runtime * 1000:.2f} ms"
                                self.search_paths[algorithm] = None
                                self.search_energy[algorithm] = None
                            success = True
                            self.hydra_killed = True
                            break
                        else:
                            # Even after killing Hydra, no path was found. This should be rare unless map is blocked.
                            print("No path found even after Hydra was killed.")
                            break
                    else:
                        print(f"Failed to kill Hydra on attempt {attempts + 1}.")
                    attempts += 1

                if not success:
                    # Even after attempts, we couldn't kill hydra or find path
                    self.search_results[algorithm] = "FAIL"
                    self.search_paths[algorithm] = None

        self.displaying_paths = True
        self.current_algorithm_index = 0
        self.algorithms_list = ['BFS', 'DFS', 'UCS', 'A*']

        current_algorithm = self.algorithms_list[self.current_algorithm_index]
        self.grid.display_path(self.search_paths.get(current_algorithm))

        print("Search algorithm results:")
        for alg, res in self.search_results.items():
            print(f"{alg}: {res}")

    def run_experiments(self, runs=100, grid_size=c.GRID_SIZE):
        # Helper function to generate random internal positions
        def random_internal_position(gs):
            return random.randint(1, gs - 2), random.randint(1, gs - 2)

        # Results file
        results_file = "results.csv"
        fieldnames = ["Run_number", "BFS", "DFS", "UCS", "A*"]

        # Write header
        with open(results_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

        for i in range(1, runs + 1):
            player_pos = random_internal_position(grid_size)
            goal_pos = random_internal_position(grid_size)
            while goal_pos == player_pos:
                goal_pos = random_internal_position(grid_size)

            # Create new map
            self.grid = Grid(grid_size)
            self.grid.create_auto_map(player_pos, goal_pos, place_obstacles=True)

            # If map isn't valid after generation, just continue
            if not self.grid.valid_map:
                continue

            # Run searches
            _, bfs_runtime = self.grid.bfs(player_pos, goal_pos)
            _, dfs_runtime = self.grid.dfs(player_pos, goal_pos)
            _, ucs_runtime = self.grid.ucs(player_pos, goal_pos)
            _, astar_runtime = self.grid.astar(player_pos, goal_pos)

            # Save results to CSV in the requested format
            with open(results_file, "a", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({
                    "Run_number": i,
                    "BFS": bfs_runtime,
                    "DFS": dfs_runtime,
                    "UCS": ucs_runtime,
                    "A*": astar_runtime
                })

        print(f"Experiment completed. Results saved to {results_file}")

    def try_kill_hydra(self):
        """
        Attempt to kill the hydra. Probability of success = 1/(hydra_heads).
        If failed, hydra_heads += 1.
        Returns True if killed, False if not.
        """
        if not self.grid.hydra_position:
            return True  # No hydra present

        success_prob = 1.0 / self.grid.hydra_heads
        if random.random() < success_prob:
            # Successfully killed the hydra
            hx, hy = self.grid.hydra_position
            self.grid.grid[hy][hx] = c.EMPTY_CELL_ID  # Mark as empty cell
            self.killed_hidras.append((hx, hy))  # Add to killed hydras list for display
            self.grid.hydra_position = None
            self.grid.hydra_heads = 0
            print("Hydra has been killed!")
            return True
        else:
            # Failed attempt, hydra grows more heads
            self.grid.hydra_heads += 1
            print(f"Hydra evaded! It now has {self.grid.hydra_heads} heads.")
            return False

    def remove_dead_hidras(self):
        """
        Remove all killed Hydras from the killed_hidras list.
        Since the grid cells are already set to EMPTY, nothing else is needed.
        """
        if self.killed_hidras:
            for hx, hy in self.killed_hidras:
                # They are already set to EMPTY_CELL_ID in try_kill_hydra
                print(f"Removed killed Hydra at ({hx}, {hy})")
            self.killed_hidras.clear()


if __name__ == "__main__":
    # Check for arguments
    auto_map = True
    experiment = False
    if "--no-auto-map" in sys.argv:
        auto_map = False
    if "--experiment" in sys.argv:
        experiment = True

    game = Game(auto_map=auto_map, experiment=experiment)
    game.run()

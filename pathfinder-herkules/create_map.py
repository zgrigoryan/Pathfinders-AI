import pygame
import sys
from pygame import Rect
import custom_constants as c
from typing import List, Tuple
from collections import deque
import time
import random

class Grid:
    """
    Class to represent the grid and its properties.
    """
    def __init__(self, grid_size: int):
        self.grid_size = grid_size
        self.cell_size = c.WINDOW_SIZE // grid_size
        self.grid = [[c.EMPTY_CELL_ID for _ in range(grid_size)] for _ in range(grid_size)]
        self.player_in_the_game = False
        self.goal_in_the_game = False
        self.valid_map = False
        self.violating_cells = set()

        # Load and scale images
        self.wall_image = self.upload_and_scale_image("./images/wall.jpeg")
        self.player_image = self.upload_and_scale_image("./images/hercules.jpeg")
        self.wifey_image = self.upload_and_scale_image("./images/wifey.jpeg")
        self.lava_image = self.upload_and_scale_image("./images/lava.jpg")
        self.mountain_image = self.upload_and_scale_image("./images/mountain.jpg")

    def upload_and_scale_image(self, image_path: str) -> pygame.Surface:
        """
        Load and scale the image to the cell size.
        """
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (self.cell_size, self.cell_size))
        return image

    def update_violating_cells(self) -> None:
        """
        Highlight with red all the violations and check if the map is valid.
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

    def draw(self, screen: pygame.Surface, check_map: bool) -> None:
        """
        Draw the grid on the screen.
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

                if check_map and (x, y) in self.violating_cells:
                    s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    s.fill((255, 0, 0, 100))  # Red with transparency
                    screen.blit(s, rect.topleft)

                pygame.draw.rect(screen, c.GREY, rect, c.GRID_WIDTH)

    def update_cell(self, x: int, y: int, tool: str) -> None:
        """
        Update the cell based on the selected tool.
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

        self.update_violating_cells()

    def bfs(self, start, goal):
        """
        Perform BFS search from start to goal.
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
                    if (nx, ny) not in visited and self.grid[ny][nx] != c.WALL_ID:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + [(nx, ny)]))
        runtime = time.perf_counter() - start_time
        return None, runtime

    def dfs(self, start, goal):
        """
        Perform DFS search from start to goal.
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
                    if (nx, ny) not in visited and self.grid[ny][nx] != c.WALL_ID:
                        visited.add((nx, ny))
                        stack.append(((nx, ny), path + [(nx, ny)]))
        runtime = time.perf_counter() - start_time
        return None, runtime

    def ucs(self, start, goal):
        """
        Perform Uniform Cost Search from start to goal.
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
                        continue
                    new_cost = cost + cell_cost
                    if (nx, ny) not in visited or new_cost < visited[(nx, ny)]:
                        visited[(nx, ny)] = new_cost
                        heapq.heappush(heap, (new_cost, (nx, ny), path + [(nx, ny)]))
        runtime = time.perf_counter() - start_time
        return None, runtime

    def astar(self, start, goal):
        """
        Perform A* Search from start to goal using Manhattan distance heuristic.
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
                        continue
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
                        place_obstacles: bool = True) -> None:
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
            max_attempts = 20
            path_exists = False

            while attempts < max_attempts:
                # Clear internal cells first
                for yy in range(1, self.grid_size - 1):
                    for xx in range(1, self.grid_size - 1):
                        if (xx, yy) not in [player_pos, goal_pos]:
                            self.grid[yy][xx] = c.EMPTY_CELL_ID

                # Place a small number of obstacles randomly
                num_internal_cells = (self.grid_size - 2) * (self.grid_size - 2)
                num_obstacles = num_internal_cells // 10  # ~10%

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

        self.update_violating_cells()


class Sidebar:
    def __init__(self):
        self.selected_tool = "wall"
        self.check_map = False

    def draw(self, screen: pygame.Surface, valid_map: bool, search_results=None) -> Tuple[List[Rect], Rect, Rect]:
        font = pygame.font.Font(None, c.PYGAME_FONT)

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

        slider_rect = self.draw_slider(screen, font, valid_map)
        current_y += c.BUTTON_SPACING + c.BUTTON_HEIGHT

        run_button_rect = pygame.Rect(c.BUTTON_X, c.RUN_BUTTON_Y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
        if self.check_map and valid_map:
            run_button_color = c.BLUE
            run_button_text_color = c.WHITE
        else:
            run_button_color = c.DARK_GREY
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
            for alg_name, runtime in search_results.items():
                result_text = f"{alg_name}: {runtime * 1000:.2f} ms"
                result_surface = result_font.render(result_text, True, c.BLACK)
                text_x = c.BUTTON_X
                screen.blit(result_surface, (text_x, current_y))
                current_y += result_surface.get_height() + 5

        return tool_buttons, slider_rect, run_button_rect

    def draw_slider(self, screen: pygame.Surface, font: pygame.font.Font, valid_map: bool) -> Rect:
        slider_rect = pygame.Rect(c.BUTTON_X, c.MAP_CHECK_Y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
        pygame.draw.rect(screen, c.DARK_GREY, slider_rect, border_radius=20)

        circle_x = slider_rect.x + 20 if not self.check_map else slider_rect.x + c.BUTTON_WIDTH - 20
        circle_y = slider_rect.y + c.BUTTON_HEIGHT // 2

        if self.check_map:
            circle_color = c.GREEN if valid_map else c.RED
        else:
            circle_color = c.WHITE

        pygame.draw.circle(screen, circle_color, (circle_x, circle_y), c.BUTTON_WIDTH // 4)

        slider_text = font.render("Check Map", True, c.BLACK)
        text_x = slider_rect.x + (c.BUTTON_WIDTH - slider_text.get_width()) // 2
        text_y = slider_rect.y - 25
        screen.blit(slider_text, (text_x, text_y))

        return slider_rect

    def toggle_check_map(self) -> None:
        self.check_map = not self.check_map

    def select_tool(self, tool: str) -> None:
        self.selected_tool = tool


class Game:
    def __init__(self, auto_map: bool = True):
        pygame.init()
        self.grid_size = 50
        self.screen = pygame.display.set_mode((c.WINDOW_SIZE + c.SIDEBAR_WIDTH, c.WINDOW_SIZE))
        pygame.display.set_caption("Hercules finds his path underworld")
        self.grid = Grid(self.grid_size)
        self.sidebar = Sidebar()
        self.running = True
        self.mouse_held = False

        # Automatically create map if auto_map is True
        if auto_map:
            player_pos = (1, self.grid_size - 2)  # Player at lower-left inside the boundary
            goal_pos = (self.grid_size - 2, 1)    # Goal at upper-right inside the boundary
            self.grid.create_auto_map(player_pos, goal_pos, place_obstacles=True)

        self.grid.update_violating_cells()
        self.search_paths = None
        self.search_results = None

    def run(self) -> None:
        while self.running:
            self.screen.fill(c.WHITE)
            self.grid.draw(self.screen, self.sidebar.check_map)

            if hasattr(self, 'search_results'):
                tool_buttons, slider, run_button = self.sidebar.draw(self.screen,
                                                                     self.grid.valid_map,
                                                                     self.search_results)
            else:
                tool_buttons, slider, run_button = self.sidebar.draw(self.screen, self.grid.valid_map)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
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
                            break

                    if not tool_clicked:
                        # Check slider
                        if slider.collidepoint(mouse_x, mouse_y):
                            self.sidebar.toggle_check_map()
                        # Check RUN button
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
                if mouse_x < c.WINDOW_SIZE:  # Only interact within grid area
                    grid_x, grid_y = mouse_x // self.grid.cell_size, mouse_y // self.grid.cell_size
                    if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                        self.grid.update_cell(grid_x, grid_y, self.sidebar.selected_tool)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def run_game(self):
        print("RUN button clicked! Starting the game...")

        # Get player and goal positions
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

        # Run searches
        bfs_path, bfs_runtime = self.grid.bfs(player_pos, goal_pos)
        dfs_path, dfs_runtime = self.grid.dfs(player_pos, goal_pos)
        ucs_path, ucs_runtime = self.grid.ucs(player_pos, goal_pos)
        astar_path, astar_runtime = self.grid.astar(player_pos, goal_pos)

        self.search_results = {
            'BFS': bfs_runtime,
            'DFS': dfs_runtime,
            'UCS': ucs_runtime,
            'A*': astar_runtime
        }

        self.search_paths = {
            'BFS': bfs_path,
            'DFS': dfs_path,
            'UCS': ucs_path,
            'A*': astar_path
        }

        print("Search algorithm runtimes:")
        for alg, runtime in self.search_results.items():
            print(f"{alg}: {runtime:.6f} seconds")


if __name__ == "__main__":
    # Check for --no-auto-map argument
    auto_map = True
    if "--no-auto-map" in sys.argv:
        auto_map = False
    game = Game(auto_map=auto_map)
    game.run()

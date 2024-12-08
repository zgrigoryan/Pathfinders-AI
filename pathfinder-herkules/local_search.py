import random
import time
import csv
import os
from create_map import Grid
from custom_constants import WALL_ID, HIDRA_ID, LAVA_ID, CELL_COSTS

class LocalSearch:
    def __init__(self, grid):
        """
        :param grid: The Grid object from your main code that provides
                     environment info: grid.grid[y][x] and grid_size, etc.
        """
        self.grid = grid
        self.grid_size = grid.grid_size

    def heuristic(self, x, y, goal):
        # Manhattan distance heuristic
        gx, gy = goal
        return abs(x - gx) + abs(y - gy)

    def get_neighbors(self, x, y):
        # Return valid neighbors (passable cells only)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                cell_id = self.grid.grid[ny][nx]
                # Check if cell is impassable or fatal
                # If it's lava or hydra cell, stepping here = death = fail
                cost = CELL_COSTS.get(cell_id, 1)
                # We consider these impassable or fatal:
                if cost == float('inf'):
                    continue
                neighbors.append((nx, ny))
        return neighbors

    def hill_climbing(self, start, goal, max_iterations=1000):
        """
        Basic hill-climbing local search:
        - Start at `start`
        - Repeatedly move to the neighbor that reduces the heuristic the most
        - If no improvement, stop and fail
        - If goal is found, return path
        - If a monster (HIDRA) or LAVA cell is stepped on, fail immediately.
        """
        current = start
        path = [current]
        current_h = self.heuristic(*current, goal)

        for _ in range(max_iterations):
            if current == goal:
                return path
            neighbors = self.get_neighbors(*current)
            if not neighbors:
                # Nowhere to go
                return None

            # Evaluate neighbors
            best_neighbor = None
            best_h = current_h
            for n in neighbors:
                nh = self.heuristic(*n, goal)
                if nh < best_h:
                    best_h = nh
                    best_neighbor = n

            if best_neighbor is None:
                # No improvement found
                return None
            else:
                # Check if this best_neighbor is a lava/hydra cell
                nx, ny = best_neighbor
                cell_id = self.grid.grid[ny][nx]
                if cell_id == HIDRA_ID or cell_id == LAVA_ID:
                    # Stepping here = death, immediate fail
                    return None
                current = best_neighbor
                current_h = best_h
                path.append(current)

        return None  # If we exceeded max_iterations without reaching goal

    def local_search_with_restarts(self, start, goal, restarts=10):
        """
        Try hill_climbing from `start` multiple times.
        If fail, just retry from the start again.
        """
        for _ in range(restarts):
            path = self.hill_climbing(start, goal)
            if path is not None:
                return path
        return None


def run_tests(runs=50, maps_per_run=100, grid_size=20, output_file="local_search_results.csv"):
    """
    Runs the local search test `runs` times. Each run generates `maps_per_run` maps.
    For each map, we:
      - create a map
      - run local search
      - consider success if we reach the goal, failure otherwise
    At the end of each run, we record how many times local search succeeded out of `maps_per_run`.

    The results are saved in a CSV file for further analysis.
    """
    # Prepare CSV file
    write_header = not os.path.exists(output_file)
    with open(output_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(["Run_Number", "Maps_Per_Run", "Successes", "Failures", "Success_Rate"])

        for run_index in range(1, runs + 1):
            successes = 0
            failures = 0

            for _ in range(maps_per_run):
                g = Grid(grid_size)
                px = random.randint(1, grid_size - 2)
                py = random.randint(1, grid_size - 2)
                gx = random.randint(1, grid_size - 2)
                gy = random.randint(1, grid_size - 2)
                while (gx, gy) == (px, py):
                    gx = random.randint(1, grid_size - 2)
                    gy = random.randint(1, grid_size - 2)

                g.create_auto_map((px, py), (gx, gy), place_obstacles=True)

                # If map isn't valid, treat as failure
                # Validity means player and goal are enclosed properly
                if not g.valid_map:
                    failures += 1
                    continue

                ls = LocalSearch(g)
                ls_path = ls.local_search_with_restarts((px, py), (gx, gy), restarts=5)
                if ls_path is not None:
                    # Success
                    successes += 1
                else:
                    # Failure
                    failures += 1

            success_rate = (successes / maps_per_run) * 100.0
            writer.writerow([run_index, maps_per_run, successes, failures, f"{success_rate:.2f}%"])

    print(f"Test completed. Results saved to {output_file}")


if __name__ == "__main__":
    # Run 50 test runs with 100 maps each
    run_tests(runs=50, maps_per_run=100, grid_size=20, output_file="local_search_results.csv")

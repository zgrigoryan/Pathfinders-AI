
# Hercules Finds His Path Underworld

This program is a grid-based pathfinding simulation where the player (Hercules) must navigate through obstacles to reach the goal. You can either draw the maps on your own, or have them auto generated!
The map can include walls, lava, mountains, and an optional hydra as additional challenges. 
The application uses BFS, DFS, Uniform Cost Search (UCS), and A* algorithms for pathfinding.

## Features
- Drag-and-drop walls and obstacles to design the map.
- Automatically generate a map with random obstacles and valid paths.
- Perform pathfinding using BFS, DFS, UCS, and A* algorithms.
- Simulate battles with hydras blocking paths.

---

## Setup and Installation

### Step 1: Create a Virtual Environment
1. Open your terminal or command prompt.
2. Navigate to the directory containing the project.
3. Run the following command to create a virtual environment:
   ```
   python -m venv venv
   ```

### Step 2: Activate the Virtual Environment
- On **Windows**:
  ```
  venv\Scripts\activate
  ```
- On **Mac/Linux**:
  ```
  source venv/bin/activate
  ```

### Step 3: Install Requirements
1. Ensure your virtual environment is activated.
2. Install the required dependencies from `requirements.txt`:
   ```
   pip install -r requirements.txt
   ```

---

## Running the Code

1. Ensure your virtual environment is activated.
2. Run the program using the following command:
   ```
   python3 create_map.py
   ```
3. By default, the program uses a grid size defined in the `custom_constants.py` file. 
   To change the grid size at runtime:
   - Set the `--experiment` flag to skip manual input for grid size and proceed with the default configuration.
   - Example:
     ```
     python create_map.py --experiment
     ```

4. Use the GUI to design the map or let the program auto-generate a playable map. Click "RUN" to begin pathfinding.

---

## Key Shortcuts
- Press **Space** to cycle through the pathfinding algorithms during visualization.
- Use the slider in the sidebar to validate the map before running the simulation.

---


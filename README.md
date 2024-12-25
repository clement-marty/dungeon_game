# Untitled Dungeon Game

This game is a tile-based dungeon crawler game built with Python and Pygame. The game features procedurally generated dungeons, various textures for tiles, obstacles, and decorations, and a simple turn-based game logic for player and enemy movements.  
This is still an unfinished project, so the game still lacks some textures, and enemies move randomly without dealing any damage.


## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/clement-marty/dungeon_game.git
    cd dungeon_game
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the game:
    ```sh
    python main.py
    ```

2. Use the following keys to control the player:
    - `Z`: Move up
    - `Q`: Move left
    - `S`: Move down
    - `D`: Move right

## Project Structure

- `main.py`: The main entry point of the game.
- `scripts/`: Contains the core game scripts.
  - `dungeon_generation.py`: Contains the BSP algorithm for dungeon generation.
  - `textures.py`: Manages the loading and handling of textures.
  - `renderer.py`: Handles rendering of the game scene and UI.
  - `game_logic.py`: Contains the game logic for player and enemy movements.
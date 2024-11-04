import random
import numpy as np

from scripts.textures import GameSprites

class GameLogic:
    DUNGEON_GRID: np.ndarray
    WALL_VMATRIX: np.ndarray
    ROOM_VMATRIX: np.ndarray
    CORRIDOR_VMATRIX: np.ndarray
    OBSTACLES_VMATRIX: np.ndarray

    ENEMIES: 'list[GameLogic.Enemy]'
    PLAYER: 'GameLogic.Player'

    @classmethod
    def init(cls, dungeon_grid: np.ndarray,
             wall_vmatrix: np.ndarray,
             room_vmatrix: np.ndarray,
             corridor_vmatrix: np.ndarray,
             obstacles_vmatrix: np.ndarray,
             *args, **kwargs) -> tuple:
        cls.DUNGEON_GRID = dungeon_grid
        cls.WALL_VMATRIX = wall_vmatrix
        cls.ROOM_VMATRIX = room_vmatrix
        cls.CORRIDOR_VMATRIX = corridor_vmatrix
        cls.OBSTACLES_VMATRIX = obstacles_vmatrix

        cls.PLAYER = cls.Player()
        cls.ENEMIES = []
        return cls.PLAYER, cls.ENEMIES

    @classmethod
    def _positions(cls, entities: 'list[GameLogic.Entity]') -> list[tuple[int, int]]:
        pos = []
        for e in entities:
            pos.append(e.position)
        return pos


    class Entity:

        def __init__(self, max_health: int) -> None:
            self.position: list[int, int]
            self.texture: GameSprites._Texture
            self.texture_variant = random.randint(0, self.texture.variants-1)
            self.max_health = max_health
            self._health = max_health

        def _can_move_to(self, position: tuple[int, int]) -> bool:
            return GameLogic.DUNGEON_GRID[*position] != 0 and\
                (GameLogic.OBSTACLES_VMATRIX[*position][0] is None or GameLogic.DUNGEON_GRID[*position] != 1) and\
                position not in GameLogic._positions(GameLogic.ENEMIES) and\
                position != GameLogic.PLAYER.position

        def _move(self, direction: tuple[int, int]) -> None:
            new_position = (self.position[0] + direction[0], self.position[1] + direction[1])
            if self._can_move_to(new_position):
                self.position = new_position

        @property
        def health(self) -> int:
            return self._health
        def reduce_health(self, amount: int) -> None: self._health = max(0, self._health - amount)


    class Player(Entity):
        texture = GameSprites.entities.PLAYER
            
        def __init__(self, max_health: int = 100, max_energy: int = 100) -> None:
            super().__init__(max_health)
            self.max_energy = max_energy
            self._energy = max_energy

        def move_up(self) -> None: self._move((0, -1))
        def move_down(self) -> None: self._move((0, 1))
        def move_left(self) -> None: self._move((-1, 0))
        def move_right(self) -> None: self._move((1, 0))

        @property
        def energy(self) -> int:
            return self._energy
        def reduce_energy(self, amount: int) -> None: self._energy = max(0, self._energy - amount)
    

    class Enemy(Entity):
        texture = GameSprites.entities.ENEMY

        def __init__(self, max_health: int, starting_position: tuple[int, int]):
            super().__init__(max_health)
            self.position = starting_position
        
        def move(self, random_seed: int = None) -> None:
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            if random_seed:
                random.seed(random_seed)
            random.shuffle(directions)
            i = 0
            while i < len(directions) and not self._can_move_to(directions[i]):
                i += 1
            
            if i != len(directions): # i == len(directions) ==> while loop has not found a direction that the enemy can move to
                self._move(direction=directions[i])


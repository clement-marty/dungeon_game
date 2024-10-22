import numpy as np


class GameLogic:
    DUNGEON_GRID: np.ndarray
    WALL_VMATRIX: np.ndarray
    ROOM_VMATRIX: np.ndarray
    CORRIDOR_VMATRIX: np.ndarray
    OBSTACLES_VMATRIX: np.ndarray

    @classmethod
    def init(cls, dungeon_grid: np.ndarray,
             wall_vmatrix: np.ndarray,
             room_vmatrix: np.ndarray,
             corridor_vmatrix: np.ndarray,
             obstacles_vmatrix: np.ndarray,
             *args, **kwargs) -> None:
        cls.DUNGEON_GRID = dungeon_grid
        cls.WALL_VMATRIX = wall_vmatrix
        cls.ROOM_VMATRIX = room_vmatrix
        cls.CORRIDOR_VMATRIX = corridor_vmatrix
        cls.OBSTACLES_VMATRIX = obstacles_vmatrix



    class Entity:

        def __init__(self, max_health: int) -> None:
            self.position: list[int, int]
            self.max_health = max_health
            self.health = max_health

        def _move(self, direction: tuple[int, int]) -> None:
            new_position = (self.position[0] + direction[0], self.position[1] + direction[1])
            if GameLogic.DUNGEON_GRID[*new_position] != 0 and \
                (GameLogic.OBSTACLES_VMATRIX[*new_position][0] is None or GameLogic.DUNGEON_GRID[*new_position] != 1):
                self.position = new_position

        @property
        def health(self) -> int:
            return self._health
        def reduce_health(self, amount: int) -> None: self._health = max(0, self._health - amount)


    class Player(Entity):
            
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
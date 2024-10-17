import pygame
import numpy as np

from scripts.textures import GameSprites


class Renderer:
    SCREEN_SIZE: tuple[int, int]
    TILE_SIZE: int
    DUNGEON_GRID: np.ndarray
    WALL_VMATRIX: np.ndarray
    ROOM_VMATRIX: np.ndarray
    CORRIDOR_VMATRIX: np.ndarray
    OBSTACLES_VMATRIX: np.ndarray
    VMATRIX_PADDING: int

    @classmethod
    def init(cls, screen_size: tuple[int, int],
             tile_size: int,
             dungeon_grid: np.ndarray,
             wall_vmatrix: np.ndarray,
             room_vmatrix: np.ndarray,
             corridor_vmatrix: np.ndarray,
             obstacles_vmatrix: np.ndarray,
             *args, **kwargs) -> None:
        cls.SCREEN_SIZE = screen_size
        cls.TILE_SIZE = tile_size

        cls.VMATRIX_PADDING = max(cls.SCREEN_SIZE)

        cls.DUNGEON_GRID = np.pad(dungeon_grid, (cls.VMATRIX_PADDING,), mode='constant', constant_values=0)
        cls.WALL_VMATRIX = np.pad(wall_vmatrix, (cls.VMATRIX_PADDING,), mode='constant', constant_values=0)
        cls.ROOM_VMATRIX = np.pad(room_vmatrix, (cls.VMATRIX_PADDING,), mode='constant', constant_values=0)
        cls.CORRIDOR_VMATRIX = np.pad(corridor_vmatrix, (cls.VMATRIX_PADDING,), mode='constant', constant_values=0)
        cls.OBSTACLES_VMATRIX = np.pad(obstacles_vmatrix, ([cls.VMATRIX_PADDING]*2, [cls.VMATRIX_PADDING]*2, [0]*2), mode='constant', constant_values=(None, None))

    
    @classmethod
    def render_scene(cls, screen: pygame.Surface, player_position: tuple[int, int]) -> None:
        x_offset, y_offset = cls.SCREEN_SIZE[0] // 2, cls.SCREEN_SIZE[1] // 2

        splitter = (
            player_position[0] + cls.VMATRIX_PADDING - x_offset, player_position[0] + cls.VMATRIX_PADDING + x_offset+1,
            player_position[1] + cls.VMATRIX_PADDING - y_offset, player_position[1] + cls.VMATRIX_PADDING + y_offset+1
        )
        rendered_tiles = cls.DUNGEON_GRID[splitter[0]:splitter[1], splitter[2]:splitter[3]]
        rendered_obstacles = cls.OBSTACLES_VMATRIX[splitter[0]:splitter[1], splitter[2]:splitter[3]]
        for x in range(rendered_tiles.shape[0]):
            for y in range(rendered_tiles.shape[1]):
                texture, vmatrix = (GameSprites.ROOM_TEXTURE, cls.ROOM_VMATRIX) if rendered_tiles[x, y] == 1 else \
                                (GameSprites.CORRIDOR_TEXTURE, cls.CORRIDOR_VMATRIX) if rendered_tiles[x, y] == 2 else \
                                (GameSprites.WALL_TEXTURE, cls.WALL_VMATRIX)
                screen.blit(
                    texture.get_variant(vmatrix[x + splitter[0], y + splitter[2]]),
                    (x * cls.TILE_SIZE, y * cls.TILE_SIZE)
                )

                if rendered_tiles[x, y] == 1 :
                    if rendered_obstacles[x, y][0] is not None:
                        screen.blit(
                            rendered_obstacles[x, y][0].get_variant(rendered_obstacles[x, y][1]), (x * cls.TILE_SIZE, y * cls.TILE_SIZE)
                        )
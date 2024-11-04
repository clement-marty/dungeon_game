import pygame
import numpy as np

from scripts.textures import GameSprites
from scripts.game_logic import GameLogic


class Renderer:
    SCREEN: pygame.Surface
    SCREEN_SIZE: tuple[int, int]
    TILE_SIZE: int
    DUNGEON_GRID: np.ndarray
    WALL_VMATRIX: np.ndarray
    ROOM_VMATRIX: np.ndarray
    CORRIDOR_VMATRIX: np.ndarray
    OBSTACLES_VMATRIX: np.ndarray
    DECORATION_VMATRIX: np.ndarray
    VMATRIX_PADDING: int

    UI_BACKGROUND_COLOR: tuple[int, int, int] = (150, 150, 150)
    UI_HEALTH_BAR_COLOR: tuple[int, int, int] = (255, 50, 50)
    UI_ENERGY_BAR_COLOR: tuple[int, int, int] = (100, 100, 255)

    @classmethod
    def init(cls, screen: pygame.Surface,
             screen_size: tuple[int, int],
             tile_size: int,
             dungeon_grid: np.ndarray,
             wall_vmatrix: np.ndarray,
             room_vmatrix: np.ndarray,
             corridor_vmatrix: np.ndarray,
             obstacles_vmatrix: np.ndarray,
             decoration_vmatrix: np.ndarray,
             *args, **kwargs) -> None:
        cls.SCREEN = screen
        cls.SCREEN_SIZE = screen_size
        cls.TILE_SIZE = tile_size

        cls.VMATRIX_PADDING = max(cls.SCREEN_SIZE)

        cls.DUNGEON_GRID = np.pad(dungeon_grid, (cls.VMATRIX_PADDING,), mode='constant', constant_values=0)
        cls.WALL_VMATRIX = np.pad(wall_vmatrix, (cls.VMATRIX_PADDING,), mode='constant', constant_values=0)
        cls.ROOM_VMATRIX = np.pad(room_vmatrix, (cls.VMATRIX_PADDING,), mode='constant', constant_values=0)
        cls.CORRIDOR_VMATRIX = np.pad(corridor_vmatrix, (cls.VMATRIX_PADDING,), mode='constant', constant_values=0)
        cls.OBSTACLES_VMATRIX = np.pad(obstacles_vmatrix, ([cls.VMATRIX_PADDING]*2, [cls.VMATRIX_PADDING]*2, [0]*2), mode='constant', constant_values=(None, None))
        cls.DECORATION_VMATRIX = np.pad(decoration_vmatrix, ([cls.VMATRIX_PADDING]*2, [cls.VMATRIX_PADDING]*2, [0]*2), mode='constant', constant_values=(None, None))

    
    @classmethod
    def render_scene(cls, player_position: tuple[int, int]) -> None:
        x_offset, y_offset = cls.SCREEN_SIZE[0] // 2, cls.SCREEN_SIZE[1] // 2

        splitter = (
            player_position[0] + cls.VMATRIX_PADDING - x_offset, player_position[0] + cls.VMATRIX_PADDING + x_offset+1,
            player_position[1] + cls.VMATRIX_PADDING - y_offset, player_position[1] + cls.VMATRIX_PADDING + y_offset+1
        )
        rendered_tiles = cls.DUNGEON_GRID[splitter[0]:splitter[1], splitter[2]:splitter[3]]
        rendered_obstacles = cls.OBSTACLES_VMATRIX[splitter[0]:splitter[1], splitter[2]:splitter[3]]
        rendered_decoration = cls.DECORATION_VMATRIX[splitter[0]:splitter[1], splitter[2]:splitter[3]]
        for x in range(rendered_tiles.shape[0]):
            for y in range(rendered_tiles.shape[1]):
                texture, vmatrix = (GameSprites.tiles.ROOM, cls.ROOM_VMATRIX) if rendered_tiles[x, y] == 1 else \
                                (GameSprites.tiles.CORRIDOR, cls.CORRIDOR_VMATRIX) if rendered_tiles[x, y] == 2 else \
                                (GameSprites.tiles.WALL, cls.WALL_VMATRIX)
                cls.SCREEN.blit(
                    texture.get_variant(vmatrix[x + splitter[0], y + splitter[2]], cls.TILE_SIZE),
                    (x * cls.TILE_SIZE, y * cls.TILE_SIZE)
                )

                if rendered_tiles[x, y] == 1 and rendered_obstacles[x, y][0] is not None:
                    cls.SCREEN.blit(
                        rendered_obstacles[x, y][0].get_variant(rendered_obstacles[x, y][1], cls.TILE_SIZE), (x * cls.TILE_SIZE, y * cls.TILE_SIZE)
                    )
                
                elif rendered_tiles[x, y] != 0 and rendered_decoration[x, y][0] is not None:
                    cls.SCREEN.blit(
                        rendered_decoration[x, y][0].get_variant(rendered_decoration[x, y][1], cls.TILE_SIZE), (x * cls.TILE_SIZE, y * cls.TILE_SIZE)
                    )



    @classmethod
    def render_entities(cls, entities: list[GameLogic.Entity]) -> None:
        raise NotImplementedError()

    
    @classmethod
    def render_ui(cls, player: GameLogic.Player) -> None:
        x_pixels, y_pixels = cls.SCREEN_SIZE[0] * cls.TILE_SIZE, cls.SCREEN_SIZE[1] * cls.TILE_SIZE

        rect_size = (int(x_pixels * .3), int(y_pixels * .05))
        margin = int(y_pixels * .05)

        health_background = pygame.Rect(margin, y_pixels - margin - rect_size[1], *rect_size)
        energy_background = pygame.Rect(x_pixels - margin - rect_size[0], y_pixels - margin - rect_size[1], *rect_size)
        health_bar = pygame.Rect(
            health_background.left, 
            health_background.top,
            int(health_background.width * player.health / player.max_health),
            health_background.height
        )
        energy_bar = pygame.Rect(
            energy_background.left,
            energy_background.top,
            int(energy_background.width * player.energy / player.max_energy),
            energy_background.height
        )

        for rect in [health_background, energy_background]:
            pygame.draw.rect(surface=cls.SCREEN, color=cls.UI_BACKGROUND_COLOR, rect=rect)

        for rect, color, icon in zip(
                [health_bar, energy_bar],
                [cls.UI_HEALTH_BAR_COLOR, cls.UI_ENERGY_BAR_COLOR],
                [GameSprites.ui.HEALTH_ICON, GameSprites.ui.ENERGY_ICON]
            ):
            pygame.draw.rect(surface=cls.SCREEN, color=color, rect=rect)
            cls.SCREEN.blit(icon.get(side_length=rect.height), rect)
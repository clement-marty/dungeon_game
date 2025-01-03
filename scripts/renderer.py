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
        '''Initializes the renderer with the given parameters.

        This method sets up the renderer by initializing the screen, tile size, and various matrices used for rendering the dungeon.

        :param screen: The screen surface to render on.
        :param int tile_size: The size of each tile in pixels.
        :param np.ndarray dungeon_grid: The grid representing the dungeon layout.
        :param np.ndarray wall_vmatrix: The matrix representing the walls.
        :param np.ndarray room_vmatrix: The matrix representing the rooms.
        :param np.ndarray corridor_vmatrix: The matrix representing the corridors.
        :param np.ndarray obstacles_vmatrix: The matrix representing the obstacles.
        :param np.ndarray decoration_vmatrix: The matrix representing the decorations.
        :return: None
        '''
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
        '''Renders the entire scene centered around the player's position.

        This method calculates the visible area of the dungeon grid based on the player's position and the screen size.
        It then renders the tiles, obstacles, decorations, and entities within this visible area.

        :param tuple[int, int] player_position: The current position of the player in the dungeon grid.
        :return: None
        '''
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

                cls._render_tile(x, y, rendered_tiles, splitter)

                has_rendered_an_obstacle = cls._render_obstacle(x, y, rendered_tiles, rendered_obstacles)
                
                if not has_rendered_an_obstacle:
                    cls._render_decoration(x, y, rendered_tiles, rendered_decoration)
        
        cls._render_entities([GameLogic.PLAYER] + GameLogic.ENEMIES, splitter)


    @classmethod
    def _render_tile(cls, x: int, y: int, rendered_tiles: np.ndarray, splitter: tuple) -> None:
        '''Renders a single tile at the specified position.

        This method renders a tile at the given (x, y) position within the visible area of the dungeon grid.

        :param int x: The x-coordinate of the tile.
        :param int y: The y-coordinate of the tile.
        :param np.ndarray rendered_tiles: The array of tiles to be rendered.
        :param tuple splitter: The tuple defining the visible area of the dungeon grid.
        :return: None
        '''
        texture, vmatrix = (GameSprites.tiles.ROOM, cls.ROOM_VMATRIX) if rendered_tiles[x, y] == 1 else \
                                (GameSprites.tiles.CORRIDOR, cls.CORRIDOR_VMATRIX) if rendered_tiles[x, y] == 2 else \
                                (GameSprites.tiles.WALL, cls.WALL_VMATRIX)
        cls.SCREEN.blit(
            texture.get_variant(vmatrix[x + splitter[0], y + splitter[2]], cls.TILE_SIZE),
            (x * cls.TILE_SIZE, y * cls.TILE_SIZE)
        )
    

    @classmethod
    def _render_obstacle(cls, x: int, y: int, rendered_tiles: np.ndarray, rendered_obstacles: np.ndarray) -> bool:
        '''Renders an obstacle at the specified position.

        This method renders an obstacle at the given (x, y) position within the visible area of the dungeon grid.

        :param int x: The x-coordinate of the obstacle.
        :param int y: The y-coordinate of the obstacle.
        :param np.ndarray rendered_tiles: The array of tiles to be rendered.
        :param np.ndarray rendered_obstacles: The array of obstacles to be rendered.
        :return bool: True if an obstacle was rendered, False otherwise.
        '''
        obstacle: bool = rendered_tiles[x, y] == 1 and rendered_obstacles[x, y][0] is not None
        if obstacle:
            cls.SCREEN.blit(
                rendered_obstacles[x, y][0].get_variant(rendered_obstacles[x, y][1], cls.TILE_SIZE), (x * cls.TILE_SIZE, y * cls.TILE_SIZE)
            )
        return obstacle
    

    @classmethod
    def _render_decoration(cls, x: int, y: int, rendered_tiles: np.ndarray, rendered_decoration: np.ndarray) -> bool:
        '''Renders a decoration at the specified position.

        This method renders a decoration at the given (x, y) position within the visible area of the dungeon grid.

        :param int x: The x-coordinate of the decoration.
        :param int y: The y-coordinate of the decoration.
        :param np.ndarray rendered_tiles: The array of tiles to be rendered.
        :param np.ndarray rendered_decoration: The array of decorations to be rendered.
        :return bool: True if a decoration was rendered, False otherwise.
        '''
        decoration = rendered_tiles[x, y] != 0 and rendered_decoration[x, y][0] is not None
        if decoration:
            cls.SCREEN.blit(
                rendered_decoration[x, y][0].get_variant(rendered_decoration[x, y][1], cls.TILE_SIZE), (x * cls.TILE_SIZE, y * cls.TILE_SIZE)
            )
        return decoration


    @classmethod
    def _render_entities(cls, entities: list[GameLogic.Entity], splitter: tuple) -> None:
        '''Renders all entities within the visible area.

        This method renders all entities within the visible area of the dungeon grid.

        :param list[GameLogic.Entity] entities: The list of entities to be rendered.
        :param tuple splitter: The tuple defining the visible area of the dungeon grid.
        :return: None
        '''
        s = (
            splitter[0] - cls.VMATRIX_PADDING, splitter[1] - cls.VMATRIX_PADDING,
            splitter[2] - cls.VMATRIX_PADDING, splitter[3] - cls.VMATRIX_PADDING
        )
        for entity in entities:
            if entity.position[0] >= s[0] and entity.position[0] < s[1] and \
                    entity.position[1] >= s[2] and entity.position[1] < s[3]:
                x, y = entity.position[0] - s[0], entity.position[1] - s[2]
                cls.SCREEN.blit(
                    entity.texture.get_variant(entity.texture_variant, cls.TILE_SIZE), (x * cls.TILE_SIZE, y * cls.TILE_SIZE)
                )

    
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
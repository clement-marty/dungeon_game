import pygame
import numpy as np

from scripts.dungeon_generation import BSPAlgorithm
from scripts.textures import GameSprites
from scripts.textures import variant_matrix
from scripts.textures import object_variant_matrix


SCREEN_SIZE: tuple [int, int] = (15, 9) # The size of the screen, in game tiles. Both numbers should be odd
TILE_SIZE: int = 64 # The side length, in pixels, of each game tile rendered on screen
DUNGEON_SIZE: tuple[int, int] = 100, 75 # The size, in tiles, of the game's dungeon
RANDOM_SEED: int = 42

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE[0] * TILE_SIZE, SCREEN_SIZE[1] * TILE_SIZE))
clock = pygame.time.Clock()
running = True


vmatrix_size = (DUNGEON_SIZE[0] + 2 * max(SCREEN_SIZE), DUNGEON_SIZE[1] + 2 * max(SCREEN_SIZE))
ROOM_VMATRIX     = variant_matrix(size=vmatrix_size, variants=GameSprites.ROOM_TEXTURE.variants, random_seed=RANDOM_SEED)
CORRIDOR_VMATRIX = variant_matrix(size=vmatrix_size, variants=GameSprites.CORRIDOR_TEXTURE.variants, random_seed=RANDOM_SEED + 1)
WALL_VMATRIX     = variant_matrix(size=vmatrix_size, variants=GameSprites.WALL_TEXTURE.variants, random_seed=RANDOM_SEED + 2)
OBSTACLES_VMATRIX = object_variant_matrix(size=vmatrix_size, object_textures=[GameSprites.CRATE_TEXTURE], random_seed=RANDOM_SEED + 3)


DUNGEON_GRID, ROOMS = BSPAlgorithm.generate(
    dungeon_size=DUNGEON_SIZE,
    splitting_iterations=5,
    corridor_width=3,
    random_seed=RANDOM_SEED
)


class Player:
    position: list[int, int]

    @classmethod
    def _move(cls, direction: tuple[int, int]):
        new_position = (cls.position[0] + direction[0], cls.position[1] + direction[1])
        vmatrix_pos = (new_position[0] + max(SCREEN_SIZE), new_position[1] + max(SCREEN_SIZE))
        if DUNGEON_GRID[*new_position] != 0 and \
            (OBSTACLES_VMATRIX[*vmatrix_pos, 0] is None or DUNGEON_GRID[*new_position] != 1):
            cls.position = new_position
        
    @classmethod
    def move_up(cls): return cls._move((0, -1))
    @classmethod
    def move_down(cls): return cls._move((0, 1))
    @classmethod
    def move_left(cls): return cls._move((-1, 0))
    @classmethod
    def move_right(cls): return cls._move((1, 0))


# Compute the area of all rooms to find the smallest one and the greatest one
areas = [room[2]*room[3] for room in ROOMS]
spawn_room, exit_room = ROOMS[areas.index(min(areas))], ROOMS[areas.index(max(areas))]
spawn_coords, exit_coords = (spawn_room[0] + spawn_room[2]//2, spawn_room[1] + spawn_room[3]//2), (exit_room[0] + exit_room[2]//2, exit_room[1] + exit_room[3]//2)
Player.position = spawn_coords

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q: Player.move_left()
            if event.key == pygame.K_d: Player.move_right()
            if event.key == pygame.K_z: Player.move_up()
            if event.key == pygame.K_s: Player.move_down()


    screen.fill((0, 0, 0))

    x_offset, y_offset = SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2

    padded_grid = np.pad(DUNGEON_GRID, (max(SCREEN_SIZE),), mode='constant', constant_values=0)
    splitter = (
        Player.position[0] + max(SCREEN_SIZE) - x_offset, Player.position[0] + max(SCREEN_SIZE) + x_offset+1,
        Player.position[1] + max(SCREEN_SIZE) - y_offset, Player.position[1] + max(SCREEN_SIZE) + y_offset+1
    )
    rendered_tiles = padded_grid[splitter[0]:splitter[1], splitter[2]:splitter[3]]
    rendered_obstacles = OBSTACLES_VMATRIX[splitter[0]:splitter[1], splitter[2]:splitter[3]]
    for x_rel in range(rendered_tiles.shape[0]):
        for y_rel in range(rendered_tiles.shape[1]):
            x_abs, y_abs = x_rel + Player.position[0] - max(SCREEN_SIZE) + x_offset, y_rel + Player.position[1] - max(SCREEN_SIZE) + y_offset

            texture, vmatrix = (GameSprites.ROOM_TEXTURE, ROOM_VMATRIX) if rendered_tiles[x_rel, y_rel] == 1 else \
                               (GameSprites.CORRIDOR_TEXTURE, CORRIDOR_VMATRIX) if rendered_tiles[x_rel, y_rel] == 2 else \
                               (GameSprites.WALL_TEXTURE, WALL_VMATRIX)
            screen.blit(
                texture.get_variant(vmatrix[x_abs, y_abs]),
                (x_rel*TILE_SIZE, y_rel*TILE_SIZE)
            )

            if rendered_tiles[x_rel, y_rel] == 1 and rendered_obstacles[x_rel, y_rel, 0] is not None:
                screen.blit(
                    rendered_obstacles[x_rel, y_rel, 0].get_variant(rendered_obstacles[x_rel, y_rel, 1]), (x_rel*TILE_SIZE, y_rel*TILE_SIZE)
                )
    
    pygame.draw.circle(screen, (255, 0, 0), (SCREEN_SIZE[0]*TILE_SIZE//2, SCREEN_SIZE[1]*TILE_SIZE//2), int(TILE_SIZE*40/100))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
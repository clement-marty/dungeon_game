import pygame

from scripts.dungeon_generation import BSPAlgorithm
from scripts.textures import GameSprites
from scripts.renderer import Renderer
from scripts.game_logic import GameLogic


SCREEN_SIZE: tuple[int, int] = (15, 9) # The size of the screen, in game tiles. Both numbers should be odd
TILE_SIZE: int = 64 # The side length, in pixels, of each game tile rendered on screen
DUNGEON_SIZE: tuple[int, int] = 100, 75 # The size, in tiles, of the game's dungeon
RANDOM_SEED: int = 42

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE[0] * TILE_SIZE, SCREEN_SIZE[1] * TILE_SIZE))
clock = pygame.time.Clock()
running = True

WALL_VMATRIX = GameSprites.variant_matrix(size=DUNGEON_SIZE, variants=GameSprites.tiles.WALL.variants, random_seed=RANDOM_SEED)
ROOM_VMATRIX = GameSprites.variant_matrix(size=DUNGEON_SIZE, variants=GameSprites.tiles.ROOM.variants, random_seed=RANDOM_SEED + 1)
CORRIDOR_VMATRIX = GameSprites.variant_matrix(size=DUNGEON_SIZE, variants=GameSprites.tiles.CORRIDOR.variants, random_seed=RANDOM_SEED + 2)
OBSTACLES_VMATRIX = GameSprites.object_variant_matrix(size=DUNGEON_SIZE, object_textures=[GameSprites.tiles.CRATE], random_seed=RANDOM_SEED + 3)
DECORATION_VMATRIX = GameSprites.object_variant_matrix(size=DUNGEON_SIZE, object_textures=[GameSprites.tiles.BONES], random_seed=RANDOM_SEED + 4, fill=.02)

NEW_TURN_EVENT = pygame.USEREVENT + 1

DUNGEON_GRID, ROOMS = BSPAlgorithm.generate(
    dungeon_size=DUNGEON_SIZE,
    splitting_iterations=5,
    corridor_width=3,
    random_seed=RANDOM_SEED
)

init_config = {
    "screen": screen,
    "screen_size": SCREEN_SIZE,
    "tile_size": TILE_SIZE,
    "dungeon_grid": DUNGEON_GRID,
    "wall_vmatrix": WALL_VMATRIX,
    "room_vmatrix": ROOM_VMATRIX,
    "corridor_vmatrix": CORRIDOR_VMATRIX,
    "obstacles_vmatrix": OBSTACLES_VMATRIX,
    "decoration_vmatrix": DECORATION_VMATRIX,
    "new_turn_event": NEW_TURN_EVENT
}
Renderer.init(**init_config)
PLAYER, ENEMIES = GameLogic.init(**init_config)

# Compute the area of all rooms to find the smallest one and the greatest one
areas = [room[2]*room[3] for room in ROOMS]
spawn_room, exit_room = ROOMS[areas.index(min(areas))], ROOMS[areas.index(max(areas))]
spawn_coords, exit_coords = (spawn_room[0] + spawn_room[2]//2, spawn_room[1] + spawn_room[3]//2), (exit_room[0] + exit_room[2]//2, exit_room[1] + exit_room[3]//2)

PLAYER.position = spawn_coords
GameLogic.instantiate_enemies(amount=50, random_seed=RANDOM_SEED + 5)

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q: PLAYER.move_left()
            if event.key == pygame.K_d: PLAYER.move_right()
            if event.key == pygame.K_z: PLAYER.move_up()
            if event.key == pygame.K_s: PLAYER.move_down()


    screen.fill((0, 0, 0))

    Renderer.render_scene(player_position=PLAYER.position)
    Renderer.render_ui(player=PLAYER)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
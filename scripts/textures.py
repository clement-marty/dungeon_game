import pygame
import random
import numpy as np


class GameSprites:

    class _Texture:
        def __init__(self, texture_filenames: list[str]) -> None:
            self.texture_images: list[pygame.Surface] = [
                pygame.image.load(filename) for filename in texture_filenames
            ]

        @property
        def variants(self) -> int:
            return len(self.texture_images)

        def get_variant(self, variant_id: int) -> pygame.Surface:
            return pygame.transform.scale(self.texture_images[variant_id], (64, 64))
    

    WALL_TEXTURE = _Texture([
        'assets/floor/wall_tile.png'
    ])
    ROOM_TEXTURE = _Texture([
        'assets/floor/room_tile_1.png',
        'assets/floor/room_tile_2.png',
        'assets/floor/room_tile_3.png'
    ])
    CORRIDOR_TEXTURE = _Texture([
        'assets/floor/corridor_tile_1.png',
        'assets/floor/corridor_tile_2.png',
        'assets/floor/corridor_tile_3.png',
        'assets/floor/corridor_tile_4.png'
    ])
    CRATE_TEXTURE = _Texture([
        'assets/objects/crate_tile_1.png',
        'assets/objects/crate_tile_2.png',
        'assets/objects/crate_tile_3.png',
        'assets/objects/crate_tile_4.png'
    ])


def variant_matrix(size: tuple[int, int], variants: int, random_seed: int) -> np.ndarray:
    if variants > 1:
        np.random.seed(random_seed)
        return np.random.randint(low=0, high=variants, size=size, dtype=int)
    else:
        return np.zeros(shape=size, dtype=int)


def object_variant_matrix(size: tuple[int, int], object_textures: list[GameSprites._Texture], random_seed: int, fill: float = 0.25) -> np.ndarray:
    vmatrices = [variant_matrix(size=size, variants=obj.variants, random_seed=random_seed) for obj in object_textures]
    fill_matrix = np.random.rand(*size)
    final_matrix = np.full(shape=(*size, 2), fill_value=(None, None))
    for x in range(size[0]):
        for y in range(size[1]):
            if fill_matrix[x, y] <= fill:
                obj_id = random.randint(0, len(object_textures) - 1)
                final_matrix[x, y][0] = object_textures[obj_id]
                final_matrix[x, y][1] = vmatrices[obj_id][x, y]
    return final_matrix
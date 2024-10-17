import time
import random
import numpy as np


class BSPAlgorithm:

    @classmethod
    def generate(cls, dungeon_size: tuple[int, int],
                 splitting_iterations: int = 4,
                 split_range: float = 0.5,
                 corridor_width: int = 3,
                 random_seed: int = None) -> tuple[np.ndarray, list[tuple[int, int, int, int]]]:
        '''Generates a dungeon based on the BSP algorithm

        :param tuple[int, int] dungeon_size: the size of the dungeon to be generated
        :param int splitting_iterations: the number of recursive splits made, defaults to 4
        :param float split_range: the range at which rooms are split, defaults to 0.5
            this value must always be between 0 and 1
            0 means all rooms are split exactly in half
            1 means rooms are split in any random proportion, ranging 0-100%
            A value of 0.5 means that rooms can be cut by 25-75% of their length
        :param int corridor_width: the width (in tiles) of the corridors connecting all rooms together, defaults to 3
        :param int random_seed: the seed used to generate the dungeon, defaults to None
        :return tuple[numpy.ndarray, tuple[int, int], tuple[int, int]]: Returns in the following order:
            A numpy 2-dimentional array in which each element corresponds to a dungeon tile.
            - The values of each tile can be 0 (the tile is empty), 1 (the tile is contained in a room) or 2 (the tile is a corridor)
            The rectangle values of each room of the dungeon, in the format (x-position, y-position, width, height)
        '''
        if random_seed is not None:
            random.seed(random_seed)
        else: random.seed(time.time())

        root = cls.Room(position=(0, 0), size=dungeon_size)

        rooms = [[root]]
        for i in range(splitting_iterations):
            rooms.append([])
            for room in rooms[i]:
                r1, r2 = cls._split(room, split_range=split_range)
                rooms[i+1].append(r1)
                rooms[i+1].append(r2)
        
        room_rects = [cls._room_rectangle(subarea) for subarea in rooms[-1]]

        corridor_rects: list[tuple[int, int, int, int]] = []
        for sublist in rooms[-2::-1]:
            for subarea in sublist:
                corridor_rects.append(cls._corridor_rectangle(area=subarea, corridor_width=corridor_width))

        return (
            cls._rects_to_grid(
                dungeon_size=dungeon_size,
                room_rects=room_rects,
                corridor_rects=corridor_rects
            ),
            room_rects
        )



    class Room:
        def __init__(self, position: tuple[int, int], size: tuple[int, int]) -> None:
            self.position = position
            self.size = size
            self.child_1 = None
            self.child_2 = None
        def __repr__(self) -> str:
            return str(self.position)


    @classmethod
    def _split(cls, room: Room, split_range: float) -> tuple[Room, Room]:
        '''splits a given room into two according to a split_range factor

        :param Room room: the area that should be splitted
        :param float split_range: a factor describing in which proportions the area can be split (see documentation of BSPAlgorithm.generate())
        :return tuple[Room, Room]: the two new rooms that can also be accessed using room.child_1 and room.child_2
        '''
        split_direction: int
        if room.size[0] / room.size[1] >= 1.5:
            split_direction = 0
        elif room.size[1] / room.size[0] >= 1.5:
            split_direction = 1
        else:
            split_direction = random.randint(0, 1)

        split = random.random() * split_range + (1-split_range)/2

        size1: tuple[int, int]
        size2: tuple[int, int]
        pos1: tuple[int, int] = room.position
        pos2: tuple[int, int]
        if split_direction == 0:
            size1 = (round(room.size[0] * split), room.size[1])
            size2 = (room.size[0] - size1[0], room.size[1])
            pos2 = (room.position[0] + size1[0], room.position[1])
        else:
            size1 = (room.size[0], round(room.size[1] * split))
            size2 = (room.size[0], room.size[1] - size1[1])
            pos2 = (room.position[0], room.position[1] + size1[1])

        room1 = cls.Room(position=pos1, size=size1)
        room2 = cls.Room(position=pos2, size=size2)
        room.child_1 = room1
        room.child_2 = room2

        return room1, room2


    @classmethod
    def _room_rectangle(cls, area: Room) -> tuple[int, int, int, int]:
        '''returns values describing a rectangle inside the area given as parameter

        :param Room area: the area in which the desired room should be
        :return tuple[int, int, int, int]: a tuple of format (x-position, y-position, width, height)
        '''
        x1 = random.randint(0, area.size[0] // 4) + area.position[0]
        y1 = random.randint(0, area.size[1] // 4) + area.position[1]
        x2 = random.randint(0, area.size[0] // 4) + area.position[0] + 3 * area.size[0] // 4
        y2 = random.randint(0, area.size[1] // 4) + area.position[1] + 3 * area.size[1] // 4
        return (x1, y1, x2 - x1, y2 - y1)
    

    @classmethod
    def _corridor_rectangle(cls, area: Room, corridor_width: int) -> tuple[int, int, int, int]:
        '''returns values describing a rectangle being a corridor that links the two sub-areas of the one passed as parameter

        :param Room area: an instance of Room, whose attributes child_1 and child_2 are not None
        :param int corridor_width: See documentation of BSPAlgorithm.generate
        :return tuple[int, int, int, int]: a tuple of format (x-position, y-position, width, height)
        '''
        pos1, pos2 = area.child_1.position, area.child_2.position
        s1, s2 = area.child_1.size, area.child_2.size
        c1 = (pos1[0] + s1[0] // 2, pos1[1] + s1[1] // 2)
        c2 = (pos2[0] + s2[0] // 2, pos2[1] + s2[1] // 2)
        
        cw1 = (corridor_width) // 2
        cw2 = cw1 + (1 if corridor_width % 2 == 1 else 0)
        p1: int
        p2: int
        if c1[0] == c2[0]:
            p1 = (c1[0] - cw1, min(c1[1], c2[1]) - cw1)
            p2 = (c1[0] + cw2, max(c1[1], c2[1]) + cw2)
        else:
            p1 = (min(c1[0], c2[0]) - cw1, c1[1] - cw1)
            p2 = (max(c1[0], c2[0]) + cw2, c1[1] + cw2)
        
        return (p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
    

    @classmethod
    def _rects_to_grid(cls, dungeon_size: tuple[int, int],
                       room_rects: list[tuple[int, int, int, int]],
                       corridor_rects: list[tuple[int, int, int, int]]) -> np.ndarray:
        '''takes as parameters the list of all rectangles corresponding to all rooms and corridors of the dungeon and returns a matrix
        in which each tile of the dungeon is associated to a symbol corresponding to its type (0 for empty, 1 for room or 2 for corridor)

        :param tuple[int, int] dungeon_size: the size of the dungeon in which all rect values are contained
        :param list[tuple[int, int, int, int]] room_rects: the rectangles corresponding to the rooms of the dungeon (See documentation of BSPAlgorithm._room_rectangle)
        :param list[tuple[int, int, int, int]] corridor_rects: the rectangles corresponding to the rooms of the dungeon (See documentation of BSPAlgorithm._corridor_rectangle)
        :return numpy.ndarray: the dungeon grid in which each value is the type of the corresponding tile (0 for an empty tile, 1 for a room and 2 for a corridor)
        '''    
        grid = np.zeros(shape=dungeon_size, dtype=int)
        
        for c in corridor_rects:
            grid[c[0]:c[0]+c[2], c[1]:c[1]+c[3]] = 2
        for r in room_rects:
            grid[r[0]:r[0]+r[2], r[1]:r[1]+r[3]] = 1
        
        return grid
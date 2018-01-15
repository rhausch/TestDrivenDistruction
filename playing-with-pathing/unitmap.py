
import battlecode as bc
from collections import deque


# Useful helpers
movable_directions = [d for d in list(bc.Direction) if not bc.Direction.Center]


def empty_map(x, y):
    return [[(bc.Direction.Center, -1) for _ in range(0, y)] for _ in range(0, x)]


def direction_lookup(direction):
    if direction == bc.Direction.North:
        return "↑"
    if direction == bc.Direction.Northwest:
        return "↖"
    if direction == bc.Direction.West:
        return "←"
    if direction == bc.Direction.Southwest:
        return "↙"
    if direction == bc.Direction.South:
        return "↓"
    if direction == bc.Direction.Southeast:
        return "↘"
    if direction == bc.Direction.East:
        return "→"
    if direction == bc.Direction.Northeast:
        return "↗"
    if direction == bc.Direction.Center:
        return "O"


def get_opposite_direction(direction):
    if direction == bc.Direction.North:
        return bc.Direction.South
    if direction == bc.Direction.Northwest:
        return bc.Direction.Southeast
    if direction == bc.Direction.West:
        return bc.Direction.East
    if direction == bc.Direction.Southwest:
        return bc.Direction.Northeast
    if direction == bc.Direction.South:
        return bc.Direction.North
    if direction == bc.Direction.Southeast:
        return bc.Direction.Northwest
    if direction == bc.Direction.East:
        return bc.Direction.West
    if direction == bc.Direction.Northeast:
        return bc.Direction.Southwest
    if direction == bc.Direction.Center:
        return bc.Direction.Center


class Unitmap:
    def __init__(self, gc):
        self.gc = gc
        self.planet =  gc.planet()
        self.planet_map = gc.starting_map(self.planet)
        self.size_x = self.planet_map.width
        self.size_y = self.planet_map.height
        self.map = empty_map(self.size_x, self.size_y)

    def get_map_width(self):
        return self.size_x

    def get_map_height(self):
        return self.size_y

    def get_planet(self):
        return self.planet

    def clear_map(self):
        self.map = empty_map(self.size_x, self.size_y)

    def print_map(self):
        print("Values")
        print("\n".join([" ".join([str(self.map[x][y][1]) for x in range(0, self.size_x)]) for y in range(0, self.size_y)]))
        print("Directions")
        print("\n".join([" ".join([direction_lookup(self.map[x][y][0]) for x in range(0, self.size_x)]) for y in range(0, self.size_y)]))

    def get_location(self, map_location):
        return self.map[map_location.x][map_location.y]

    def get_value_at_location(self, map_location):
        return self.get_location(map_location)[1]

    def get_direction_at_location(self, map_location):
        return self.get_location(map_location)[0]

    def set_location(self, map_location, values):
        self.map[map_location.x][map_location.y] = values

    def generate_map(self, enemies):
        location_queue = deque([enemy.location.map_location() for enemy in enemies if enemy.location.is_on_map()])
        for location in location_queue:
            self.set_location(location, (bc.Direction.Center, 0))

        while location_queue:
            current_location = location_queue.popleft()
            value = self.get_value_at_location(current_location) + 1

            for direction in movable_directions:
                test_location = current_location.add(direction)
                if self.planet_map.on_map(test_location) and self.planet_map.is_passable_terrain_at(test_location):
                    old_value = self.get_value_at_location(test_location)
                    if old_value == -1 or old_value > value:
                        self.set_location(test_location, (get_opposite_direction(direction), value))
                        location_queue.append(test_location)

    def generate_map_from_initial_units(self):
        self.generate_map([unit for unit in self.planet_map.initial_units if unit.team != self.gc.team()])

    def generate_map_from_visible_enemies(self):
        self.generate_map([unit for unit in self.gc.units() if unit.team != self.gc.team()])

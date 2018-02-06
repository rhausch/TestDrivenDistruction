import battlecode as bc
from collections import deque
import util


def empty_map(x, y):
    return [[(bc.Direction.Center, -99) for _ in range(0, y)] for _ in range(0, x)]


class EarthKarbonite:
    def __init__(self, gc):
        self.gc = gc
        self.planet = bc.Planet.Earth
        self.planet_map = gc.starting_map(self.planet)
        self.size_x = self.planet_map.width
        self.size_y = self.planet_map.height
        self.karbonite_map = [[self.planet_map.initial_karbonite_at(util.x_y_to_location_earth(x, y))
                               for y in range(0, self.size_y)] for x in range(0, self.size_x)]
        self.direction_map = [[(bc.Direction.Center, -99) for _ in range(0, self.size_y)] for _ in range(0, self.size_x)]
        self.generate_direction_map()

    def get_map_width(self):
        return self.size_x

    def get_map_height(self):
        return self.size_y

    def get_planet(self):
        return self.planet

    def print_map(self):
        print("Values")
        print("\n".join([" ".join([str(self.map[x][y][1]) for x in range(self.size_x)]) for y in range(self.size_y - 1, -1, -1)]))
        print("Directions")
        print("\n".join(
            ["".join([util.direction_to_str(self.map[x][y][0], self.map[x][y][1]) for x in range(self.size_x)]
                     ) for y in range(self.size_y - 1, -1, -1)]))

    def get_location(self, map_location):
        return self.direction_map[map_location.x][map_location.y]

    def get_value_at_location(self, map_location):
        return self.get_location(map_location)[1]

    def get_direction_at_location(self, map_location):
        return self.get_location(map_location)[0]

    def set_location(self, map_location, values):
        self.direction_map[map_location.x][map_location.y] = values

    def karbonite_at(self, location):
        return self.karbonite_map[location.x][location.y]

    def generate_direction_map(self):
        # location_queue = deque([enemy.location.map_location() for enemy in enemies if enemy.location.is_on_map()])
        # for location in location_queue:
        #    self.set_location(location, (bc.Direction.Center, 0))

        self.direction_map = [[(bc.Direction.Center, -99) for _ in range(0, self.size_y)] for _ in range(0, self.size_x)]

        location_queue = deque()
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                location = util.x_y_to_location_earth(x, y)
                if self.karbonite_at(location):
                    self.direction_map[x][y] = (self.karbonite_at(location), bc.Direction.Center)
                    location_queue.append(location)

        while location_queue:
            current_location = location_queue.popleft()
            value = self.get_value_at_location(current_location) - 1

            for direction in util.movable_directions:
                test_location = current_location.add(direction)
                # print("Testing direction ", direction, " ", get_opposite_direction(direction), " ", test_location, " ", self.planet_map.on_map(test_location), " ", self.planet_map.is_passable_terrain_at(test_location))
                if self.planet_map.on_map(test_location) and self.planet_map.is_passable_terrain_at(test_location):
                    old_value = self.get_value_at_location(test_location)
                    # print("Old value ", old_value, " new value ", value)
                    if old_value < value:
                        self.set_location(test_location, (util.get_opposite_direction(direction), value))
                        location_queue.append(test_location)
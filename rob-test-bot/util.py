import random
import battlecode as bc

gc = None

directions = list(bc.Direction)
movable_directions = [d for d in list(bc.Direction) if d != bc.Direction.Center]
orthogonal_directions = [bc.Direction.North, bc.Direction.East, bc.Direction.South, bc.Direction.West]


def get_random_direction():
    return random.choice(movable_directions)


def direction_to_str(direction, value):
    if value == -1:
        return "[#]"
    if value < 10:
        v = str(value)
    else:
        v = " "

    if direction == bc.Direction.North:
        return v + "↑ "
    if direction == bc.Direction.Northwest:
        # return "↖"
        return "`\\" + v
    if direction == bc.Direction.West:
        return v + "← "
    if direction == bc.Direction.Southwest:
        # return "↙"
        return "./" + v
    if direction == bc.Direction.South:
        return v + "↓ "
    if direction == bc.Direction.Southeast:
        # return "↘"
        return v + "\\."
    if direction == bc.Direction.East:
        return v + "→ "
    if direction == bc.Direction.Northeast:
        # return "↗"
        return v + "/'"
    if direction == bc.Direction.Center:
        return " @ "


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


def rotate_left(direction):
    if direction == bc.Direction.North:
        return bc.Direction.Northwest
    if direction == bc.Direction.Northwest:
        return bc.Direction.West
    if direction == bc.Direction.West:
        return bc.Direction.Southwest
    if direction == bc.Direction.Southwest:
        return bc.Direction.South
    if direction == bc.Direction.South:
        return bc.Direction.Southeast
    if direction == bc.Direction.Southeast:
        return bc.Direction.East
    if direction == bc.Direction.East:
        return bc.Direction.Northeast
    if direction == bc.Direction.Northeast:
        return bc.Direction.North
    if direction == bc.Direction.Center:
        return bc.Direction.Center


def rotate_right(direction):
    if direction == bc.Direction.North:
        return bc.Direction.Northeast
    if direction == bc.Direction.Northwest:
        return bc.Direction.North
    if direction == bc.Direction.West:
        return bc.Direction.Northwest
    if direction == bc.Direction.Southwest:
        return bc.Direction.West
    if direction == bc.Direction.South:
        return bc.Direction.Southwest
    if direction == bc.Direction.Southeast:
        return bc.Direction.South
    if direction == bc.Direction.East:
        return bc.Direction.Southeast
    if direction == bc.Direction.Northeast:
        return bc.Direction.East
    if direction == bc.Direction.Center:
        return bc.Direction.Center


def x_y_to_location_earth(x, y):
    return bc.MapLocation(bc.Planet.Earth, x, y)


def x_y_to_location_mars(x, y):
    return bc.MapLocation(bc.Planet.Mars, x, y)


def get_random_location(planet):
    planet_map = gc.starting_map(planet)
    x = random.randint(0, planet_map.height - 1)
    y = random.randint(0, planet_map.width - 1)
    return bc.MapLocation(planet, x, y)


def get_random_landing_location():
    location = get_random_location(bc.Planet.Mars)
    print("Random Mars Location:", location)
    while not gc.starting_map(bc.Planet.Mars).is_passable_terrain_at(location):
        location = get_random_location(bc.Planet.Mars)
        print("Wasn't valid, tried again and got:", location)
    return location


def get_nearest_unit(location, units):
    closest_unit = None
    closest_distance = 9999
    for unit in units:
        if unit.location.is_on_map():
            unit_distance = unit.location.map_location().distance_squared_to(location)
            if unit_distance < closest_distance:
                closest_distance = unit_distance
                closest_unit = unit
    return closest_unit


def try_harvesting(worker):
    for direction in movable_directions:
        if gc.can_harvest(worker.id, direction):
            # TODO: pick best place to harvest
            gc.harvest(worker.id, direction)
            return True
    return False


def try_unload(structure):
    for direction in movable_directions:
        if gc.can_unload(structure.id, direction):
            gc.unload(structure.id, direction)
            return True
    return False

def try_build(worker, factory):
    if worker.location.map_location().is_adjacent_to(factory.location.map_location()):
        if gc.can_build(worker.id, factory.id):
            gc.build(worker.id, factory.id)


def try_repair(worker, factory):
    if worker.location.map_location().is_adjacent_to(factory.location.map_location()):
        if gc.can_build(worker.id, factory.id):
            gc.build(worker.id, factory.id)


def try_move_strict(robot, direction):
    if gc.can_move(robot.id, direction) and gc.is_move_ready(robot.id):
        gc.move_robot(robot.id, direction)
        return True
    return False


def try_move_loose(robot, direction, tollerance):
    if not gc.is_move_ready(robot.id):
        return False
    if try_move_strict(robot, direction):
        return True
    left = direction
    right = direction
    for i in range(0, tollerance):
        left = rotate_left(left)
        right = rotate_right(right)
        if try_move_strict(robot, left) or try_move_strict(robot, right):
            return True
    return False


bugging = {}


def try_move_bug(robot, target):
    if not gc.is_move_ready(robot.id):
        return False
    current_location = robot.location.map_location()
    if current_location.distance_squared_to(target) == 0:
        return False
    # Get direction to target
    direction = current_location.direction_to(target)
    # If we are not in bug move try and move to the target
    if robot.id not in bugging:
        if try_move_strict(robot, direction):
            return True
        else:
            # Can't move that direction, need to bug
            bugging[robot.id] = direction
    if robot.id in bugging:
        last_dir = bugging[robot.id]
        if gc.can_move(robot.id, last_dir):
            # Way is open, rewind
            test_dir = rotate_right(last_dir)
            while gc.can_move(robot.id, test_dir):
                if test_dir == direction:
                    # no longer need to bug
                    del bugging[robot.id]
                    return try_move_strict(robot, test_dir)
                test_dir = rotate_right(test_dir)
            this_dir = rotate_left(test_dir)
            bugging[robot.id] = this_dir
            return try_move_strict(robot, this_dir)
        else:
            # Way is closed, wind up
            test_dir = rotate_left(last_dir)
            while not gc.can_move(robot.id, test_dir):
                if test_dir == last_dir:
                    # cannot move this turn
                    return False
                test_dir = rotate_left(test_dir)
            # found the way
            this_dir = test_dir
            bugging[robot.id] = this_dir
            return try_move_strict(robot, this_dir)
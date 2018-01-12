import battlecode as bc
import random
import sys
import traceback

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Knight)

my_team = gc.team()
if my_team == bc.Team.Red:
    opponent_team = bc.Team.Blue
else:
    opponent_team = bc.Team.Red

while True:
    # We only support Python 3, which means brackets around print()

    myFactories = []
    myWorkers = []
    myHealers = []
    myKnights = []
    myMages = []
    myRangers = []
    myRockets = []

    someLoc = None

    # frequent try/catches are a good idea
    try:
        # walk through our units:
        for unit in gc.my_units():
            if unit.unit_type == bc.UnitType.Factory:
                myFactories.append(unit)
            elif unit.unit_type == bc.UnitType.Worker:
                myWorkers.append(unit)
            elif unit.unit_type == bc.UnitType.Knight:
                myKnights.append(unit)

            if someLoc is None and unit.location.is_on_map():
                someLoc = unit.location.map_location()
        print('pyround:', gc.round(),
              ' karbonite:', gc.karbonite(),
              ' units:', len(myWorkers), ',', len(myFactories), ',', len(myKnights), ' debug:', someLoc)

        if len(myWorkers) < 5 and gc.karbonite() > 16:
            print('Not enough workers:', gc.karbonite())
            d = random.choice(directions)
            for worker in myWorkers:
                if gc.can_replicate(worker.id, d):
                    gc.replicate(worker.id, d)
                    print('replicated! ', gc.karbonite())
                    break

        if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and (len(myFactories) < 2 or gc.karbonite() > 300):
            d = random.choice(directions)
            for worker in myWorkers:
                if gc.can_blueprint(worker.id, bc.UnitType.Factory, d):
                    gc.blueprint(worker.id, bc.UnitType.Factory, d)
                    break

        factoriesToHeal = []
        for factory in myFactories:
            if factory.health < factory.max_health:
                factoriesToHeal.append(factory)
            garrison = factory.structure_garrison()
            # print('in factory:', factory.id, ' ', len(garrison), ' ', factory.unit_type, ' ', gc.can_produce_robot(factory.id, bc.UnitType.Knight))
            if len(garrison) > 0:
                d = random.choice(directions)
                if gc.can_unload(factory.id, d):
                    # print('unloaded a knight!')
                    gc.unload(factory.id, d)
                    continue
            elif gc.can_produce_robot(factory.id, bc.UnitType.Knight):
                gc.produce_robot(factory.id, bc.UnitType.Knight)
                # print('produced a knight!')
                continue

        # Have workers move to
        # TODO: handle being in a garrison
        for worker in myWorkers:
            location = worker.location
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if gc.can_build(worker.id, other.id):
                        gc.build(worker.id, other.id)
                        # print('built a factory!')
                        # skip moving
                        continue
                    if gc.can_repair(worker.id, other.id):
                        gc.repair(worker.id, other.id)
                        print('repaired a factory!')
                        continue
            if len(factoriesToHeal) > 0: #move towards closest factory
                closestFactory = None
                distance = 999
                mapLocation = location.map_location()
                for factory in factoriesToHeal:
                    loc = factory.location.map_location()
                    dist = mapLocation.distance_squared_to(loc)
                    if dist < distance:
                        distance = dist
                        closestFactory = factory
                if closestFactory is not None:
                    # print("Moving to closest factory:", dist)
                    d = mapLocation.direction_to(factory.location.map_location())
                    if gc.is_move_ready(worker.id) and gc.can_move(worker.id, d):
                        gc.move_robot(worker.id, d)
            else: #move randomly
                d = random.choice(directions)
                if gc.is_move_ready(worker.id) and gc.can_move(worker.id, d):
                    gc.move_robot(worker.id, d)

        enemy_locations = []
        #sense enemies
        if someLoc is not None:
            units = gc.sense_nearby_units_by_team(someLoc, 5001, opponent_team)
            print('enemies sensed:', len(units))
            for unit in units:
                if unit.location.is_on_map():
                    enemy_locations.append(unit.location.map_location())

        # moves knights around randomly
        for knight in myKnights:
            location = knight.location
            if location.is_on_map():
                mapLoc = location.map_location()
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if other.team != my_team and gc.is_attack_ready(knight.id) and gc.can_attack(knight.id, other.id):
                        print('attacked a thing!')
                        gc.attack(knight.id, other.id)
                        continue

                if len(enemy_locations) > 0:
                    closestLoc = None
                    distance = 999
                    mapLocation = location.map_location()
                    for loc in enemy_locations:
                        dist = mapLocation.distance_squared_to(loc)
                        if dist < distance:
                            distance = dist
                            closestLoc = loc
                    if closestLoc is not None:
                        # print("Moving to closest factory:", dist)
                        d = mapLocation.direction_to(closestLoc)
                        if gc.is_move_ready(knight.id) and gc.can_move(knight.id, d):
                            gc.move_robot(knight.id, d)

                else:
                    d = random.choice(directions)
                    if gc.is_move_ready(knight.id) and gc.can_move(knight.id, d):
                        gc.move_robot(knight.id, d)


    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()

    if False:
        # first, factory logic
        if unit.unit_type == bc.UnitType.Factory:
            garrison = unit.structure_garrison()
            if len(garrison) == 0:
                d = random.choice(directions)
                if gc.can_unload(unit.id, d):
                    print('unloaded a knight!')
                    gc.unload(unit.id, d)
                    continue
            elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
                gc.produce_robot(unit.id, bc.UnitType.Knight)
                print('produced a knight!')
                continue

        # first, let's look for nearby blueprints to work on
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    print('built a factory!')
                    # move onto the next unit
                    continue
                if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                    print('attacked a thing!')
                    gc.attack(unit.id, other.id)
                    continue

        # okay, there weren't any dudes around
        # pick a random direction:
        d = random.choice(directions)

        # or, try to build a factory:
        if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
            gc.blueprint(unit.id, bc.UnitType.Factory, d)
        # and if that fails, try to move
        elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            gc.move_robot(unit.id, d)


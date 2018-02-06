import battlecode as bc
import util
import units
import unitmap
import earthkarbonite

class EarthController:

    gc = None
    units = None
    my_team = None
    enemy_team = None
    unit_map = None
    structures_to_heal = []

    def __init__(self, gc):
        self.gc = gc
        util.gc = gc
        self.units = units.Units(gc)
        self.my_team = gc.team()
        self.unit_map = unitmap.Unitmap(gc)
        self.karbonite_map = earthkarbonite.EarthKarbonite(gc)

        if self.my_team == bc.Team.Red:
            self.enemy_team = bc.Team.Blue
        else:
            self.enemy_team = bc.Team.Red

        # let's start off with some research!
        # we can queue as much as we want.
        gc.queue_research(bc.UnitType.Worker)
        gc.queue_research(bc.UnitType.Rocket)
        gc.queue_research(bc.UnitType.Knight)
        gc.queue_research(bc.UnitType.Knight)
        gc.queue_research(bc.UnitType.Knight)

    def run_turn(self):
        # update world status
        self.units.process_units()
        if self.units.enemy_units:
            # There are visible enemies. Lets go get them
            self.unit_map.generate_map_raw(self.units.enemy_units)
        else:
            # No enemies visible. Lets attack starting locations, maybe they are there.
            self.unit_map.generate_map_from_initial_units()
        self.karbonite_map.generate_direction_map()

        if self.gc.round() % 50 == 0:
            self.units.print()

        # reset round based variables
        self.structures_to_heal = []

        # build structures and units
        self.replicate_workers(5)
        if len(self.units.my_factories) < 2 or self.gc.karbonite() > 150:
            self.build_factory()
        if self.gc.round() > 50 and self.gc.karbonite() > 100:
            self.build_rocket()

        # run units
        self.run_factories()
        self.run_rockets()
        self.run_worker()
        self.run_knights()

    def replicate_workers(self, target_num_workers):
        if len(self.units.my_workers) < target_num_workers and self.gc.karbonite() > 16:
            d = util.get_random_direction()
            for worker in self.units.my_workers:
                if self.gc.can_replicate(worker.id, d):
                    self.gc.replicate(worker.id, d)
                    break

    def build_factory(self):
        if self.gc.karbonite() > bc.UnitType.Factory.blueprint_cost():
            d = util.get_random_direction()
            for worker in self.units.my_workers:
                if self.gc.can_blueprint(worker.id, bc.UnitType.Factory, d):
                    self.gc.blueprint(worker.id, bc.UnitType.Factory, d)
                    break

    def build_rocket(self):
        if self.gc.karbonite() > bc.UnitType.Rocket.blueprint_cost():
            d = util.get_random_direction()
            for worker in self.units.my_workers:
                if self.gc.can_blueprint(worker.id, bc.UnitType.Rocket, d):
                    self.gc.blueprint(worker.id, bc.UnitType.Rocket, d)

    def run_factories(self):
        for factory in self.units.my_factories:
            if factory.health < factory.max_health:
                self.structures_to_heal.append(factory)
            garrison = factory.structure_garrison()
            if len(garrison) > 0:
                util.try_unload(factory)
            elif not self.units.my_workers and self.gc.can_produce_robot(factory.id, bc.UnitType.Worker):
                self.gc.produce_robot(factory.id, bc.UnitType.Worker)
            elif self.gc.can_produce_robot(factory.id, bc.UnitType.Knight):
                self.gc.produce_robot(factory.id, bc.UnitType.Knight)

    def run_rockets(self):
        for rocket in self.units.my_rockets:
            if rocket.health < rocket.max_health:
                self.structures_to_heal.append(rocket)
            garrison = rocket.structure_garrison()
            if len(garrison) >= 2:
                self.gc.launch_rocket(rocket.id, util.get_random_landing_location())
            else:
                for worker in self.units.my_workers:
                    if self.gc.can_load(rocket.id, worker.id):
                        self.gc.load(rocket.id, worker.id)
                # hack, use heal list to get workers to move towards rocket
                self.structures_to_heal.append(rocket)

    def run_worker(self):
        for worker in self.units.my_workers:
            location = worker.location
            if location.is_on_map():
                my_location = location.map_location()
                for structure in self.structures_to_heal:
                    if my_location.is_adjacent_to(structure.location.map_location()):
                        util.try_build(worker, structure)
                        util.try_repair(worker, structure)

                util.try_harvesting(worker)

                closest_structure_to_heal = util.get_nearest_unit(my_location, self.structures_to_heal)
                if closest_structure_to_heal:
                    direction = my_location.direction_to(closest_structure_to_heal.location.map_location())
                    util.try_move_loose(worker, direction, 1)
                else:
                    # direction = util.get_random_direction()
                    direction = self.karbonite_map.get_direction_at_location(my_location)
                    util.try_move_loose(worker, direction, 2)

    def run_knights(self):
        for knight in self.units.my_knights:
            location = knight.location
            if location.is_on_map():
                my_location = knight.location.map_location()
                d = self.unit_map.get_direction_at_location(my_location)
                util.try_move_loose(knight, d, 1)

                nearby_enemies = [unit for unit in self.gc.sense_nearby_units(location.map_location(), 2)
                                  if unit.team != self.my_team]
                for enemy in nearby_enemies:
                    if self.gc.is_attack_ready(knight.id) and self.gc.can_attack(knight.id, enemy.id):
                        self.gc.attack(knight.id, enemy.id)
                        continue

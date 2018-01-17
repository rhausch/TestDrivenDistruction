import battlecode as bc
import util
import units


class EarthController:

    gc = None
    units = None
    my_team = None
    enemy_team = None
    structures_to_heal = []

    def __init__(self, gc):
        self.gc = gc
        self.units = units.Units(gc)
        self.my_team = gc.team()
        if self.my_team == bc.Team.Red:
            self.enemy_team = bc.Team.Blue
        else:
            self.enemy_team = bc.Team.Red

    def run_turn(self):
        self.units.process_units()

    def replicate_works(self, target_num_workers):
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
                d = util.get_random_direction()
                if self.gc.can_unload(factory.id, d):
                    self.gc.unload(factory.id, d)
                    continue
            elif self.gc.can_produce_robot(factory.id, bc.UnitType.Knight):
                self.gc.produce_robot(factory.id, bc.UnitType.Knight)
                continue

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

                closest_factory = self.units.get_closest_factory(my_location)
                if closest_factory:
                    direction = my_location.direction_to(closest_factory.location.map_location())
                    util.try_move_loose(worker, direction, 1)
                else:
                    direction = util.get_random_direction()
                    util.try_move_loose(worker, direction, 2)

import battlecode as bc
import util
import units
import unitmap


class MarsController:

    gc = None
    units = None
    my_team = None
    enemy_team = None
    unit_map = None

    def __init__(self, gc):
        self.gc = gc
        self.units = units.Units(gc)
        self.my_team = gc.team()
        self.unit_map = unitmap.Unitmap(gc)
        if self.my_team == bc.Team.Red:
            self.enemy_team = bc.Team.Blue
        else:
            self.enemy_team = bc.Team.Red

    def run_turn(self):
        # update world status
        self.units.process_units()
        if self.units.enemy_units:
            # There are visible enemies. Lets go get them
            self.unit_map.generate_map_raw(self.units.enemy_units)
        else:
            # No enemies visible. Lets attack starting locations, maybe they are there.
            self.unit_map.generate_map_from_initial_units()

        # build structures and units
        self.replicate_workers(5)

        # run units
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

    def run_rockets(self):
        for rocket in self.units.my_rockets:
            garrison = rocket.structure_garrison()
            if garrison:
                util.try_unload(rocket)

    def run_worker(self):
        for worker in self.units.my_workers:
            location = worker.location
            if location.is_on_map():
                util.try_harvesting(worker)
                direction = util.get_random_direction()
                util.try_move_loose(worker, direction, 2)

    def run_knights(self):
        for knight in self.units.my_knights:
            location = knight.location
            if location.is_on_map():
                my_location = knight.location.map_location()
                d = self.unit_map.get_direction_at_location(my_location)
                print("Knight ", knight.id, " got told direction ", d)
                util.try_move_loose(knight, d, 1)

                nearby_enemies = [unit for unit in self.gc.sense_nearby_units(location.map_location(), 2)
                                  if unit.team != self.my_team]
                for enemy in nearby_enemies:
                    if self.gc.is_attack_ready(knight.id) and self.gc.can_attack(knight.id, enemy.id):
                        self.gc.attack(knight.id, enemy.id)
                        continue

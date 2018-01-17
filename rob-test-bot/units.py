import battlecode as bc
import random
import util


class Units:

    gc = None

    my_factories = []
    my_workers = []
    my_healers = []
    my_knights = []
    my_mages = []
    my_rangers = []
    my_rockets = []
    my_units = []

    enemy_factories = []
    enemy_workers = []
    enemy_healers = []
    enemy_knights = []
    enemy_mages = []
    enemy_rangers = []
    enemy_rockets = []
    enemy_units = []

    def __init__(self, gc):
        self.gc = gc
        self.my_team = gc.team()
        self.process_units()

    def clear_units(self):
        self.my_factories = []
        self.my_workers = []
        self.my_healers = []
        self.my_knights = []
        self.my_mages = []
        self.my_rangers = []
        self.my_rockets = []
        self.my_units = []

        self.enemy_factories = []
        self.enemy_workers = []
        self.enemy_healers = []
        self.enemy_knights = []
        self.enemy_mages = []
        self.enemy_rangers = []
        self.enemy_rockets = []
        self.enemy_units = []

    def process_units(self):
        self.clear_units()
        for unit in gc.units():
            if unit.team == self.my_team:
                self.my_units.append(unit)
                if unit.unit_type == bc.UnitType.Factory:
                    self.my_factories.append(unit)
                elif unit.unit_type == bc.UnitType.Worker:
                    self.my_workers.append(unit)
                elif unit.unit_type == bc.UnitType.Knight:
                    self.my_knights.append(unit)
                elif unit.unit_type == bc.UnitType.Ranger:
                    self.my_rangers.append(unit)
                elif unit.unit_type == bc.UnitType.Healer:
                    self.my_healers.append(unit)
                elif unit.unit_type == bc.UnitType.Mage:
                    self.my_mages.append(unit)
                elif unit.unit_type == bc.UnitType.Rocket:
                    self.my_rockets.append(unit)
            else:
                self.enemy_units.append(unit)
                if unit.unit_type == bc.UnitType.Factory:
                    self.enemy_factories.append(unit)
                elif unit.unit_type == bc.UnitType.Worker:
                    self.enemy_workers.append(unit)
                elif unit.unit_type == bc.UnitType.Knight:
                    self.enemy_knights.append(unit)
                elif unit.unit_type == bc.UnitType.Ranger:
                    self.enemy_rangers.append(unit)
                elif unit.unit_type == bc.UnitType.Healer:
                    self.enemy_healers.append(unit)
                elif unit.unit_type == bc.UnitType.Mage:
                    self.enemy_mages.append(unit)
                elif unit.unit_type == bc.UnitType.Rocket:
                    self.enemy_rockets.append(unit)

    def get_closest_enemy(self, location):
        return util.get_nearest_unit(location, self.enemy_units)

    def get_closest_rocket(self, location):
        return util.get_nearest_unit(location, self.my_rockets)

    def get_closest_factory(self, location):
        return util.get_nearest_unit(location, self.my_factories)

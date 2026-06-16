import random
import numpy as np
from terraforge import TownForge
from dyecon import Economy, SubEconomy

import helpfunctions as helpf
import professions
import itemtypes
import buildingtypes

class Game:
	def __init__(self, save_path):
		self.save_path = save_path + "/game_data"
		
		self.calendar = None
		
		self.directions = {
			"north": [0, -1],
			"northwest": [-1, -1],
			"northeast": [1, -1],
			"south": [0, 1],
			"southwest": [-1, 1],
			"southeast": [1, 1],
			"west": [-1, 0],
			"east": [1, 0],
		}
		
		self.location_map = []
		
		self.civilizations = []
		self.settlements = []
		
		self.building_type_objs = buildingtypes.BUILDING_TYPES
		
		self.profession_objs = professions.PROFESSIONS
		
		self.item_type_objs = itemtypes.ITEM_TYPES
		
		base_values = {}
		
		for key, val in self.item_type_objs.items():
			base_values[key] = val.base_value
		
		self.economy = Economy(base_values=base_values)
		
	def inc_time(self, ticks=None):
		if ticks is None:
			ticks = self.get_turn_ticks(self.player)
			
		self.calendar.update(ticks=ticks)
		
	def get_turn_ticks(self, entity):
		if entity.is_location_local():
			return 1
			
		return 60
		
	def get_location(self, entity):
		if entity.lx == None or entity.ly == None or entity.lz == None:
			if self.location_map[entity.gy][entity.gx]:
				location = self.location_map[entity.gy][entity.gx]
				
				return f"{location.name} {entity.gx},{entity.gy}"
				
			else:
				return f"{entity.gx},{entity.gy}"
				
		else:
			location = self.location_map[entity.gy][entity.gx]
			
			if location:
				return f"{location.name} {entity.lx},{entity.ly},{entity.lz}"
			
			return f"{entity.lx},{entity.ly},{entity.lz}"
		
	def random_region_placement(self, entity):
		map_size = self.world_size
		
		entity.gx = random.randint(0, map_size - 1)
		entity.gy = random.randint(0, map_size - 1)
		
	def move_entity(self, entity, dir):
		if entity.lx == None and entity.ly == None:
			self.move_entity_region(entity, dir)
			
		else:
			self.move_entity_tile(entity, dir)
			
	def move_entity_region(self, entity, dir):
		map_size = self.world_size
		
		try:
			cx, cy = self.directions[dir]
			
			tx = (entity.gx + cx) % map_size
			ty = (entity.gy + cy) % map_size
				
			entity.gx = tx
			entity.gy = ty
			entity.last_region_direction = dir
			
			#if isinstance(entity, Player):
			#	self.turns = 60
		
		except KeyError:
			if dir == "in":
				map_size = self.local_map_size
				mid = map_size // 2
				
				if entity.last_region_direction == "north":
					entity.lx = mid
					entity.ly = map_size - 1
					
				elif entity.last_region_direction == "south":
					entity.lx = mid
					entity.ly = 0
					
				elif entity.last_region_direction == "east":
					entity.lx = 0
					entity.ly = mid
					
				elif entity.last_region_direction == "west":
					entity.lx = map_size - 1
					entity.ly = mid
					
				elif entity.last_region_direction == "northeast":
					entity.lx = 0
					entity.ly = map_size - 1
					
				elif entity.last_region_direction == "northwest":
					entity.lx = map_size - 1
					entity.ly = map_size - 1
					
				elif entity.last_region_direction == "southeast":
					entity.lx = 0
					entity.ly = 0
					
				elif entity.last_region_direction == "southwest":
					entity.lx = map_size - 1
					entity.ly = 0
					
				else:
					entity.lx = mid
					entity.ly = mid
				
				entity.lz = 0
				
	def move_entity_tile(self, entity, dir):
		map_size = self.local_map_size
		
		try:
			cx, cy = self.directions[dir]
			
			tx = entity.lx + cx
			ty = entity.ly + cy
			
			if not (0 <= tx < map_size) or not (0 <= ty < map_size):
				entity.lx = None
				entity.ly = None
				entity.lz = None
				
				raise KeyError
				
			local_generator = getattr(self, "local_generator", None)
			
			if local_generator is not None:
				if not local_generator.is_walkable(tx, ty):
					return
			
			entity.lx = tx
			entity.ly = ty
			
			#if isinstance(entity, Player):
			#	self.turns = 1
			
		except KeyError:
			pass
			
	def generate_civilization(self, race):
		civilization_name_system_id = race.get_name_system_id("civilization")
		civilization_name = self.name_system_objs[civilization_name_system_id].get_name()
		
		civilization = Civilization(race, civilization_name)
		
		self.civilizations.append(civilization)
			
	def generate_settlement(self, race):
		map_size = self.world_size
	
		gx = random.randint(0, map_size - 1)
		gy = random.randint(0, map_size - 1)
		
		if self.location_map[gy][gx] is not None:
			return None
		
		biome = self.overworld_generator.get_biome(gx, gy)
		
		if not biome["id"] in race.settlement_biomes:
			return None
			
		settlement_char = race.settlement_char
		settlement_char_color = race.settlement_char_color
		
		settlement_name_system_id = race.get_name_system_id("settlement")
		settlement_name = self.name_system_objs[settlement_name_system_id].get_name()
		
		sub_economy = SubEconomy(self.economy)
		gold = random.randint(race.settlement_gold[0], race.settlement_gold[1])
		
		settlement = Settlement(
			gx, gy, 
			settlement_char, 
			settlement_char_color,
			settlement_name,
			race.settlement_buildings,
			sub_economy,
			gold,
		)
			
		self.settlements.append(settlement)
		
		self.generate_settlement_professions(settlement, race)
		
		self.location_map[gy][gx] = settlement
		
		return settlement
		
	def generate_settlement_professions(self, settlement, race):
		settlement.professions = {}
		
		for profession_id, amount_range in race.settlement_professions.items():
			min_amount, max_amount = amount_range
			
			settlement.professions[profession_id] = random.randint(min_amount, max_amount)
	
	def discover_nearby_locations(self, character):
		new_locations = []
		
		for gy in range(character.gy - 1, character.gy + 2):
			for gx in range(character.gx - 1, character.gx + 2):
				gx %= self.world_size
				gy %= self.world_size
				
				location = self.location_map[gy][gx]
				
				if location is not None and (gx, gy) not in character.memory.known_locations:
					character.memory.known_locations[(gx, gy)] = location
					new_locations.append(location)
					
		return new_locations
	
	def run_settlement_production(self):
		for settlement in self.settlements:
			settlement.run_production(self)
			
	def daily_update(self, calendar=None):
		if calendar is None:
			calendar = self.calendar
		
		if calendar.hour == 12 and not calendar.is_pm:
			self.run_settlement_production()
	
	def get_discovered_locations_quantity(self, entity):
		if hasattr(entity, "memory"):
			memory = entity.memory
			
			return len(memory.known_locations.values())
			
		return 0
	def buy_item(self, buyer, settlement, item_id, quantity=1):
		price = settlement.sub_economy.get_value(item_id) * quantity
		
		if buyer.gold < price:
			return False
			
		if not settlement.sub_economy.has_item(item_id, quantity):
			return False
			
		buyer.gold -= price
		settlement.gold += price
		
		settlement.sub_economy.remove_item(item_id, quantity)
		buyer.add_item(item_id, quantity)
		
		return True
	
	def sell_item(self, seller, settlement, item_id, quantity=1):
		price = settlement.sub_economy.get_value(item_id) * quantity
		
		if not seller.remove_item(item_id, quantity):
			return False
			
		if settlement.gold < price:
			seller.add_item(item_id, quantity)
			return False
			
		seller.gold += price
		settlement.gold -= price
		
		settlement.sub_economy.add_item(item_id, quantity)
		
		return True
	
class Entity:
	def __init__(self):
		self.gx = 0
		self.gy = 0
		
		self.lx = None
		self.ly = None
		self.lz = None
		
		self.last_region_direction = None
			
	def is_location_local(self):
		if self.lx == None or self.ly == None or self.lz == None:
			return False
			
		else:
			return True

#Creatures
class Creature(Entity):
	def __init__(self):
		super().__init__()
		
		self.memory = Memory()
		
class Character(Creature):
	def __init__(self):
		super().__init__()
		
		self.gold = 0
		
		self.inventory = {}
		
	def add_item(self, item_id, quantity=1):
		self.inventory[item_id] = (self.inventory.get(item_id, 0) + quantity)
		
	def remove_item(self, item_id, quantity=1):
		if item_id not in self.inventory:
			return False
			
		self.inventory[item_id] -= quantity
		
		if self.inventory[item_id] <= 0:
			del self.inventory[item_id]
			
		return True
		
class Player(Character):
	def __init__(self):
		super().__init__()
		
		self.char = '@'
		
		self.gold = 100 #For Testing Only. Remove Later!

#Map
class Building:
	def __init__(self, building_data, building_type, settlement=None):
		self.id = building_data["id"]
		
		self.type = building_data["type"]
		
		self.name = building_data["name"]
		
		self.x = building_data["x"]
		self.y = building_data["y"]
		
		self.width = building_data["width"]
		self.height = building_data["height"]
		
		self.color = building_data["color"]
		
		self.door = building_data["door"]
		
		self.building_type = building_type
		
		self.settlement = settlement
		
	def get_name(self):
		return f"{self.settlement.name} {self.building_type.name}"
		
class LocalMapGenerator:
	def __init__(self, biome, seed, map_size):
		self.biome = biome
		
		self.main_color = biome.color
		
		self.seed = seed
		
		self.wraparound = False
		
		self.map_size = map_size
		
		self.tile_outline_color = "black"
		
		self.tile_outline_width = 2
		
		self.generate_map()
		
	def generate_map(self):
		self.map_array = np.full((self.map_size, self.map_size), self.main_color, dtype=object)
		
	def tile_color(self, x, y):
		return self.map_array[y][x]
		
	def is_walkable(self, x, y):
		return True
		
	def get_nearest_walkable(self, x, y):
		return x,y
		
class Settlement:
	def __init__(self, gx, gy, char, char_color, name="Settlement", building_rules=None, sub_economy=None, gold=0):
		self.gx = gx
		self.gy = gy
		
		self.char = char
		
		self.char_color = char_color
		
		self.is_capital = False
		
		self.name = name
		
		if building_rules is None:
			building_rules = {}
			
		self.building_rules = building_rules
		
		self.professions = {}
		
		self.sub_economy = sub_economy
		
		self.gold = gold
		
		self.resources = {
			"fauna": random.randint(0, 100),
			"mineral": random.randint(0, 100),
			"trees": random.randint(0, 100),
		}
		
	def run_production(self, game):
		for profession in game.profession_objs.values():
			profession.produce(self, game)
			
	def get_profession_quantity(self, profession_obj):
		return self.professions.get(profession_obj.id, 0)
		
class TownMapGenerator:
	def __init__(self, game, settlement, seed, map_size):
		self.game = game
		
		self.settlement = settlement
		
		self.seed = seed

		self.map_size = map_size
		
		self.wraparound = False
		
		self.tile_outline_color = "black"
		
		self.tile_outline_width = 2
		
		building_types = self.get_building_types()
		
		self.generator = TownForge(
			building_types=building_types,
			map_size=map_size,
			seed=seed,
		)
		
		self.generate_map()
		
	def generate_map(self):
		self.map_array = self.generator.generate()
		
		self.buildings = []
		
		for building_data in self.generator.buildings:
			building_type = self.game.building_type_objs[building_data["type"]]
		
			building = Building(building_data, building_type, self.settlement)
			
			self.buildings.append(building)
		
	def tile_color(self, x, y):
		tile = self.map_array[y][x]
		
		if tile == TownForge.GROUND:
			return "#3E7C3C"
			
		elif tile == TownForge.BUILDING:
			building = self.generator.get_building_at(x, y)
			
			if building:
				return building["color"]
				
			return "#8B5A2B"
			
		elif tile == TownForge.DOOR:
			return "#FFD700"
			
		return "black"
		
	def is_walkable(self, x, y):
		tile = self.map_array[y][x]
		
		if tile == TownForge.BUILDING:
			return False
			
		return True
		
	def get_nearest_walkable(self, x, y):
		if self.is_walkable(x, y):
			return x, y
			
		for radius in range(1, self.map_size):
			for dy in range(-radius, radius + 1):
				for dx in range(-radius, radius + 1):
					tx = x + dx
					ty = y + dy
					
					if not (0 <= tx < self.map_size and 0 <= ty < self.map_size):
						continue
						
					if self.is_walkable(tx, ty):
						return tx, ty
						
		return x, y
		
	def get_building_types(self):
		building_types = {}
		
		for building_type_id, rule in self.settlement.building_rules.items():
			building_type = self.game.building_type_objs[building_type_id]
			
			building_types[building_type_id] = {
				"id": building_type.id,
				"name": building_type.name,
				"color": building_type.color,
				"size": tuple(building_type.size),
				"min_quantity": rule["min_quantity"],
				"max_quantity": rule["max_quantity"],
				"priority": rule["priority"],
			}
			
		return building_types
		
	def get_building_by_door(self, x, y):
		for building in self.buildings:
			if building.door == (x, y):
				return building
				
		return None
		
#Factions
class Civilization:
	def __init__(self, culture, name):
		self.culture = culture
		
		self.capital = None
		
		self.settlements = []
		
		self.name = name


#Other
class Memory:
	def __init__(self):
		self.known_locations = {}

#Json Objects		
class Biome:
	def __init__(self, *args):
		self.id = args[0]
		
		self.name = args[1]
		
		self.color = args[2]
		
class NameSystem:
	def __init__(self, *args):
		self.id = args[0]
		
		self.name = args[1]
		
		self.parts = args[2]
		
	def get_name(self):
		name = ""
		
		for part in self.parts:
			name_part = random.choice(part)
			
			name += name_part
			
		return name
		
class Race:
	def __init__(self, *args):
		self.id = args[0]
		
		self.name = args[1]
		
		self.civilization_number = args[2]
		
		self.civilization_name_systems = args[3]
		
		self.settlement_number = args[4]
		
		self.settlement_biomes = args[5]
		
		self.settlement_char = args[6]
		
		self.settlement_char_color = args[7]
		
		self.settlement_name_systems = args[8]
		
		self.settlement_buildings = args[9]
		
		self.settlement_professions = args[10]
		
		self.settlement_gold = args[11]
		
	def get_name_system_id(self, name_system_type):
		name_systems = getattr(self, f"{name_system_type}_name_systems")
		
		if len(name_systems) > 0:
			return random.choice(name_systems)
			
		else:
			return None
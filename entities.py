import random
import numpy as np
from terraforge import TownForge
from dyecon import Economy, SubEconomy

import time

import helpfunctions as helpf
import professions
import itemtypes
import buildingtypes
import items
import inventory

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
		
		self.item_type_objs = itemtypes.ITEM_TYPES.copy()
		
		self.entities = []
		
	def init_economy(self):
		base_values = {}
		
		for key, val in self.item_type_objs.items():
			base_values[key] = val.base_value
			
		self.economy = Economy(base_values=base_values)
		
	def inc_time(self, ticks=None):
		if ticks is None:
			ticks = self.get_turn_ticks(self.player)
			
		old_hour = self.calendar.hour
		old_is_pm = self.calendar.is_pm
			
		self.calendar.update(ticks=ticks)
		
		if old_hour != self.calendar.hour or old_is_pm != self.calendar.is_pm:
			return self.hourly_update()
			
		return []
		
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
		
	def get_random_location(self):
		if len(self.settlements) > 0:
			return random.choice(self.settlements)
			
		else:
			return None
		
	def random_region_placement(self, entity):
		map_size = self.world_size
		
		entity.gx = random.randint(0, map_size - 1)
		entity.gy = random.randint(0, map_size - 1)
		
	def random_settlement_placement(self, entity):
		settlement = random.choice(self.settlements)
		
		if not settlement == None:
			entity.gx = settlement.gx
			entity.gy = settlement.gy
		
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
			
	def generate_settlement(self, civilization, race):
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
		
		settlement = Settlement(
			gx, gy,
			civilization,
			settlement_char, 
			settlement_char_color,
			settlement_name,
			race.settlement_buildings,
			sub_economy,
		)
		
		settlement.set_start_currency()
			
		self.settlements.append(settlement)
		
		self.generate_settlement_professions(settlement, race)
		
		self.location_map[gy][gx] = settlement
		
		return settlement
		
	def generate_settlement_professions(self, settlement, race):
		settlement.professions = {}
		settlement.races = {}
		
		for profession_id, amount_range in race.settlement_professions.items():
			min_amount, max_amount = amount_range
			quantity = random.randint(min_amount, max_amount)
			
			settlement.professions[profession_id] = quantity
			
			settlement.races[race.id] = settlement.races.get(race.id, 0) + quantity
	
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
			
	def run_settlement_consumption(self):
		for settlement in self.settlements:
			settlement.consume_needs(self)
			
	def daily_update(self, calendar=None):
		if calendar is None:
			calendar = self.calendar
		
		if calendar.hour == 12 and not calendar.is_pm:
			self.run_settlement_production()
			
			#self.run_settlement_consumption()
			
	def hourly_update(self):
		dead_entities = []
		
		for entity in self.entities:
			if hasattr(entity, "update_needs"):
				entity.update_needs()
				
			if hasattr(entity, "is_dead"):
				if entity.is_dead():
					dead_entities.append(entity)
					
		return dead_entities
	
	def get_discovered_locations_quantity(self, entity):
		if hasattr(entity, "memory"):
			memory = entity.memory
			
			return len(memory.known_locations.values())
			
		return 0
		
	def buy_item(self, buyer, settlement, item_id, quantity=1):
		sub_economy = settlement.sub_economy
		currency = settlement.currency
		
		price = settlement.sub_economy.get_value(item_id) * quantity
			
		if not sub_economy.has_item(item_id, quantity):
			return False
			
		if not buyer.wallet.remove_coins(currency, price):
			return False
			
		settlement.wallet.add_coins(currency, price)
		
		sub_economy.remove_item(item_id, quantity)
		buyer.inventory.add_item(item_id, quantity)
		
		return True
	
	def sell_item(self, seller, settlement, item_id, quantity=1):
		sub_economy = settlement.sub_economy
		currency = settlement.currency
		
		price = settlement.sub_economy.get_value(item_id) * quantity
		
		if not seller.inventory.remove_item(item_id, quantity):
			return False
			
		if not settlement.wallet.remove_coins(currency, price):
			seller.inventory.add_item(item_id, quantity)
			return False
			
		seller.wallet.add_coins(currency, price)
		
		sub_economy.add_item(item_id, quantity)
		
		return True
		
	def create_map(self, location, creator=None, cartography_lvl=1, settlement=None):
		value = 1
		
		success = random.randint(1, 100) <= cartography_lvl
		
		if success:
			gx = location.gx
			gy = location.gy
			
		else:
			gx = random.randint(0, self.world_size - 1)
			gy = random.randint(0, self.world_size - 1)
			
		if settlement is not None:
			value = self.get_map_value(settlement, cartography_lvl)
			
		map_item = items.Map(
			location=location,
			gx=gx,
			gy=gy,
			creator=creator,
			cartography_lvl=cartography_lvl,
			value=value
		)
		
		self.item_type_objs[map_item.id] = map_item
		self.economy.set_base_value(map_item.id, map_item.value)
		
		return map_item
		
	def get_map_value(self, settlement, cartography_lvl):
		parchment_value = settlement.sub_economy.get_value("parchment")
		ink_value = settlement.sub_economy.get_value("ink")
		
		material_cost = parchment_value + ink_value
		
		return int(material_cost + cartography_lvl)
	
	def get_settlement_by_coors(self, gx, gy):
		for settlement in self.settlements:
			if settlement.gx == gx and settlement.gy == gy:
				return settlement
				
		return None
	
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
	def __init__(self, race):
		super().__init__()
		
		self.race = race
		
		self.needs = {
			need_id: need_data["max"] for need_id, need_data in race.needs.items()
		}
		
		self.need_warnings = {
			need_id: False for need_id in self.needs
		}
		
		self.wallet = Wallet()
		
		self.inventory = inventory.Inventory()
		
		self.alive = True
		
	def update_needs(self):
		for need_id, need_data in self.race.needs.items():
			decay = need_data["decay"]
			
			self.needs[need_id] -= decay
			
			if self.needs[need_id] < 0:
				self.needs[need_id] = 0
				
	def consume_item(self, item_id, game):
		item = game.item_type_objs[item_id]
		need_values = getattr(item, "need_values", {})
		
		if not need_values:
			return False
			
		if not self.inventory.remove_item(item_id, 1):
			return False
			
		for need_id, amount in need_values.items():
			if need_id not in self.needs:
				continue
				
			max_value = self.race.needs[need_id]["max"]
			self.needs[need_id] = min(self.needs[need_id] + amount, max_value)
			
		return True
		
	def drop_item(self, item_id, game, quantity=1, source="inventory"):
		if not self.is_location_local():
			return False
			
		if quantity <= 0:
			return False
		
		settlement = game.get_settlement_by_coors(self.gx, self.gy)
		
		if settlement is None:
			return False
			
		if source == "wallet":
			removed = self.wallet.remove_coins(item_id, quantity)
			
		else:
			removed = self.inventory.remove_item(item_id, quantity)
			
		if not removed:
			return False
		
		coors = (
			self.lx,
			self.ly,
			self.lz,
		)
		
		if coors not in settlement.dropped_items:
			settlement.dropped_items[coors] = inventory.Inventory()
			
		settlement.dropped_items[coors].add_item(item_id, quantity=quantity)
		
		return True
		
	def is_dead(self):
		for value in self.needs.values():
			if value <= 0:
				return True
				
		return False
		
	def get_death_reason(self):
		for need_id, value in self.needs.items():
			if value <= 0:
				return need_id
				
		return None
		
	def get_low_needs(self, threshold=25):
		low_needs = []
		
		for need_id, value in self.needs.items():
			if value <= threshold and not self.need_warnings.get(need_id, False):
				low_needs.append(need_id)
				self.need_warnings[need_id] = True
				
			elif value > threshold:
				self.need_warnings[need_id] = False
				
		return low_needs
		
	def add_carried_object(self, item_id, game, quantity=1):
		if item_id in game.coin_objs:
			return self.wallet.add_coins(item_id, quantity)
			
		return self.inventory.add_item(item_id, quantity)
		
	def remove_carried_object(self, item_id, game, quantity=1):
		if item_id in game.coin_objs:
			return self.wallet.remove_coins(item_id, quantity)
			
		return self.inventory.remove_item(item_id, quantity)
		
class Player(Character):
	def __init__(self, race):
		super().__init__(race)
		
		self.char = '@'

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
	def __init__(self, gx, gy, civ, char, char_color, name="Settlement", building_rules=None, sub_economy=None):
		self.gx = gx
		self.gy = gy
		
		self.civilization = civ
		
		self.char = char
		
		self.char_color = char_color
		
		self.is_capital = False
		
		self.name = name
		
		if building_rules is None:
			building_rules = {}
			
		self.building_rules = building_rules
		
		self.professions = {}
		
		self.races = {}
		
		self.sub_economy = sub_economy
		
		self.wallet = Wallet()
		
		self.currency = civ.culture.currency
		
		self.resources = {
			"fauna": random.randint(0, 100),
			"flora": random.randint(0, 100),
			"mineral": random.randint(0, 100),
			"trees": random.randint(0, 100),
			"water": random.randint(0, 100),
		}
		
		self.dropped_items = {}
		
	def run_production(self, game):
		for profession in game.profession_objs.values():
			profession.produce(self, game)
			
	def get_profession_quantity(self, profession_obj):
		return self.professions.get(profession_obj.id, 0)
		
	def get_active_workers(self, profession_obj):
		workers = self.get_profession_quantity(profession_obj)
		
		if workers <= 0:
			return 0
			
		return random.randint(1, workers)
		
	def consume_needs(self, game):	
		for race_id, population in self.races.items():
			race = game.race_objs[race_id]
			
			for need_id in race.needs:
				item_id = self.get_item_for_need(game, need_id)
				
				if item_id is None:
					continue
					
				if self.sub_economy.has_item(item_id, population):
					self.sub_economy.remove_item(item_id, population)
					self.sub_economy.change_modifier(item_id, - 1)
					
				else:
					available = self.sub_economy.get_quantity(item_id)
					
					if available > 0:
						self.sub_economy.remove_item(item_id, available)
						
					self.sub_economy.change_modifier(item_id, 1)
					
	def get_item_for_need(self, game, need_id):
		valid_items = []
		
		for item_id, item in game.item_type_objs.items():
			need_values = getattr(item, "need_values", {})
			
			if need_id in need_values:
				valid_items.append(item_id)
				
		if not valid_items:
			return None
			
		return random.choice(valid_items)
		
	def set_start_currency(self):
		culture = self.civilization.culture
		
		currency = culture.currency
		
		min_coins = culture.settlement_currency[0]
		max_coins = culture.settlement_currency[1]
		
		coins = random.randint(min_coins, max_coins)
		
		self.wallet.add_coins(currency, coins)
		
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
		
		self.currency = culture.currency


#Other
class Memory:
	def __init__(self):
		self.known_locations = {}

class Wallet:
	def __init__(self, coins=None):
		if coins is None:
			coins = {}
			
		self.coins = coins
		
	def get_quantity(self, coin_id):
		return self.coins.get(coin_id, 0)
		
	def set_quantity(self, coin_id, quantity):
		if quantity <= 0:
			self.coins.pop(coin_id, None)
			
		else:
			self.coins[coin_id] = quantity
			
	def add_coins(self, coin_id, quantity=1):
		self.coins[coin_id] = self.get_quantity(coin_id) + quantity
		
		return True
		
	def remove_coins(self, coin_id, quantity=1):
		if self.get_quantity(coin_id) < quantity:
			return False
			
		self.coins[coin_id] -= quantity
		
		if self.coins[coin_id] <= 0:
			del self.coins[coin_id]
			
		return True
		
	def has_coins(self, coin_id, quantity=1):
		return self.get_quantity(coin_id) >= quantity
		
	def get_coins(self):
		return self.coins.items()
		
	def get_coin_ids(self):
		return self.coins.keys()
		
	def clear(self):
		self.coins.clear()

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
		
		self.currency = args[11]
		
		self.settlement_currency = args[12]
		
		self.needs = args[13]
		
	def get_name_system_id(self, name_system_type):
		name_systems = getattr(self, f"{name_system_type}_name_systems")
		
		if len(name_systems) > 0:
			return random.choice(name_systems)
			
		else:
			return None
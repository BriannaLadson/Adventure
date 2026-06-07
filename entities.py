import random
import numpy as np
from terraforge import TownForge

import helpfunctions as helpf

class Game:
	def __init__(self, save_path):
		self.save_path = save_path + "/game_data"
		
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
				
				#if isinstance(entity, Player):
				#	self.turns = 1
				
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
		
		settlement = Settlement(
			gx, gy, 
			settlement_char, 
			settlement_char_color,
			settlement_name,
		)
			
		self.settlements.append(settlement)
		
		self.location_map[gy][gx] = settlement
		
		return settlement
		
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
		
class Player(Creature):
	def __init__(self):
		super().__init__()
		
		self.char = '@'

#Map		
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
	def __init__(self, gx, gy, char, char_color, name="Settlement"):
		self.gx = gx
		self.gy = gy
		
		self.char = char
		
		self.char_color = char_color
		
		self.is_capital = False
		
		self.name = name
		
class TownMapGenerator:
	def __init__(self, settlement, seed, map_size):
		self.settlement = settlement
		
		self.seed = seed

		self.map_size = map_size
		
		self.wraparound = False
		
		self.tile_outline_color = "black"
		
		self.tile_outline_width = 2
		
		self.generator = TownForge(
			map_size=map_size,
			seed=seed,
		)
		
		self.generate_map()
		
	def generate_map(self):
		self.map_array = self.generator.generate()
		
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
		
#Factions
class Civilization:
	def __init__(self, culture, name):
		self.culture = culture
		
		self.capital = None
		
		self.settlements = []
		
		self.name = name

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
		
	def get_name_system_id(self, name_system_type):
		name_systems = getattr(self, f"{name_system_type}_name_systems")
		
		if len(name_systems) > 0:
			return random.choice(name_systems)
			
		else:
			return None
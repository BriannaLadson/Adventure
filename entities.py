import random
from terraforgepro import TerraForgePro

import helpfunctions as helpf

class Game:
	def __init__(self, save_path, content_path):
		self.save_path = save_path
		self.content_path = content_path
		
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
		
		self.local_maps = {}
		
	def load_data(self):
		path = self.save_path + "/content_data"
		
		attrs = {
			"biomes_dict": "biomes",
			"noise_types_dict": "noise_types",
			"ore_deposits_dict": "ore_deposits",
			"region_noise_types_dict": "region_noise_types",
			"tile_types_dict": "tile_types",
		}
		
		for key in attrs:
			data = list(helpf.get_data(path, key).values())
			
			attr = attrs[key]
			
			setattr(self, attr, data)
			
		self.load_biome_tile_type_data()
			
	def load_biome_tile_type_data(self):
		for biome in self.biomes:
			for tile_type in biome.tile_types:
				id = tile_type["id"]
				
				tile_type_obj = helpf.get_obj_by_attr_val(self.tile_types, "id", id)
				
				tile_type["color"] = tile_type_obj.color
			
	def random_region_placement(self, entity):
		map_size = self.world_settings["map_size"]
		
		entity.gx = random.randint(0, map_size - 1)
		entity.gy = random.randint(0, map_size - 1)
		
	def get_or_generate_chunk(self, gx, gy, lz):
		if (gx, gy) not in self.local_maps:
			self.local_maps[(gx, gy)] = {}
			
		if lz not in self.local_maps[(gx, gy)]:
			self.local_maps[(gx, gy)][lz] = self.generate_chunk(gx, gy, lz)
			
		return self.local_maps[(gx, gy)][lz]
		
	def move_entity(self, entity, dir):
		if entity.lx == None and entity.ly == None:
			self.move_entity_region(entity, dir)
			
		else:
			self.move_entity_tile(entity, dir)
			
	def move_entity_region(self, entity, dir):
		map_size = self.world_settings["map_size"]
		
		try:
			coors = self.directions[dir]
			
			cx = coors[0]
			cy = coors[1]
			
			tx = entity.gx + cx
			ty = entity.gy + cy
			
			if tx > map_size - 1:
				tx = 0
				
			if ty > map_size - 1:
				ty = 0
				
			entity.gx = tx
			entity.gy = ty
		
		except KeyError:
			if dir == "in":
				entity.lx = self.world_settings["region_size"] // 2 - 1
				entity.ly = entity.lx
				entity.lz = 0
				
	def move_entity_tile(self, entity, dir):
		map_size = self.world_settings["region_size"]
		
		try:
			coors = self.directions[dir]
			
			cx = coors[0]
			cy = coors[1]
			
			tx = entity.lx + cx
			ty = entity.ly + cy
			
			if tx > map_size - 1 or ty > map_size - 1 or tx < 0 or ty < 0:
				entity.lx = None
				entity.ly = None
				entity.lz = None
				
				raise KeyError
				
			entity.lx = tx
			entity.ly = ty
			
		except KeyError:
			pass
			
			
class Entity:
	def __init__(self):
		self.gx = 0
		self.gy = 0
		
		self.lx = None
		self.ly = None
		self.lz = None
		
	def get_location(self):
		if self.lx == None or self.ly == None or self.lz == None:
			return f"{self.gx},{self.gy}"
			
		else:
			return f"{self.lx},{self.ly},{self.lz}"
			
class Player(Entity):
	def __init__(self):
		super().__init__()
		
class Structure(Entity):
	def __init__(self, gx, gy, lx, ly, lz):
		super().__init__()
			
		self.gx = gx
		self.gy = gy
		
		self.lx = lx
		self.ly = ly
		self.lz = lz
		
class OreDepositStructure(Structure):
	def __init__(self, gx, gy, lx, ly, lz, ore_deposit_type):
		super().__init__(gx, gy, lx, ly, lz)
		
		self.ore_deposit_type = ore_deposit_type
		
		self.color = ore_deposit_type.color
		
	def draw(self, canvas, tile):
		x0, y0, x1, y1 = canvas.bbox(tile)
		
		inset = min(x1 - x0, y1 - y0) * .15
		
		canvas.create_oval(
			x0 + inset, y0 + inset,
			x1 - inset, y1 - inset,
			fill=self.color,
			outline="black",
			width=1,
			tags="map",
		)

#XML
class Biome:
	def __init__(self, *args):
		self.id = args[0]
		
		self.name = args[1]
		
		self.color = args[2]
		
		self.rules = args[3]
		
		self.tile_types = args[4]
		
	def convert_to_dict(self):
		dict = {
			"color": self.color,
			"rules": self.rules,
		}
		
		return dict

class NoiseType:
	def __init__(self, *args):
		self.id = args[0]
		
		self.name = args[1]
		
		self.seed = args[2]
		
		self.min_seed = args[3]
		
		self.max_seed = args[4]
		
		self.octaves = args[5]
		
		self.min_octaves = args[6]
		
		self.max_octaves = args[7]
		
		self.persistence = args[8]
		
		self.min_persistence = args[9]
		
		self.max_persistence = args[10]
		
		self.lacunarity = args[11]
		
		self.min_lacunarity = args[12]
		
		self.max_lacunarity = args[13]
		
		self.falloff_type = args[14]
		
		self.falloff = args[15]
		
		self.min_falloff = args[16]
		
		self.max_falloff = args[17]
		
		self.min_color = args[18]
		
		self.max_color = args[19]
		
		self.zoom = args[20]
		
		self.min_zoom = args[21]
		
		self.max_zoom = args[22]
		
		self.redistribution = args[23]
		self.min_redistribution = args[24]
		self.max_redistribution = args[25]
		
	def convert_to_dict(self):
		dict = {
			"seed": self.seed,
			"octaves": self.octaves,
			"persistence": self.persistence,
			"lacunarity": self.lacunarity,
			"falloff": {
				"type": self.falloff_type,
				"strength": self.falloff,
			},
			"min_color": self.min_color,
			"max_color": self.max_color,
			"zoom": self.zoom,
			"redistribution": self.redistribution,
		}
		
		return dict
	
class OreDepositType:
	def __init__(self, *args):
		self.id = args[0]
		
		self.name = args[1]
		
		self.color = args[2]
	
class TileType:
	def __init__(self, *args):
		self.id = args[0]
		
		self.name = args[1]
		
		self.color = args[2]
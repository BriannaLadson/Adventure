import json
import os

import entities

def load_data(game, data_path="data"):
	for file in os.listdir(data_path):
		if not file.endswith(".json"):
			continue
			
		path = os.path.join(data_path, file)
	
		with open(path, "r", encoding="utf-8") as f:
			data = json.load(f)
		
		if file == "world_settings.json":
			load_world_settings(game, data)
			load_biome_objs(game)
			
		prefix = file.split("_")[0] + "_"
		loader_func = PREFIX_LOADERS.get(prefix)
		
		if loader_func:
			loader_func(game, data)
		
def load_world_settings(game, data):
	game.world_size = data["world_size"]
	
	game.location_map = [
		[None for _ in range(game.world_size)]
		for _ in range(game.world_size)
	]
	
	game.noise_types = data["noise_types"]
	
	game.biomes = data["biomes"]
	
	game.num_islands = data["num_islands"]
	
	game.island_spread = data["island_spread"]
	
	game.min_island_spacing = data["min_island_spacing"]
	
	game.local_map_size = data["local_map_size"]
	
def load_biome_objs(game):
	biome_objs = {}
	
	for biome in game.biomes:
		id = biome["id"]
		
		biome_obj = entities.Biome(
			biome["id"],
			biome["name"],
			biome["color"],
		)
		
		biome_objs[id] = biome_obj
		
	game.biome_objs = biome_objs
	
def load_name_systems(game, data):
	name_system_objs = {}
	
	for name_system in data:
		id = name_system
		
		name_system_data = data[name_system]
		
		name_system_obj = entities.NameSystem(
			id,
			name_system_data["name"],
			name_system_data["parts"],
		)
		
		name_system_objs[id] = name_system_obj
		
	game.name_system_objs = name_system_objs
	
def load_races(game, data):
	race_objs = {}
	
	for race in data:
		id = race
		
		race_data = data[race]
		
		race_obj = entities.Race(
			id,
			race_data["name"],
			race_data["civilization_number"],
			race_data["civilization_name_systems"],
			race_data["settlement_number"],
			race_data["settlement_biomes"],
			race_data["settlement_char"],
			race_data["settlement_char_color"],
			race_data["settlement_name_systems"],
		)
		
		race_objs[id] = race_obj
		
	game.race_objs = race_objs
	
PREFIX_LOADERS = {
	"namesystems_": load_name_systems,
	"races_": load_races,
}
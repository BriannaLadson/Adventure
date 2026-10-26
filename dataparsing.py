import json
import os
from cqcalendar import CQCalendar

import entities
import itemtypes
import professions

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
			
	game.resolve_data_references()
	game.assign_crafting_reactions()

#World Settings		
def load_world_settings(game, data):
	game.world_size = data["world_size"]
	
	load_calendar(game, data)
	
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
	
	game.initial_production_cycles = data["initial_production_cycles"]

def load_calendar(game, data):
	game.calendar = calendar = CQCalendar(
		months = data["calendar"]["months"],
		weekdays = data["calendar"]["weekdays"],
		debug_callbacks=True,
	)
	
	calendar.on_day(game.daily_update)

#Other
def load_bars(game, data):
	bar_objs = {}
	
	for bar in data:
		id = bar
		
		bar_data = data[bar]
		
		bar_obj = itemtypes.BarType(
			id,
			bar_data["name"],
			bar_data["reagents"],
			bar_data["base_value"],
		)
		
		bar_objs[id] = bar_obj
		game.item_type_objs[id] = bar_obj
	
	game.bar_objs = bar_objs

def load_biome_objs(game):
	biome_objs = {}
	
	for biome in game.biomes:
		id = biome["id"]
		
		biome_obj = entities.Biome(
			biome["id"],
			biome["name"],
			biome["color"],
			biome["resources"],
		)
		
		biome_objs[id] = biome_obj
		
	game.biome_objs = biome_objs
	
def load_dietary_profiles(game, data):
	dietary_profile_objs = {}
	
	for dietary_profile in data:
		id = dietary_profile
		
		dietary_profile_data = data[dietary_profile]
		
		dietary_profile_obj = entities.DietaryProfile(
			id,
			dietary_profile_data,
		)
		
		dietary_profile_objs[id] = dietary_profile_obj
		
	game.dietary_profile_objs = dietary_profile_objs
	
def load_fruits(game, data):
	for fruit in data:
		id = fruit
		
		fruit_data = data[fruit]
		
		fruit_obj = itemtypes.FruitType(
			id = id,
			name = fruit_data["name"],
			base_value = fruit_data.get("base_value", 1),
			weight = fruit_data.get("weight", 1),
			can_forage = fruit_data.get("can_forage", False),
			biomes = fruit_data.get("biomes", []),
		)
		
		game.fruit_objs[id] = fruit_obj
		game.item_type_objs[id] = fruit_obj
		
def load_metals(game, data):
	game.metals.update(data)
	
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
			race_data["settlement_buildings"],
			race_data["settlement_professions"],
			race_data["currency"],
			race_data["settlement_currency"],
			race_data["needs"],
			race_data["dietary_profile"],
			race_data["capital_buildings"],
			race_data["character_name_systems"],
		)
		
		race_objs[id] = race_obj
		
	game.race_objs = race_objs
	
def load_roles(game, data):
	game.role_defs.update(data)
	
PREFIX_LOADERS = {
	"dietaryprofiles_": load_dietary_profiles,
	"fruits_": load_fruits,
	"metals_": load_metals,
	"namesystems_": load_name_systems,
	"races_": load_races,
	"roles_": load_roles,
}
import xml.etree.ElementTree as ET
import os
import shelve

import entities

def parse_xml(game):
	raw_data = shelve.open(game.save_path + "/content_data")
	
	children = os.scandir(game.content_path)
	
	for child in children:
		if child.path.endswith(".xml") and child.is_file():
			tree = ET.parse(child)
			root = tree.getroot()
			
			try:
				xml_dict[root.tag](raw_data, root)
				
			except KeyError:
				pass
	
	raw_data.close()
	
	game.load_data()
	
def get_dict(file, key):
	try:
		dict = file[key]
		
	except:
		dict = {}
		
	return dict

	
def parse_world_settings(file, root):
	world_settings_dict = get_dict(file, "world_settings_dict")
	
	#Biome Map
	biome_map_node = root.find("Biome_Map")
	
	noise_types_node = biome_map_node.find("Noise_Types")
	parse_noise_types(file, biome_map_node, noise_types_node)
	
	biomes_node = biome_map_node.find("Biomes")
	parse_biomes(file, biomes_node)
	
	#Region Map
	region_map_node = root.find("Region_Map")
	
	region_noise_types_node = region_map_node.find("Noise_Types")
	parse_noise_types(file, region_map_node, region_noise_types_node)
	
	#Tiles
	tile_types_node = root.find("Tile_Types")
	parse_tile_types(file, tile_types_node)
	
	file["world_settings_dict"] = world_settings_dict
	
def parse_noise_types(file, parent_node, noise_types_node):
	noise_types_dict = get_dict(file, "noise_types_dict")
	region_noise_types_dict = get_dict(file, "region_noise_types_dict")
	
	for noise_type_node in noise_types_node.findall("Noise_Type"):
		id = noise_type_node.find("ID").text
		
		name = noise_type_node.find("Name").text
		
		seed = int(noise_type_node.find("Seed").text)
		min_seed = int(noise_type_node.find("Min_Seed").text)
		max_seed = int(noise_type_node.find("Max_Seed").text)
		
		octaves = int(noise_type_node.find("Octaves").text)
		min_octaves = int(noise_type_node.find("Min_Octaves").text)
		max_octaves = int(noise_type_node.find("Max_Octaves").text)
		
		persistence = float(noise_type_node.find("Persistence").text)
		min_persistence = float(noise_type_node.find("Min_Persistence").text)
		max_persistence = float(noise_type_node.find("Max_Persistence").text)
		
		lacunarity = float(noise_type_node.find("Lacunarity").text)
		min_lacunarity = float(noise_type_node.find("Min_Lacunarity").text)
		max_lacunarity = float(noise_type_node.find("Max_Lacunarity").text)
		
		falloff_type = noise_type_node.find("Falloff_Type").text
		
		falloff = float(noise_type_node.find("Falloff").text)
		min_falloff = float(noise_type_node.find("Min_Falloff").text)
		max_falloff = float(noise_type_node.find("Max_Falloff").text)
		
		min_color = noise_type_node.find("Min_Color").text
		max_color = noise_type_node.find("Max_Color").text
		
		zoom = float(noise_type_node.find("Zoom").text)
		
		min_zoom = float(noise_type_node.find("Min_Zoom").text)
		max_zoom = float(noise_type_node.find("Max_Zoom").text)
		
		redistribution = float(noise_type_node.find("Redistribution").text)
		min_redistribution = float(noise_type_node.find("Min_Redistribution").text)
		max_redistribution = float(noise_type_node.find("Max_Redistribution").text)
		
		obj = entities.NoiseType(
			id,
			name,
			seed,
			min_seed,
			max_seed,
			octaves,
			min_octaves,
			max_octaves,
			persistence,
			min_persistence,
			max_persistence,
			lacunarity,
			min_lacunarity,
			max_lacunarity,
			falloff_type,
			falloff,
			min_falloff,
			max_falloff,
			min_color,
			max_color,
			zoom,
			min_zoom,
			max_zoom,
			redistribution,
			min_redistribution,
			max_redistribution,
		)
		
		if parent_node.tag == "Biome_Map":
			noise_types_dict[id] = obj
			
		else:
			region_noise_types_dict[id] = obj
	
	if parent_node.tag == "Biome_Map":
		file["noise_types_dict"] = noise_types_dict
		
	else:
		file["region_noise_types_dict"] = region_noise_types_dict
	
def parse_biomes(file, biomes_node):
	biomes_dict = get_dict(file, "biomes_dict")
	
	for biome in biomes_node.findall("Biome"):
		id = biome.find("ID").text
		
		name = biome.find("Name").text
		
		color = biome.find("Color").text
		
		rules = {}
		for noise_type_node in biome.findall("Noise_Type"):
			noise_type_id = noise_type_node.find("ID").text
			
			min_value = float(noise_type_node.find("Min_Value").text)
			
			max_value = float(noise_type_node.find("Max_Value").text)
			
			rules[noise_type_id] = (min_value, max_value)
			
		tile_types_node = biome.find("Tile_Types")
		tile_types = []
		
		for tile_type_node in tile_types_node.findall("Tile_Type"):
			tile_rules = {}
			
			for region_noise_type_node in tile_type_node.findall("Region_Noise_Type"):
				tile_rules_id = region_noise_type_node.find("ID").text
				
				tile_rules_min_value = float(region_noise_type_node.find("Min_Value").text)
				tile_rules_max_value = float(region_noise_type_node.find("Max_Value").text)
				
				tile_rules[tile_rules_id] = (tile_rules_min_value, tile_rules_max_value,)
			
			tile_type = {
				"id": tile_type_node.find("ID").text,
				"rules": tile_rules,
			}
			
			tile_types.append(tile_type)
			
		obj = entities.Biome(
			id,
			name,
			color,
			rules,
			tile_types,
		)
		
		biomes_dict[id] = obj
	
	file["biomes_dict"] = biomes_dict
	
def parse_ore_deposits(file, root):
	ore_deposits_dict = get_dict(file, "ore_deposits_dict")
	
	for ore_deposit in root.findall("Ore_Deposit"):
		id = ore_deposit.find("ID").text
		
		name = ore_deposit.find("Name").text
		
		color = ore_deposit.find("Color").text
		
		obj = entities.OreDepositType(
			id,
			name,
			color,
		)
		
		ore_deposits_dict[id] = obj
		
	file["ore_deposits_dict"] = ore_deposits_dict
	
def parse_tile_types(file, tile_types_node):
	tile_types_dict = get_dict(file, "tile_types_dict")
	
	for tile_type in tile_types_node.findall("Tile_Type"):
		id = tile_type.find("ID").text
		
		name = tile_type.find("Name").text
		
		color = tile_type.find("Color").text
		
		obj = entities.TileType(
			id,
			name,
			color,
		)
		
		tile_types_dict[id] = obj
		
	file["tile_types_dict"] = tile_types_dict
	
xml_dict = {
	"OreDeposits": parse_ore_deposits,
	"WorldSettings": parse_world_settings,
}
import random
import numpy as np
from terraforge import TownForge
from dyecon import Economy, SubEconomy
import copy
import time
from collections import deque
import uuid
from copy import deepcopy
from bite import Bite

import helpfunctions as helpf
import professions
import itemtypes
import buildingtypes
import items
import inventory
import crafting
import traits
import aidebug

class Game:
	def __init__(self, save_path):
		self.save_path = save_path + "/game_data"
		
		self.calendar = None
		
		self.sprite_manager = SpriteManager()
		
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
		
		self.regions = {}
		
		self.location_map = []
		
		self.civilizations = []
		self.settlements = []
		
		self.building_type_objs = buildingtypes.BUILDING_TYPES
		
		self.role_defs = {}
		
		self.crafting_reaction_objs = {}
		self.wine_reaction_objs = {}
		
		self.animals = {}
		
		self.fruit_objs = {}
		
		self.metals = {}
		
		self.ore_objs = {}
		
		self.bar_objs = {}
		
		self.coin_objs = {}
		
		self.pickaxe_objs = {}

		
		self.profession_objs = professions.PROFESSIONS
		
		self.item_type_objs = itemtypes.ITEM_TYPES.copy()
		
		self.entities = []
		
		self.initial_production_cycles = 1
		
		self.skills = {
			"blacksmithing": "Blacksmithing",
			"brewing": "Brewing",
			"butchering": "Butchering",
			"cartography": "Cartography",
			"coinsmithing": "Coinsmithing",
			"foraging": "Foraging",
			"hunting": "Hunting",
			"ink_making": "Ink Making",
			"left_hand": "Left Hand",
			"mining": "Mining",
			"paper_making": "Paper Making",
			"right_hand": "Right Hand",
			"smelting": "Smelting",
			"strength": "Strength",
			"speed": "Speed",
			"tanning": "Tanning",
			"wood_burning": "Wood Burning",
			"wood_cutting": "Wood Cutting",
		}
		
		self.max_npcs = 25
		
		self.skill_descriptions = {
			"blacksmithing": "Determines your chance of successfully crafting metal tools.",
			"brewing": "Determines your chance of successfully brewing drinks.",
			"butchering": "Determines your chance of successfully processing animal corpses.",
			"cartography": "Determines how accurately you record location information on maps.",
			"coinsmithing": "Determines your chance of successfully crafting coins.",
			"foraging": "Improves your chances of finding fruit and other harvestable plants.",
			"hunting": "Improves your chance of successfully hunting animals.",
			"ink_making": "Determines your chance of successfully making ink.",
			"mining": "Improves your chance of collecting ore while mining.",
			"paper_making": "Determines your chance of successfully making parchment.",
			"smelting": "Determines your chance of successfully smelting metal.",
			"speed": "Reduces the time required to travel across the overworld.",
			"strength": "Increases the weight you can carry.",
			"tanning": "Determines your chance of successfully processing hides into leather.",
			"wood_burning": "Determines your chance of successfully producing coal.",
			"wood_cutting": "Improves your chances of successfully cutting trees for wood.",
		}
		
		self.debug_npc = None
		self.debug_enabled = True
		self.debug_profession_id = "brewer"

		self.debug_action_limit = 5
		self.debug_history = deque(maxlen=self.debug_action_limit)
		
		self.town_debug_log = []
		self.overworld_debug_log = []
		
		self.body_templates = {}
		
		self.overworld_npcs = []
		
	def init_economy(self):
		base_values = {}
		
		for key, val in self.item_type_objs.items():
			base_values[key] = val.base_value
			
		self.economy = Economy(base_values=base_values)
		
	def init_item_types(self):
		self.item_type_objs = itemtypes.ITEM_TYPES.copy()
		
	def inc_time(self, ticks=None):
		if ticks is None:
			ticks = self.get_turn_ticks(self.player)

		old_hour = self.calendar.hour
		old_is_pm = self.calendar.is_pm

		self.calendar.update(ticks=ticks)

		if old_hour != self.calendar.hour or old_is_pm != self.calendar.is_pm:
			return self.hourly_update()

		return []
		
	def clear_debug_logs(self):
		self.town_debug_log = []
		self.overworld_debug_log = []
		
	def get_movement_ticks(self, entity):
		if entity.is_location_local():
			return 1
			
		base_ticks = self.local_map_size
		
		if not isinstance(entity, Character):
			return base_ticks
			
		speed_level = entity.get_skill_lvl("speed")
		
		speed_modifier = 1 + ((speed_level - 1) / 100)
		
		encumbrance_modifier = 1
		
		if entity.cur_encumbrance > entity.max_encumbrance:
			encumbrance_modifier = (entity.cur_encumbrance / entity.max_encumbrance)
			
		movement_ticks = (base_ticks / speed_modifier) * encumbrance_modifier
			
		return max(1, round(movement_ticks))
		
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
		is_local = entity.is_location_local()
		
		if not is_local:
			movement_modifier = self.local_map_size
			
		else:
			movement_modifier = 1
		
		if entity.lx == None and entity.ly == None:
			moved = self.move_entity_region(entity, dir)
			
		else:
			moved = self.move_entity_tile(entity, dir)
			
		if isinstance(entity, Character):
			entity.train_movement(moved, modifier=movement_modifier)
			
		return moved
			
	def move_entity_region(self, entity, dir):
		map_size = self.world_size
		
		try:
			cx, cy = self.directions[dir]
			
			tx = (entity.gx + cx) % map_size
			ty = (entity.gy + cy) % map_size
				
			entity.gx = tx
			entity.gy = ty
			entity.last_region_direction = dir
			
			return True
		
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
				
				return True
				
		return False
				
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
					return False
			
			entity.lx = tx
			entity.ly = ty
			
			return True
			
		except KeyError:
			return False
			
	def generate_civilization(self, race):
		civilization_name_system_id = race.get_name_system_id("civilization")
		civilization_name = self.name_system_objs[civilization_name_system_id].get_name()
		
		civilization = Civilization(race, civilization_name)
		
		self.civilizations.append(civilization)
			
	def generate_settlement(self, civilization, race, is_capital=False):
		map_size = self.world_size
	
		gx = random.randint(0, map_size - 1)
		gy = random.randint(0, map_size - 1)
		
		if self.location_map[gy][gx] is not None:
			return None
		
		region = self.get_region(gx, gy)
		
		if region.biome.id not in race.settlement_biomes:
			return None
			
		settlement_char = race.settlement_char
		settlement_char_color = race.settlement_char_color
		
		settlement_name_system_id = race.get_name_system_id("settlement")
		settlement_name = self.name_system_objs[settlement_name_system_id].get_name()
		
		sub_economy = SubEconomy(self.economy)
		
		if is_capital:
			building_rules = race.capital_buildings
			
		else:
			building_rules = race.settlement_buildings
		
		settlement = Settlement(
			gx, gy,
			civilization,
			settlement_char, 
			settlement_char_color,
			settlement_name,
			building_rules,
			sub_economy,
			region,
		)
		
		settlement.is_capital = is_capital
		
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
					character.memory.known_locations.add((gx, gy))
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
			
		self.tick_town_departure_timers()
		
		if calendar.hour == 12 and not calendar.is_pm:
			self.run_settlement_production()
			
	def hourly_update(self):
		dead_entities = []
		
		for entity in self.entities:
			if hasattr(entity, "update_needs"):
				entity.update_needs()
				
			if isinstance(entity, Player):
				entity.auto_consume_items(self)
				
			if hasattr(entity, "is_dead"):
				if entity.is_dead():
					dead_entities.append(entity)
					
		self.update_overworld_npcs()
					
		return dead_entities
	
	def get_discovered_locations_quantity(self, entity):
		if hasattr(entity, "memory"):
			memory = entity.memory
			
			return len(memory.known_locations)
			
		return 0
		
	def get_known_locations(self, character):
		locations = []

		for gx, gy in character.memory.known_locations:
			location = self.location_map[gy][gx]
			if location is not None:
				locations.append(location)

		return locations
		
	def buy_item(self, buyer, settlement, item_id, quantity=1):
		sub_economy = settlement.sub_economy
		currency = settlement.currency
		
		price = settlement.sub_economy.get_value(item_id) * quantity
			
		if not sub_economy.has_item(item_id, quantity):
			return False
			
		if not buyer.remove_carried_object(currency, self, price):
			return False
		
		sub_economy.remove_item(item_id, quantity)
		
		buyer.add_carried_object(item_id, self, quantity)
		
		return True
	
	def sell_item(self, seller, settlement, item_id, quantity=1):
		sub_economy = settlement.sub_economy
		currency = settlement.currency
		
		price = settlement.sub_economy.get_value(item_id) * quantity
		
		if not seller.remove_carried_object(item_id, self, quantity):
			return False
			
		seller.add_carried_object(currency, self, price)
		
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
			
		value = self.get_map_value(cartography_lvl)
			
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
		
	def find_carried_parchment(self, character):
		for item_id, quantity in character.inventory.get_items():
			if quantity <= 0:
				continue

			item_type = self.item_type_objs.get(item_id)
			if (
				item_id == "parchment"
				or getattr(item_type, "type_id", None) == "parchment"
			):
				return item_id

		return None	
		
	def craft_map(self, character, location):
		coordinates = (location.gx, location.gy)

		if coordinates not in character.memory.known_locations:
			return False, []

		if "cartography" not in character.skills:
			return False, []

		parchment_id = self.find_carried_parchment(character)
		if parchment_id is None:
			return False, []

		reagents = {
			parchment_id: 1,
			"ink": 1,
		}

		for item_id, quantity in reagents.items():
			if not character.inventory.has_item(item_id, quantity):
				return False, []

		for item_id, quantity in reagents.items():
			character.remove_carried_object(
				item_id,
				self,
				quantity,
			)

		for _ in range(60):
			dead_entities = self.inc_time(ticks=1)

			if character in dead_entities:
				return False, dead_entities

		cartography_level = character.get_skill_lvl("cartography")

		map_item = self.create_map(
			location=location,
			creator=character.full_name.strip() or "None",
			cartography_lvl=cartography_level,
		)

		character.add_carried_object(
			map_item.id,
			self,
			quantity=1,
		)

		character.gain_skill_xp("cartography")

		return True, []	
		
		
	def get_map_value(self, cartography_lvl):
		parchment_value = self.item_type_objs["parchment"].base_value
		ink_value = self.item_type_objs["ink"].base_value

		return int(parchment_value + ink_value + cartography_lvl)
	
	def get_settlement_by_coors(self, gx, gy):
		for settlement in self.settlements:
			if settlement.gx == gx and settlement.gy == gy:
				return settlement
				
		return None
	
	def resolve_data_references(self):
		self.generate_metal_items()
		self.generate_metal_reactions()
		
		self.resolve_race_references()
		
		self.link_forageable_items_to_forager()
		
		self.generate_wines()
		self.generate_wine_reactions()
		
		self.generate_material_reactions()
		
		self.generate_animal_items_and_reactions()
		
	def resolve_race_references(self):
		for race in self.race_objs.values():
			dietary_profile_id = race.dietary_profile
			
			race.dietary_profile = self.dietary_profile_objs[dietary_profile_id]
			
	def link_forageable_items_to_forager(self):
		forageable_items = [
			item_id
			for item_id, item_type in self.item_type_objs.items()
			if item_type.can_forage
		]
		
		self.profession_objs["forager"].outputs = forageable_items
		
	def generate_wines(self):
		self.wine_objs = {}
		
		for fruit in self.fruit_objs.values():
			wine = itemtypes.WineType(fruit)
			
			self.wine_objs[wine.id] = wine
			self.item_type_objs[wine.id] = wine
			
	def generate_animal_items_and_reactions(self):
		for animal_id, animal in self.animals.items():
			animal_name = animal["name"]
			corpse = itemtypes.AnimalCorpseType(animal_id, animal_name)
			hide = itemtypes.AnimalHideType(animal_id, animal_name)
			meat = itemtypes.AnimalMeatType(animal_id, animal_name)
			leather = itemtypes.AnimalLeatherType(animal_id, animal_name)
			parchment = itemtypes.ParchmentType(
				item_id=f"{animal_id}_parchment",
				name=f"{animal_name} Parchment",
				hide_id=hide.id,
			)
			self.item_type_objs[parchment.id] = parchment

			reaction = crafting.CraftingReaction(
				id=f"make_{parchment.id}",
				name=f"Make {parchment.name}",
				reagents=parchment.reagents.copy(),
				products={parchment.id: 1},
				skill="paper_making",
				ticks=60,
			)
			self.crafting_reaction_objs[reaction.id] = reaction

			for item in (corpse, hide, meat, leather):
				self.item_type_objs[item.id] = item

			butchering = crafting.CraftingReaction(
				id=f"butcher_{corpse.id}",
				name=f"Butcher {corpse.name}",
				reagents=hide.reagents.copy(),
				products={
					hide.id: animal["hide_quantity"],
					meat.id: animal["meat_quantity"],
				},
				skill="butchering",
				ticks=60,
			)

			tanning = crafting.CraftingReaction(
				id=f"make_{leather.id}",
				name=f"Make {leather.name}",
				reagents=leather.reagents.copy(),
				products={leather.id: 1},
				skill="tanning",
				ticks=60,
			)

			self.crafting_reaction_objs[butchering.id] = butchering
			self.crafting_reaction_objs[tanning.id] = tanning
			
	def generate_wine_reactions(self):
		for fruit_id, fruit in self.fruit_objs.items():
			wine_id = f"{fruit_id}_wine"
			wine = self.wine_objs[wine_id]
			
			reaction = crafting.CraftingReaction(
				id = f"make_{wine_id}",
				name = f"Make {wine.name}",
				reagents = {
					fruit_id: 1,
					"water": 1,
				},
				products = {
					wine_id: 1,
				},
				skill = "brewing",
				ticks = 60,
			)
			
			self.wine_reaction_objs[reaction.id] = reaction
			self.crafting_reaction_objs[reaction.id] = reaction
			
	def generate_metal_items(self):
		for metal_id, metal in self.metals.items():
			ore = itemtypes.OreType(metal_id, metal)
			bar = itemtypes.BarType(metal_id, metal)
			coin = itemtypes.CoinType(metal_id, metal)
			pickaxe = itemtypes.Pickaxe(metal_id, metal)
			
			self.ore_objs[ore.id] = ore
			self.bar_objs[bar.id] = bar
			self.coin_objs[coin.id] = coin
			self.pickaxe_objs[pickaxe.id] = pickaxe
			
			for item in (ore, bar, coin, pickaxe):
				self.item_type_objs[item.id] = item
				
		self.profession_objs["blacksmith"].outputs = list(self.pickaxe_objs)
			
	def generate_metal_reactions(self):
		item_groups = (
			(self.bar_objs, "smelting"),
			(self.coin_objs, "coinsmithing"),
			(self.pickaxe_objs, "blacksmithing"),
		)
		
		for item_objs, skill_id in item_groups:
			for item in item_objs.values():
				reaction = crafting.CraftingReaction(
					id = f"make_{item.id}",
					name = f"Make {item.name}",
					reagents = item.reagents.copy(),
					products = {item.id: 1},
					skill = skill_id,
					ticks = 60,
				)
				
				self.crafting_reaction_objs[reaction.id] = reaction
				
	def generate_material_reactions(self):
		reaction = crafting.CraftingReaction(
			id = "butcher_animal_corpse",
			name = "Butcher Animal Corpse",
			reagents = {
				"animal_corpse": 1,
			},
			products = {
				"animal_meat": 1,
				"animal_hide": 1,
			},
			skill = "butchering",
			ticks = 60,
		)

		self.crafting_reaction_objs[reaction.id] = reaction

		item_skills = {
			"animal_leather": "tanning",
			"coal": "wood_burning",
			"ink": "ink_making",
			"parchment": "paper_making",
		}

		for item_id, skill_id in item_skills.items():
			item = self.item_type_objs[item_id]

			reaction = crafting.CraftingReaction(
				id = f"make_{item.id}",
				name = f"Make {item.name}",
				reagents = item.reagents.copy(),
				products = {
					item.id: 1,
				},
				skill = skill_id,
				ticks = 60,
			)

			self.crafting_reaction_objs[reaction.id] = reaction
			
	def assign_crafting_reactions(self):
		self.assign_brewer_reactions()
		
		self.assign_butcher_reactions()
		
		self.assign_tanner_reactions()
		
		self.assign_papermaker_reactions()
		
		self.assign_smelter_reactions()
		
		self.assign_blacksmith_reactions()
			
	def assign_brewer_reactions(self):
		brewer = self.profession_objs["brewer"]
		
		brewer.crafting_reactions = list(self.wine_reaction_objs.values())
		
	def assign_butcher_reactions(self):
		butcher = self.profession_objs["butcher"]
		butcher.crafting_reactions = [
			self.crafting_reaction_objs["butcher_animal_corpse"],
		]
		butcher.crafting_reactions.extend(
			self.crafting_reaction_objs[f"butcher_{animal_id}_corpse"]
			for animal_id in self.animals
		)
		
	def assign_tanner_reactions(self):
		tanner = self.profession_objs["tanner"]
		tanner.crafting_reactions = [
			self.crafting_reaction_objs["make_animal_leather"],
		]
		tanner.crafting_reactions.extend(
			self.crafting_reaction_objs[f"make_{animal_id}_leather"]
			for animal_id in self.animals
		)
		
	def assign_blacksmith_reactions(self):
		self.profession_objs["blacksmith"].crafting_reactions = [
			reaction
			for reaction in self.crafting_reaction_objs.values()
			if reaction.skill == "blacksmithing"
		]
		
	def assign_papermaker_reactions(self):
		self.profession_objs["paper_maker"].crafting_reactions = [
			reaction
			for reaction in self.crafting_reaction_objs.values()
			if reaction.skill == "paper_making"
		]
		
	def assign_smelter_reactions(self):
		self.profession_objs["smelter"].crafting_reactions = [
			reaction
			for reaction in self.crafting_reaction_objs.values()
			if reaction.skill == "smelting"
		]
		
	def get_region(self, gx, gy):
		coordinates = (gx, gy)
		
		if coordinates not in self.regions:
			biome_data = self.overworld_generator.get_biome(gx, gy)
			biome = self.biome_objs[biome_data["id"]]
			
			self.regions[coordinates] = Region(gx, gy, biome)
			
		return self.regions[coordinates]
		
	def craft_reaction(self, character, reaction_id):
		reaction = self.crafting_reaction_objs.get(reaction_id)

		if reaction is None:
			return False, []

		if reaction.skill is not None:
			if reaction.skill not in character.skills:
				return False, []

		for item_id, quantity in reaction.reagents.items():
			if item_id in self.coin_objs:
				available = character.wallet.get_quantity(item_id)

			else:
				available = character.inventory.get_quantity(item_id)

			if available < quantity:
				return False, []

		for item_id, quantity in reaction.reagents.items():
			character.remove_carried_object(
				item_id,
				self,
				quantity,
			)

		for _ in range(reaction.ticks):
			dead_entities = self.inc_time(ticks=1)

			if character in dead_entities:
				return False, dead_entities

		if reaction.skill is not None:
			skill_level = character.get_skill_lvl(reaction.skill)
			success_chance = min(100, skill_level)

			character.gain_skill_xp(reaction.skill)

			if random.randint(1, 100) > success_chance:
				return False, []

		for item_id, quantity in reaction.products.items():
			character.add_carried_object(
				item_id,
				self,
				quantity,
			)

		return True, []
		
	def generate_settlement_npcs(self, settlement):
		if settlement.npcs is not None:
			return

		races = {
			race_id: quantity
			for race_id, quantity in settlement.races.items()
			if quantity > 0
		}

		professions = {
			profession_id: quantity
			for profession_id, quantity in settlement.professions.items()
			if quantity > 0
		}

		count = min(
			self.max_npcs,
			sum(races.values()),
			sum(professions.values()),
		)

		settlement.npcs = []

		for _ in range(count):
			race_id = random.choices(
				list(races),
				weights=list(races.values()),
			)[0]

			profession_id = random.choices(
				list(professions),
				weights=list(professions.values()),
			)[0]

			npc = NPC({race_id: 1}, self.race_objs, self.skills)
			npc.generate_body_from_ancestry(self.race_objs, self.body_templates)

			npc.settlement = settlement
			npc.gx = settlement.gx
			npc.gy = settlement.gy
			npc.migration_trait = random.choice(self.migration_traits)
			npc.days_until_departure = npc.migration_trait.roll_stay_length()

			npc.profession_id = profession_id
			npc.profession = self.profession_objs[profession_id]
			npc.profession.give_starting_skills(npc)
			npc.profession.give_starting_reactions(self, npc)
			npc.profession.give_starting_items(self, npc)

			self.give_npc_starting_locations(npc, settlement)
			npc.randomize_skill_potentials()

			race = self.race_objs[race_id]

			if race.sprites and race.sprites_palettes:
				npc.sprite = random.choice(race.sprites)
				npc.sprite_palette = random.choice(race.sprites_palettes)

			name_system_id = race.get_name_system_id("character")

			if name_system_id is not None:
				name_system = self.name_system_objs[name_system_id]
				npc.first_name = name_system.get_name()
				npc.last_name = name_system.get_name()

			npc.full_name = " ".join(
				part for part in (
					npc.first_name,
					npc.middle_name,
					npc.last_name,
				)
				if part
			)

			settlement.npcs.append(npc)

			races[race_id] -= 1
			professions[profession_id] -= 1
			settlement.races[race_id] -= 1
			settlement.professions[profession_id] -= 1
			
	def mine(self, character, settlement):
		if not self.ore_objs:
			return False

		equipped = character.ensure_equipped(
			self,
			self.pickaxe_objs,
		)

		if equipped is None:
			return False

		part_id, pickaxe_id = equipped

		hand_skill = character.body_parts[part_id]["hand_skill"]
		hand_level = character.get_skill_lvl(hand_skill)

		mineral = settlement.region.resources["mineral"]
		mining_level = character.get_skill_lvl("mining")

		base_chance = min(
			100,
			(mineral + mining_level) / 2,
		)

		hand_modifier = 0.5 + (
			min(100, max(1, hand_level)) / 200
		)

		mining_chance = base_chance * hand_modifier

		success = random.uniform(0, 100) < mining_chance

		if success:
			ore_id = random.choice(list(self.ore_objs))

			character.add_carried_object(
				ore_id,
				self,
				quantity=1,
			)

		character.gain_skill_xp("mining")
		character.gain_skill_xp(hand_skill)

		self.wear_equipped_item(
			character,
			part_id,
			amount=1,
		)

		return success
		
	def select_debug_npc(self, settlement, profession_id=None):
		self.debug_history.clear()
		
		candidates = [
			npc
			for npc in settlement.npcs or []
			if npc.alive
			and (
				profession_id is None
				or npc.profession_id == profession_id
			)
		]

		self.debug_npc = (
			random.choice(candidates)
			if candidates
			else None
		)

		if self.debug_npc is not None:
			print(
				f"[DEBUG] Following: {self.debug_npc.full_name} "
				f"({self.debug_npc.profession_id})"
			)

		return self.debug_npc
		
	def individualize_equipped_item(self, character, body_part_id):
		part = character.body_parts.get(body_part_id)

		if part is None:
			return None

		item_id = part.get("equipped_item_id")

		if item_id is None:
			return None

		if character.inventory.get_quantity(item_id) < 1:
			return None

		item = self.item_type_objs[item_id]

		if getattr(item, "is_unique", False):
			return item_id

		individual_item = copy.deepcopy(item)

		individual_item.id = f"item_{uuid.uuid4().hex}"
		individual_item.source_item_id = item_id
		individual_item.is_unique = True

		unique_id = individual_item.id

		self.item_type_objs[unique_id] = individual_item

		self.economy.set_base_value(
			unique_id,
			individual_item.base_value,
		)

		character.inventory.remove_item(item_id, 1)
		character.inventory.add_item(unique_id, 1)

		part["equipped_item_id"] = unique_id

		character.calc_encumbrance(self)

		return unique_id
		
	def item_matches(self, item_id, item_ids):
		if item_id in item_ids:
			return True

		item = self.item_type_objs.get(item_id)

		if item is None:
			return False

		source_item_id = getattr(item, "source_item_id", None)

		return source_item_id is not None and source_item_id in item_ids
		
	def wear_equipped_item(self, character, body_part_id, amount=1):
		if amount <= 0:
			return None

		item_id = self.individualize_equipped_item(
			character,
			body_part_id,
		)

		if item_id is None:
			return None

		item = self.item_type_objs[item_id]

		item.durability = max(
			0,
			item.durability - amount,
		)

		if item.durability == 0:
			for part in character.body_parts.values():
				if part.get("equipped_item_id") == item_id:
					part["equipped_item_id"] = None

			character.inventory.remove_item(item_id, 1)
			character.calc_encumbrance(self)

		return item.durability
		
	def give_npc_starting_locations(self, npc, settlement):
		known_locations = npc.memory.known_locations
		starting_coordinates = (settlement.gx, settlement.gy)
		known_locations.add(starting_coordinates)

		if npc.profession_id != "cartographer":
			return

		locations = {
			(location.gx, location.gy)
			for row in self.location_map
			for location in row
			if location is not None
		}
		locations.add(starting_coordinates)

		cartography_level = min(
			100,
			max(0, npc.get_skill_lvl("cartography")),
		)

		known_quantity = max(
			1,
			int(len(locations) * cartography_level / 100),
		)

		other_locations = sorted(locations - {starting_coordinates})
		known_locations.update(
			random.sample(other_locations, known_quantity - 1)
		)
		
	def get_local_corpse_ids(self, settlement):
		biome_id = settlement.region.biome.id

		return [
			f"{animal_id}_corpse"
			for animal_id, animal in self.animals.items()
			if biome_id in animal["biomes"]
		]	
		
	def tick_town_departure_timers(self):
		player = getattr(self, "player", None)
		if player is None or not player.is_location_local() or player.lz != 0:
			return

		settlement = self.get_settlement_by_coors(player.gx, player.gy)
		if settlement is None:
			return

		for npc in settlement.npcs or []:
			days = getattr(npc, "days_until_departure", None)
			if npc.alive and days is not None and days > 0:
				npc.days_until_departure = days - 1	
		
	def update_overworld_npcs(self):
		for npc in list(getattr(self, "overworld_npcs", [])):
			if npc.alive:
				self.advance_migrant(npc)

	def advance_migrant(self, npc):
		known_towns = {}

		for gx, gy in npc.memory.known_locations:
			location = self.location_map[gy][gx]

			if isinstance(location, Settlement) and location is not npc.previous_settlement:
				known_towns[(gx, gy)] = location

		position = (npc.gx, npc.gy)
		target = getattr(npc, "tile_target", None)

		if known_towns:
			if target not in known_towns:
				target = random.choice(list(known_towns))
		elif target is None or target == position:
			if self.world_size <= 1:
				return

			target = position
			while target == position:
				target = (
					random.randrange(self.world_size),
					random.randrange(self.world_size),
				)

		npc.tile_target = target

		if position != target:
			npc.gx = self.step_overworld_axis(npc.gx, target[0])
			npc.gy = self.step_overworld_axis(npc.gy, target[1])
			discovered = self.discover_nearby_locations(npc)

			if self.debug_enabled:
				discovery_text = ", ".join(
					location.name for location in discovered
				) or "none"

				aidebug.write_log(
					self,
					"overworld_debug_log",
					f"{self.calendar.date_string()} {self.calendar.time_string()} | "
					f"{npc.full_name} traveling | "
					f"position: {position} -> {(npc.gx, npc.gy)} | "
					f"target: {target} | discovered: {discovery_text}",
				)

		if (npc.gx, npc.gy) == target and target in known_towns:
			self.settle_migrant(npc, known_towns[target])

	def step_overworld_axis(self, current, target):
		forward = (target - current) % self.world_size
		if forward == 0:
			return current

		if forward <= self.world_size - forward:
			return (current + 1) % self.world_size

		return (current - 1) % self.world_size

	def settle_migrant(self, npc, settlement):
		self.overworld_npcs.remove(npc)

		npc.settlement = settlement
		npc.tile_target = None
		npc.days_until_departure = npc.migration_trait.roll_stay_length()

		self.generate_settlement_npcs(settlement)
		settlement.npcs.append(npc)
		
		if self.debug_enabled:
			aidebug.write_log(
				self,
				"overworld_debug_log",
				f"{self.calendar.date_string()} {self.calendar.time_string()} | "
				f"{npc.full_name} arrived in {settlement.name} | "
				f"position: {(npc.gx, npc.gy)} | "
				f"days until departure: {npc.days_until_departure}",
			)

		player = getattr(self, "player", None)
		town_map = getattr(self, "local_generator", None)

		if (
			player is not None
			and player.is_location_local()
			and player.lz == 0
			and (player.gx, player.gy) == (settlement.gx, settlement.gy)
			and isinstance(town_map, TownMapGenerator)
			and town_map.settlement is settlement
		):
			self.place_arriving_npcs(town_map)

	def place_arriving_npcs(self, town_map):
		settlement = town_map.settlement
		arrivals = [
			npc for npc in settlement.npcs
			if npc.alive and not npc.is_location_local()
		]
		if not arrivals:
			return

		occupied = {(npc.lx, npc.ly) for npc in settlement.npcs}

		player = getattr(self, "player", None)
		if player is not None:
			occupied.add((player.lx, player.ly))

		free_tiles = [
			(x, y)
			for y, row in enumerate(town_map.map_array)
			for x, tile in enumerate(row)
			if tile == TownForge.GROUND and (x, y) not in occupied
		]
		random.shuffle(free_tiles)

		for npc, (x, y) in zip(arrivals, free_tiles):
			npc.lx, npc.ly, npc.lz = x, y, 0

			if npc not in self.entities:
				self.entities.append(npc)	
		
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
		
		self.char = '@'
		
		self.sprite = None
		self.sprite_palette = None
		
class Character(Creature):
	def __init__(self, ancestry, race_objs, skills):
		super().__init__()
		
		#Ancestry
		self.ancestry = {
			race_id: ratio
			for race_id, ratio in ancestry.items()
			if ratio != 0
		}
		
		if not self.ancestry:
			raise ValueError("A character must have ancestry.")
			
		if any(
			not isinstance(ratio, (int, float)) or not 0 < ratio <= 1
			for ratio in self.ancestry.values()
		):
			raise ValueError("Ancestry ratios must be greater than 0 and at most 1.")
			
		if abs(sum(self.ancestry.values()) - 1.0) > 0.000001:
			raise ValueError("Ancestry ratios must total 1.")
			
		for race_id in self.ancestry:
			if race_id not in race_objs:
				raise ValueError(f"Unknown ancestry: {race_id}")
		
		self.generate_need_definitions(race_objs)
		
		self.needs = {
			need_id: need_data["max"] 
			for need_id, need_data in self.need_definitions.items()
		}
		
		self.need_warnings = {
			need_id: False for need_id in self.needs
		}
		
		self.wallet = Wallet()
		
		self.inventory = inventory.Inventory()
		
		self.alive = True
		
		self.skills = {}
		
		for skill_id, skill_name in skills.items():
			self.skills[skill_id] = {
				"name": skill_name,
				"level": 1,
				"xp": 0,
				"max_xp": 200,
				"potential": 1,
			}
			
		self.handedness = random.choice(traits.HANDEDNESS_TRAITS)
		self.handedness.apply(self)
		
		self.generate_dietary_profile(race_objs)
		
		self.cur_encumbrance = 0
		self.max_encumbrance = 100
		
		self.first_name = ""
		self.middle_name = ""
		self.last_name = ""
		
		self.full_name = f"{self.first_name} {self.middle_name} {self.last_name}"
		
		self.body_template_id = None
		self.body_parts = {}
		
		self.personality_traits = []
		
	def set_full_name(self):
		self.full_name = f"{self.first_name} {self.middle_name} {self.last_name}"
		
	def update_needs(self):
		for need_id, need_data in self.need_definitions.items():
			self.needs[need_id] = max(0, self.needs[need_id] - need_data["decay"])
				
	def consume_item(self, item_id, game):
		need_values = self.get_item_need_values(item_id, game)
		
		if not need_values:
			return False
			
		if not self.remove_carried_object(item_id, game, 1):
			return False
			
		for need_id, amount in need_values.items():
			if need_id not in self.needs:
				continue
				
			max_value = self.need_definitions[need_id]["max"]
			self.needs[need_id] = min(self.needs[need_id] + amount, max_value)
			
		return True
		
	def auto_consume_items(self, game, threshold=25):
		consumed_items = []
		
		for need_id in self.needs:
			while self.needs[need_id] <= threshold:
				item_id = self.find_item_for_need(need_id, game)
				
				if item_id is None:
					break
					
				if not self.consume_item(item_id, game):
					break
					
				consumed_items.append(item_id)
				
		return consumed_items
		
	def find_item_for_need(self, need_id, game):
		for item_id, quantity in self.inventory.get_items():
			if quantity <= 0:
				continue
				
			effects = self.get_item_need_values(item_id, game)
			amount = effects.get(need_id, 0)
			
			if amount > 0:
				return item_id
				
		return None
		
	def drop_item(self, item_id, game, quantity=1, source="inventory"):
		if not self.is_location_local():
			return False
			
		if quantity <= 0:
			return False
		
		settlement = game.get_settlement_by_coors(self.gx, self.gy)
		
		if settlement is None:
			return False
			
		removed = self.remove_carried_object(
			item_id,
			game,
			quantity,
		)
			
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
		
	def generate_need_definitions(self, race_objs):
		race_ids = list(self.ancestry)
		weights = [self.ancestry[race_id] for race_id in race_ids]
		
		need_ids = sorted({
			need_id
			for race_id in race_ids
			for need_id in race_objs[race_id].needs
		})
		
		self.need_definitions = {}
		
		for need_id in need_ids:
			race_id = random.choices(
				race_ids,
				weights=weights,
				k=1,
			)[0]
			
			need_data = race_objs[race_id].needs.get(need_id)
			
			if need_data is not None:
				self.need_definitions[need_id] = need_data.copy()
		
	def generate_dietary_profile(self, race_objs):
		item_ids = sorted({
			item_id
			for race_id in self.ancestry
			for item_id in race_objs[race_id].dietary_profile.items
		})
		
		inherited_items = {}
		
		for item_id in item_ids:
			supporting_races = [
				race_id
				for race_id in self.ancestry
				if item_id in race_objs[race_id].dietary_profile.items
			]
			
			weights = [
				self.ancestry[race_id]
				for race_id in supporting_races
			]
			
			inheritance_chance = min(1.0, sum(weights))
			
			if random.random() >= inheritance_chance:
				continue
				
			race_id = random.choices(
				supporting_races,
				weights=weights,
				k=1
			)[0]
			
			inherited_items[item_id] = (
				race_objs[race_id].dietary_profile.items[item_id].copy()
			)
			
		self.dietary_profile = DietaryProfile("inherited", inherited_items)
		
		self.ensure_diet_compatibility(race_objs)
		
	def ensure_diet_compatibility(self, race_objs):
		for need_id in self.need_definitions:
			supported = any(
				values.get(need_id, 0) > 0
				for values in self.dietary_profile.items.values()
			)
			
			if supported:
				continue
				
			candidates = []
			weights = []
			
			for race_id, ratio in self.ancestry.items():
				profile = race_objs[race_id].dietary_profile
				
				compatible_items = [
					item_id
					for item_id, values in profile.items.items()
					if values.get(need_id, 0) > 0
				]
				
				if compatible_items:
					candidates.append((race_id, compatible_items))
					weights.append(ratio)
					
			if not candidates:
				raise ValueError(f"No ancestry dietary entry can satisfy {need_id}.")
			race_id, compatible_items = random.choices(
				candidates,
				weights = weights,
				k=1,
			)[0]
			
			item_id = random.choice(compatible_items)
			source_values = race_objs[race_id].dietary_profile.items[item_id]
			
			inherited_values = self.dietary_profile.items.setdefault(item_id, {})
			inherited_values[need_id] = source_values[need_id]
		
	def add_carried_object(self, item_id, game, quantity=1):
		if item_id in game.coin_objs:
			success = self.wallet.add_coins(item_id, quantity)
			
		else:
			success = self.inventory.add_item(item_id, quantity)
			
		if success:
			self.calc_encumbrance(game)
			
		return success
		
	def remove_carried_object(self, item_id, game, quantity=1):
		if quantity <= 0:
			return False

		if item_id in game.coin_objs:
			success = self.wallet.remove_coins(item_id, quantity)

		else:
			if self.get_unequipped_quantity(item_id) < quantity:
				return False

			success = self.inventory.remove_item(item_id, quantity)

		if success:
			self.calc_encumbrance(game)

		return success
		
	def calc_encumbrance(self, game):
		self.calc_cur_encumbrance(game)
		
		self.calc_max_encumbrance()
		
	def calc_cur_encumbrance(self, game):
		encumbrance = 0
		
		for item_id, quantity in self.inventory.get_items():
			item_type = game.item_type_objs[item_id]
			encumbrance += item_type.weight * quantity
			
		for coin_id, quantity in self.wallet.get_coins():
			coin_type = game.coin_objs[coin_id]
			encumbrance += coin_type.weight * quantity
			
		self.cur_encumbrance = round(encumbrance, 1)
		
	def calc_max_encumbrance(self):
		self.max_encumbrance = 99 + self.get_skill_lvl("strength")
		
	def get_skill_lvl(self, skill):
		return self.skills[skill]["level"]
		
	def gain_skill_xp(self, skill_id, modifier=1):
		skill = self.skills[skill_id]

		potential = skill.get("potential", 1)

		max_gain = max(
			1,
			min(potential, int((potential * modifier) + 0.5))
		)

		xp_gain = random.randint(1, max_gain)

		skill["xp"] += xp_gain

		while skill["xp"] >= skill["max_xp"]:
			skill["xp"] -= skill["max_xp"]

			skill["level"] += 1

			skill["max_xp"] = (skill["level"] + 1) * 100

			if skill_id == "strength":
				self.calc_max_encumbrance()

		return xp_gain
		
	def train_movement(self, moved=True, modifier=1):
		if self.cur_encumbrance > self.max_encumbrance:
			encumbrance_modifier = (self.cur_encumbrance / self.max_encumbrance)
			
			return self.gain_skill_xp("strength", modifier=modifier * encumbrance_modifier)
			
		if moved:
			return self.gain_skill_xp("speed", modifier=modifier)
			
		return 0
		
	def get_item_need_values(self, item_id, game):
		item_type = game.item_type_objs[item_id]
		
		return self.dietary_profile.get_need_values(item_type)
		
	def find_inventory_item(self, game, item_ids):
		for item_id, quantity in self.inventory.get_items():
			if quantity > 0 and game.item_matches(item_id, item_ids):
				return item_id

		return None
		
	def randomize_skill_potentials(self):
		for skill in self.skills.values():
			skill["potential"] = random.randint(1, 100)
			
	def generate_body(self, template_id, body_templates):
		body_parts = copy.deepcopy(body_templates[template_id])

		for part in body_parts.values():
			part.setdefault("equipped_item_id", None)

		self.body_template_id = template_id
		self.body_parts = body_parts
		
	def generate_body_from_ancestry(self, race_objs, body_templates):
		template_ids = {
			race_objs[race_id].body_template
			for race_id in self.ancestry
		}

		if len(template_ids) != 1:
			raise ValueError(
				"Mixed ancestry uses different body templates; "
				"a body selection rule is required."
			)

		template_id = next(iter(template_ids))

		self.generate_body(template_id, body_templates)
		
	def set_handedness(self, handedness):
		self.handedness = handedness
		self.handedness.apply(self)
		
	def get_free_hand(self):
		free_hands = [
			part_id
			for part_id, part in self.body_parts.items()
			if part.get("hand_skill") in self.skills
			and part.get("equipped_item_id") is None
		]

		if not free_hands:
			return None

		preferred_skill = self.handedness.preferred_hand_skill

		preferred_hands = [
			part_id
			for part_id in free_hands
			if self.body_parts[part_id]["hand_skill"] == preferred_skill
		]

		candidates = preferred_hands or free_hands

		best_level = max(
			self.get_skill_lvl(
				self.body_parts[part_id]["hand_skill"]
			)
			for part_id in candidates
		)

		best_hands = [
			part_id
			for part_id in candidates
			if self.get_skill_lvl(
				self.body_parts[part_id]["hand_skill"]
			) == best_level
		]

		return random.choice(best_hands)
		
	def get_equipped_quantity(self, item_id):
		return sum(
			1
			for part in self.body_parts.values()
			if part.get("equipped_item_id") == item_id
		)

	def get_unequipped_quantity(self, item_id):
		return max(
			0,
			self.inventory.get_quantity(item_id)
			- self.get_equipped_quantity(item_id),
		)

	def equip(self, item_id, body_part_id):
		part = self.body_parts.get(body_part_id)

		if part is None:
			return False

		if part.get("hand_skill") not in self.skills:
			return False

		if part.get("equipped_item_id") is not None:
			return False

		if self.get_unequipped_quantity(item_id) < 1:
			return False

		part["equipped_item_id"] = item_id

		return True

	def auto_equip(self, item_id):
		hand_id = self.get_free_hand()

		if hand_id is None:
			return False

		return self.equip(item_id, hand_id)

	def unequip(self, body_part_id):
		part = self.body_parts.get(body_part_id)

		if part is None:
			return False

		if part.get("equipped_item_id") is None:
			return False

		part["equipped_item_id"] = None

		return True
		
	def find_equipped_item(self, game, item_ids):
		for part_id, part in self.body_parts.items():
			item_id = part.get("equipped_item_id")

			if (
				item_id is not None
				and game.item_matches(item_id, item_ids)
			):
				return part_id, item_id

		return None
		
	def ensure_equipped(self, game, item_ids):
		equipped = self.find_equipped_item(game, item_ids)

		if equipped is not None:
			return equipped

		for item_id, quantity in self.inventory.get_items():
			if quantity <= 0:
				continue

			if not game.item_matches(item_id, item_ids):
				continue

			if self.auto_equip(item_id):
				return self.find_equipped_item(game, item_ids)

		return None
		
		
class Player(Character):
	def __init__(self, ancestry, race_objs, skill_objs):
		super().__init__(ancestry, race_objs, skill_objs)
		
		self.char = '@'

class NPC(Character):
	def __init__(self, ancestry, race_objs, skills):
		super().__init__(ancestry, race_objs, skills)
		
		self.char = "N"
		self.char_color = "black"
		
		self.settlement = None
		self.previous_settlement = None
		
		self.migration_trait = None
		self.days_until_departure = None
		
		self.profession_id = None
		self.profession = None
		self.work_shift = random.choice(traits.WORK_SHIFTS)
		
		self.current_activity = None
		
		self.last_need_check = None
		
		self.handling_need = False
		
		self.actions = []
		
		self.tile_target = None
		self.overworld_target = None

#Map
class Region:
	def __init__(self, gx, gy, biome):
		self.gx = gx
		self.gy = gy
		
		self.biome = biome
		
		self.resources = {
			resource_id: random.randint(
				resource_range[0], 
				resource_range[1]
			)
			for resource_id, resource_range in biome.resource_ranges.items()
		}

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
	def __init__(self, gx, gy, civ, char, char_color, name="Settlement", building_rules=None, sub_economy=None, region=None):
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
		
		self.bank = None
		
		self.region = region
		
		self.resources = self.region.resources
		
		self.dropped_items = {}
		
		self.npcs = None
		
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
		
	def has_building(self, building_id):
		return building_id in self.building_rules
		
class TownMapGenerator:
	def __init__(self, game, settlement, seed, map_size):
		self.game = game
		
		self.settlement = settlement
		
		self.region = region = settlement.region
		
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
			ground_color=region.biome.color
		)
		
		self.generate_map()
		
	def generate_map(self):
		self.map_array = self.generator.generate()
		
		self.buildings = []
		
		for building_data in self.generator.buildings:
			building_type = self.game.building_type_objs[building_data["type"]]
		
			building = Building(building_data, building_type, self.settlement)
			
			self.buildings.append(building)
			
		self.game.generate_settlement_npcs(self.settlement)
		self.game.place_arriving_npcs(self)
		
	def tile_color(self, x, y):
		tile = self.map_array[y][x]
		
		if tile == TownForge.GROUND:
			return self.generator.ground_color
			
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
		
	def get_buildings(self, building_type=None, is_shop=None):
		return [
			building
			for building in self.buildings
			if (
				building_type is None
				or building.type == building_type
			)
			and (
				is_shop is None
				or building.building_type.is_shop == is_shop
			)
		]
		
	def get_building_positions(self, building):
		x, y = building.door

		if not (
			0 <= x < self.map_size
			and 0 <= y < self.map_size
		):
			return set()

		if not self.is_walkable(x, y):
			return set()

		return {(x, y)}
		
	def find_path(self, start, goals, blocked=None):
		goals = set(goals)
		blocked = set() if blocked is None else set(blocked)

		if start in goals:
			return []

		frontier = deque([start])
		previous = {start: None}

		while frontier:
			x, y = frontier.popleft()
			position = (x, y)

			if position in goals:
				path = []

				while position != start:
					path.append(position)
					position = previous[position]

				path.reverse()

				return path

			for dx, dy in (
				(-1, 0),
				(1, 0),
				(0, -1),
				(0, 1),
			):
				next_position = (x + dx, y + dy)
				tx, ty = next_position

				if not (
					0 <= tx < self.map_size
					and 0 <= ty < self.map_size
				):
					continue

				if next_position in previous:
					continue

				if next_position in blocked:
					continue

				if not self.is_walkable(tx, ty):
					continue

				previous[next_position] = position
				frontier.append(next_position)

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
		self.known_locations = set()
		
		self.known_crafting_reactions = {}
		
class SpriteManager(Bite):
	def __init__(self):
		super().__init__()

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
		
		self.resource_ranges = args[3]
		
class DietaryProfile:
	def __init__(self, *args):
		self.id = args[0]
		
		self.items = args[1]
		
	def get_need_values(self, item_type):
		need_values = self.items.get(item_type.id)
		
		if need_values is not None:
			return need_values
			
		type_id = getattr(item_type, "type_id", item_type.id)
			
		return self.items.get(type_id, {})
		
	def copy(self):
		return DietaryProfile(
			self.id,
			copy.deepcopy(self.items),
		)
		
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
		
		self.dietary_profile = args[14]
		
		self.capital_buildings = args[15]
		
		self.character_name_systems = args[16]
		
		self.body_template = args[17]
		
		self.sprites = args[18]
		
		self.sprites_palettes = args[19]
		
	def get_name_system_id(self, name_system_type):
		name_systems = getattr(self, f"{name_system_type}_name_systems")
		
		if len(name_systems) > 0:
			return random.choice(name_systems)
			
		else:
			return None
			
class Skill:
	def __init__(self, *args):
		self.id = args[0]
		
		self.name = args[1]
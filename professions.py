import random

import items

class Profession:
	def __init__(self):
		self.id = "profession"
		
		self.name = "Profession"
		
		self.outputs = []
		
		self.crafting_reactions = []
		
		self.can_craft = True
		
		self.skill = None
		
		self.starting_items = {}
		
		self.starting_skills = []
		
		self.reactions_based_on_skill = False
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		workers = settlement.get_active_workers(self)

		if not self.crafting_reactions and not self.outputs:
			return

		for _ in range(workers):
			if self.crafting_reactions:
				available_reactions = [
					reaction
					for reaction in self.crafting_reactions
					if all(
						sub_economy.has_item(reagent_id, quantity)
						for reagent_id, quantity in reaction.reagents.items()
					)
				]

				# If every recipe is blocked, use one to signal demand.
				reaction = random.choice(
					available_reactions or self.crafting_reactions
				)

				reagents = reaction.reagents
				products = reaction.products

			else:
				item_id = random.choice(self.outputs)
				item_type = game.item_type_objs[item_id]

				reagents = getattr(item_type, "reagents", {})
				products = {item_id: 1}

			can_make = all(
				sub_economy.has_item(reagent_id, quantity)
				for reagent_id, quantity in reagents.items()
			)

			if can_make:
				for reagent_id, quantity in reagents.items():
					sub_economy.remove_item(reagent_id, quantity)
					sub_economy.change_modifier(reagent_id, -quantity)

				for product_id, quantity in products.items():
					if quantity > 0:
						sub_economy.add_item(product_id, quantity)

			else:
				for reagent_id, quantity in reagents.items():
					if not sub_economy.has_item(reagent_id, quantity):
						sub_economy.change_modifier(reagent_id, quantity)
		
	def give_starting_items(self, game, character):
		for item_type_id, quantity in self.starting_items.items():
			variants = [
				item_id
				for item_id, item in game.item_type_objs.items()
				if getattr(item, "type_id", None) == item_type_id
				and item_id != item_type_id
				and not getattr(item, "is_unique", False)
			]

			if variants:
				item_id = random.choice(variants)

			elif item_type_id in game.item_type_objs:
				item_id = item_type_id

			else:
				continue

			character.add_carried_object(
				item_id,
				game,
				quantity=quantity,
			)
		
	def add_work_ai(self, game, character, town_map):
		pass
		
	def give_starting_skills(self, character):
		for skill_id in self.starting_skills:
			skill = character.skills[skill_id]

			skill["level"] = random.randint(1, 100)
			skill["xp"] = 0
			skill["max_xp"] = (skill["level"] + 1) * 100

		character.calc_max_encumbrance()
		
	def give_starting_reactions(self, game, character):
		for skill_id in self.starting_skills:
			reactions = [
				reaction
				for reaction in game.crafting_reaction_objs.values()
				if reaction.skill == skill_id
			]

			if not reactions:
				continue

			if self.reactions_based_on_skill:
				skill_level = min(
					100,
					max(0, character.get_skill_lvl(skill_id)),
				)

				reaction_quantity = max(
					1,
					int(len(reactions) * skill_level / 100),
				)

				reactions = random.sample(
					reactions,
					reaction_quantity,
				)

			for reaction in reactions:
				character.memory.known_crafting_reactions[
					reaction.id
				] = reaction
		
class CustomProfession(Profession):
	def __init__(self, *args):
		super().__init__()
		
		self.id = args[0]
		
		self.name = args[1]
		
class Hunter(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "hunter"
		
		self.name = "Hunter"
		
		self.can_craft = False
		
		self.starting_skills = [
			"hunting",
		]
		
		self.starting_items = {
			"animal_corpse": 5,
		}
		
	def produce(self, settlement, game):
		corpse_ids = game.get_local_corpse_ids(settlement)
		if not corpse_ids:
			return

		hunters = settlement.get_active_workers(self)
		fauna = settlement.resources["fauna"]
		quantity = int(hunters * (fauna / 100))

		for _ in range(quantity):
			corpse_id = random.choice(corpse_ids)
			settlement.sub_economy.add_item(corpse_id, quantity=1)
		
	def add_work_ai(self, game, character, town_map):
		for item_id, item_type in game.item_type_objs.items():
			is_corpse = (
				item_id == "animal_corpse"
				or item_type.type_id == "animal_corpse"
			)
			if not is_corpse or not character.inventory.has_item(item_id):
				continue

			shops = town_map.get_buildings(is_shop=True)
			if shops:
				shop = random.choice(shops)
				character.actions.extend([
					("travel", shop),
					("sell", (shop, item_id)),
				])
			else:
				character.actions.append(("idle", None))
			return

		if game.get_local_corpse_ids(town_map.settlement):
			character.actions.append(("hunt", None))
		else:
			character.actions.append(("idle", None))
		
	
		
class Cartographer(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "cartographer"
		
		self.name = "Cartographer"
		
		self.starting_skills = [
			"cartography",
		]
		
		self.starting_items = {
			"parchment": 5,
			"ink": 5,
		}
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		cartographers = settlement.get_active_workers(self)
		
		for i in range(cartographers):
			parchment_quantity = sub_economy.get_quantity("parchment")
			ink_quantity = sub_economy.get_quantity("ink")
			
			if parchment_quantity < 1:
				sub_economy.change_modifier("parchment", 1)
				
			if ink_quantity < 1:
				sub_economy.change_modifier("ink", 1)
			
			if parchment_quantity >= 1 and ink_quantity >= 1:
				sub_economy.remove_item("parchment", 1)
				sub_economy.remove_item("ink", 1)
				
				sub_economy.change_modifier("parchment", -1)
				sub_economy.change_modifier("ink", -1)
				
				location = game.get_random_location()
				cartography_lvl = random.randint(1, 100)
				
				map_item = game.create_map(location, cartography_lvl=cartography_lvl, settlement=settlement)
				
				sub_economy.add_item(map_item.id)
				
	def add_work_ai(self, game, character, town_map):
		map_id = next(
			(
				item_id
				for item_id, quantity in character.inventory.get_items()
				if quantity > 0
				and isinstance(game.item_type_objs[item_id], items.Map)
			),
			None,
		)

		missing_supplies = [
			item_id
			for item_id in ("ink", "parchment")
			if not character.inventory.has_item(item_id)
		]

		if map_id is not None or missing_supplies:
			shops = town_map.get_buildings(is_shop=True)

			if not shops:
				character.actions.append(("idle", None))
				return

			shop = random.choice(shops)

			character.actions.append(("travel", shop))

			if map_id is not None:
				character.actions.append(
					("sell", (shop, map_id))
				)

			else:
				for item_id in missing_supplies:
					character.actions.append(
						("buy", (shop, item_id))
					)

			return

		locations = list(
			character.memory.known_locations.values()
		)

		if not locations:
			character.actions.append(("idle", None))
			return

		location = random.choice(locations)

		character.actions.append(("make_map", location))			
				
		
class Butcher(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "butcher"
		
		self.name = "Butcher"
		
		self.outputs = [
			"animal_hide",
			"animal_meat",
		]
		
		self.starting_items = {
			"animal_corpse": 5,
		}
		
		self.starting_skills =  [
			"butchering",
		]
		
	def produce(self, settlement, game):
		market = settlement.sub_economy

		for _ in range(settlement.get_active_workers(self)):
			available_reactions = [
				reaction
				for reaction in self.crafting_reactions
				if all(
					market.has_item(item_id, quantity)
					for item_id, quantity in reaction.reagents.items()
				)
			]

			if not available_reactions:
				market.change_modifier("animal_corpse", 1)
				continue

			reaction = random.choice(available_reactions)

			for item_id, quantity in reaction.reagents.items():
				market.remove_item(item_id, quantity)
				market.change_modifier(item_id, -quantity)

			for item_id, quantity in reaction.products.items():
				if quantity > 0:
					market.add_item(item_id, quantity)
				
	def add_work_ai(self, game, character, town_map):
		shops = town_map.get_buildings(is_shop=True)

		if shops:
			shop = random.choice(shops)

			for item_id, item_type in game.item_type_objs.items():
				is_butcher_product = (
					item_id in ("animal_hide", "animal_meat")
					or item_type.type_id in ("animal_hide", "animal_meat")
				)
				if is_butcher_product and character.inventory.has_item(item_id):
					character.actions.extend([
						("travel", shop),
						("sell", (shop, item_id)),
					])
					return

		for reaction in self.crafting_reactions:
			if all(
				character.inventory.has_item(item_id, quantity)
				for item_id, quantity in reaction.reagents.items()
			):
				character.actions.append(("craft", reaction.id))
				return

		if shops:
			settlement = shop.settlement
			market = settlement.sub_economy
			budget = character.wallet.get_quantity(settlement.currency)

			for reaction in self.crafting_reactions:
				# Each butcher recipe requires one corpse.
				corpse_id = next(iter(reaction.reagents))

				if (
					market.has_item(corpse_id, 1)
					and market.get_value(corpse_id) <= budget
				):
					character.actions.extend([
						("travel", shop),
						("buy_material", (shop, corpse_id, 1)),
					])
					return

		character.actions.append(("idle", None))
				
class Brewer(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "brewer"
		
		self.name = "Brewer"
		
		self.outputs = [
			"wine",
		]
		
		self.reactions_based_on_skill = True
		
		self.starting_skills = [
			"brewing",
		]
		
	def give_starting_items(self, game, character):
		super().give_starting_items(game, character)

		reactions = [
			reaction
			for reaction in character.memory.known_crafting_reactions.values()
			if reaction.skill == "brewing"
		]

		if not reactions:
			return

		reaction = random.choice(reactions)

		for item_id, quantity in reaction.reagents.items():
			character.add_carried_object(
				item_id,
				game,
				quantity=quantity * 5,
			)
		
	def add_work_ai(self, game, character, town_map):
		reactions = [
			reaction
			for reaction in character.memory.known_crafting_reactions.values()
			if reaction.skill == "brewing"
		]

		if not reactions:
			character.actions.append(("idle", None))
			return

		product_ids = {
			item_id
			for reaction in game.wine_reaction_objs.values()
			for item_id in reaction.products
		}

		products = [
			item_id
			for item_id in product_ids
			if character.inventory.has_item(item_id)
		]

		if products:
			shops = town_map.get_buildings(is_shop=True)

			if not shops:
				character.actions.append(("idle", None))
				return

			shop = random.choice(shops)

			character.actions.append(("travel", shop))

			for item_id in products:
				character.actions.append(
					("sell", (shop, item_id))
				)

			return

		ready_reactions = [
			reaction
			for reaction in reactions
			if all(
				character.inventory.has_item(item_id, quantity)
				for item_id, quantity in reaction.reagents.items()
			)
		]

		if ready_reactions:
			reaction = random.choice(ready_reactions)

			character.actions.append(
				("craft", reaction.id)
			)

			return

		settlement = town_map.settlement
		sub_economy = settlement.sub_economy

		money = character.wallet.get_quantity(
			settlement.currency,
		)

		candidates = []

		for reaction in reactions:
			missing = {
				item_id: quantity - character.inventory.get_quantity(item_id)
				for item_id, quantity in reaction.reagents.items()
				if character.inventory.get_quantity(item_id) < quantity
			}

			available = all(
				sub_economy.has_item(item_id, quantity)
				for item_id, quantity in missing.items()
			)

			if not available:
				continue

			cost = sum(
				sub_economy.get_value(item_id) * quantity
				for item_id, quantity in missing.items()
			)

			if cost <= money:
				candidates.append((reaction, missing))

		shops = town_map.get_buildings(is_shop=True)

		if not candidates or not shops:
			character.actions.append(("idle", None))
			return

		reaction, missing = random.choice(candidates)
		shop = random.choice(shops)

		character.actions.append(("travel", shop))

		for item_id, quantity in missing.items():
			character.actions.append(
				("buy_material", (shop, item_id, quantity))
			)

		character.actions.append(("craft", reaction.id))
		
class InkMaker(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "ink_maker"
		
		self.name = "Ink Maker"
		
		self.outputs = [
			"ink",
		]
		
		self.starting_skills = [
			"ink_making",
		]
		
		self.starting_items = {
			"coal": 5,
		}
		
	def add_work_ai(self, game, character, town_map):
		if character.inventory.has_item("ink"):
			shops = town_map.get_buildings(is_shop=True)

			if shops:
				shop = random.choice(shops)
				character.actions.extend([
					("travel", shop),
					("sell", (shop, "ink")),
				])
			else:
				character.actions.append(("idle", None))

			return

		reaction = character.memory.known_crafting_reactions.get("make_ink")

		if reaction is None:
			character.actions.append(("idle", None))
			return

		missing = {}

		for item_id, quantity in reaction.reagents.items():
			carried = character.inventory.get_quantity(item_id)

			if carried < quantity:
				missing[item_id] = quantity - carried

		if not missing:
			character.actions.append(("craft", reaction.id))
			return

		settlement = town_map.settlement
		market = settlement.sub_economy

		if not all(
			market.has_item(item_id, quantity)
			for item_id, quantity in missing.items()
		):
			character.actions.append(("idle", None))
			return

		cost = sum(
			market.get_value(item_id) * quantity
			for item_id, quantity in missing.items()
		)

		money = character.wallet.get_quantity(settlement.currency)
		shops = town_map.get_buildings(is_shop=True)

		if cost > money or not shops:
			character.actions.append(("idle", None))
			return

		shop = random.choice(shops)
		character.actions.append(("travel", shop))

		for item_id, quantity in missing.items():
			character.actions.append(
				("buy_material", (shop, item_id, quantity))
			)

		character.actions.append(("craft", reaction.id))
		
class Tanner(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "tanner"
		
		self.name = "Tanner"
		
		self.outputs = [
			"animal_leather"
		]
		
		self.starting_skills = [
			"tanning",
		]
		
		self.starting_items = {
			"animal_hide": 5,
		}
		
	def add_work_ai(self, game, character, town_map):
		shops = town_map.get_buildings(is_shop=True)
		shop = random.choice(shops) if shops else None

		if shop is not None:
			for reaction in self.crafting_reactions:
				leather_id = next(iter(reaction.products))

				if character.inventory.has_item(leather_id):
					character.actions.extend([
						("travel", shop),
						("sell", (shop, leather_id)),
					])
					return

		for reaction in self.crafting_reactions:
			hide_id = next(iter(reaction.reagents))

			if character.inventory.has_item(hide_id):
				character.actions.append(("craft", reaction.id))
				return

		if shop is not None:
			settlement = shop.settlement
			market = settlement.sub_economy
			budget = character.wallet.get_quantity(settlement.currency)

			for reaction in self.crafting_reactions:
				hide_id = next(iter(reaction.reagents))

				if (
					market.has_item(hide_id, 1)
					and market.get_value(hide_id) <= budget
				):
					character.actions.extend([
						("travel", shop),
						("buy_material", (shop, hide_id, 1)),
					])
					return

		character.actions.append(("idle", None))
		
class TreeCutter(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "tree_cutter"
		
		self.name = "Tree Cutter"
		
		self.can_craft = False
		
		self.starting_skills = [
			"wood_cutting",
		]
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		tree_cutters = settlement.get_active_workers(self)
		
		trees = settlement.resources["trees"]
		
		wood_quantity = int(tree_cutters * (trees / 100))
		
		sub_economy.add_item("wood", quantity=wood_quantity)
		
	def add_work_ai(self, game, character, town_map):
		if character.inventory.has_item("wood"):
			shops = town_map.get_buildings(is_shop=True)
			if shops:
				shop = random.choice(shops)
				character.actions.extend([
					("travel", shop),
					("sell", (shop, "wood")),
				])
				return

			character.actions.append(("idle", None))
			return

		if town_map.settlement.resources["trees"] > 0:
			character.actions.append(("cut_tree", None))
		else:
			character.actions.append(("idle", None))
		
class PaperMaker(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "paper_maker"
		
		self.name = "Paper Maker"
		
		self.outputs = [
			"parchment"
		]
		
class WoodBurner(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "wood_burner"
		
		self.name = "Wood Burner"
		
		self.outputs = [
			"coal"
		]
		
class Miner(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "miner"
		
		self.name = "Miner"
		
		self.outputs = []
		
		self.can_craft = False
		
		self.starting_items = {
			"pickaxe": 1,
		}
		
		self.starting_skills = [
			"mining",
		]
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		miners = settlement.get_active_workers(self)
		
		mineral = settlement.resources["mineral"]
		
		ore_quantity = int(miners * (mineral / 100))
		
		for _ in range(ore_quantity):
			ore = random.choice(list(game.ore_objs.keys()))
			
			sub_economy.add_item(ore, quantity=1)
			
	def add_work_ai(self, game, character, town_map):
		ore_id = character.find_inventory_item(
			game,
			game.ore_objs,
		)

		if ore_id is not None:
			shops = town_map.get_buildings(is_shop=True)

			if shops:
				shop = random.choice(shops)

				character.actions.extend([
					("travel", shop),
					("sell", (shop, ore_id)),
				])

			return

		pickaxe_id = character.find_inventory_item(
			game,
			game.pickaxe_objs,
		)

		if pickaxe_id is None:
			shops = town_map.get_buildings(is_shop=True)

			if shops:
				shop = random.choice(shops)

				character.actions.extend([
					("travel", shop),
					("buy", (shop, "pickaxe")),
				])

			return

		if not game.ore_objs:
			return

		mines = town_map.get_buildings(
			building_type="mine_building",
		)

		if mines:
			mine_building = random.choice(mines)

			character.actions.extend([
				("travel", mine_building),
				("mine", None),
			])
			
class Smelter(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "smelter"
		
		self.name = "Smelter"
		
		self.outputs = []
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		smelters = settlement.get_active_workers(self)
		
		bar_ids = list(game.bar_objs.keys())
		
		if not bar_ids:
			return
		
		for _ in range(smelters):
			bar_id = random.choice(bar_ids)
			bar_obj = game.bar_objs[bar_id]
			reagents = getattr(bar_obj, "reagents", {})
			
			can_make = all(
				sub_economy.has_item(reagent_id, amount) for reagent_id, amount in reagents.items()
			)
			
			if can_make:
				for reagent_id, amount in reagents.items():
					sub_economy.remove_item(reagent_id, amount)
					sub_economy.change_modifier(reagent_id, -amount)
					
				sub_economy.add_item(bar_id, 1)
				
			else:
				for reagent_id, amount in reagents.items():
					if not sub_economy.has_item(reagent_id, amount):
						sub_economy.change_modifier(reagent_id, amount)
			
class Coinsmith(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "coinsmith"
		
		self.name = "Coinsmith"
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		coinsmiths = settlement.get_active_workers(self)
		
		coin_ids = list(game.coin_objs)
		
		if not coin_ids:
			return
			
		for _ in range(coinsmiths):
			coin_id = random.choice(coin_ids)
			
			coin = game.coin_objs[coin_id]
			
			reagents = coin.reagents
			
			can_make = all(
				sub_economy.has_item(reagent_id, quantity)
				for reagent_id, quantity in reagents.items()
			)
			
			if can_make:
				for reagent_id, quantity in reagents.items():
					sub_economy.remove_item(reagent_id, quantity)
					
					sub_economy.change_modifier(reagent_id, -quantity)
					
				settlement.wallet.add_coins(coin_id, 1)
				
			else:
				for reagent_id, quantity in reagents.items():
					if not sub_economy.has_item(reagent_id, quantity):
						sub_economy.change_modifier(reagent_id, quantity)
					
class WaterCollector(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "water_collector"
		
		self.name = "Water Collector"
		
		self.outputs = [
			"water"
		]
		
		self.can_craft = False
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		water_collectors = settlement.get_active_workers(self)
		
		water = settlement.resources["water"]
		
		water_quantity = int(water_collectors * (water / 100))
		
		sub_economy.add_item("water", quantity=water_quantity)
		
class Forager(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "forager"
		
		self.name = "Forager"
		
		self.outputs = [
			"fruit",
			"water",
		]
		
		self.can_craft = False
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		foragers = settlement.get_active_workers(self)
		
		flora = settlement.resources["flora"]
		water = settlement.resources["water"]
		
		biome_id = settlement.region.biome.id
		
		fruit_outputs = [
			fruit_id 
			for fruit_id, fruit in game.fruit_objs.items()
			if fruit.can_forage
			and biome_id in fruit.biomes
		]
		
		for _ in range(foragers):
			forage_type = random.choice(["fruit", "water"])
			
			if forage_type == "water":
				chance = water
				forage_item = "water"
				
			else:
				if not fruit_outputs:
					continue
					
				chance = flora
				forage_item = random.choice(fruit_outputs)
				
			if random.randint(1, 100) <= chance:
				sub_economy.add_item(forage_item, quantity=1)
	
class Blacksmith(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "blacksmith"
		
		self.name = "Blacksmith"
	
PROFESSIONS = {
	"hunter": Hunter(),
	"water_collector": WaterCollector(),
	"miner": Miner(),
	"tree_cutter": TreeCutter(),
	"forager": Forager(),
	"wood_burner": WoodBurner(),
	"butcher": Butcher(),
	"ink_maker": InkMaker(),
	"tanner": Tanner(),
	"paper_maker": PaperMaker(),
	"cartographer": Cartographer(),
	"smelter": Smelter(),
	"coinsmith": Coinsmith(),
	"brewer": Brewer(),
	"blacksmith": Blacksmith(),
}
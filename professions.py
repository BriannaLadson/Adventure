import random

import items
import aidebug

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
		
	def run_offscreen_ai(self, game, npc, settlement):
		return False
		
	def log_offscreen_result(self, game, npc, settlement, result):
		if not game.debug_enabled:
			return

		calendar = game.calendar
		aidebug.write_log(
			game,
			"overworld_debug_log",
			f"{calendar.date_string()} {calendar.time_string()} | "
			f"{settlement.name} | {npc.full_name} | {self.name} | {result}",
		)
		
	def run_offscreen_hide_crafting(
		self, game, npc, settlement, *, skill_id, product_name,
	):
		has_market = settlement.has_building("market_building")

		if has_market:
			for reaction in self.crafting_reactions:
				product_id = next(iter(reaction.products))
				if not npc.inventory.has_item(product_id):
					continue

				if game.sell_item(npc, settlement, product_id):
					self.log_offscreen_result(
						game, npc, settlement,
						f"sold {product_name}: {product_id}",
					)
					return True

		if skill_id not in npc.skills:
			return False

		known_reactions = npc.memory.known_crafting_reactions
		reactions = [
			reaction
			for reaction in self.crafting_reactions
			if reaction.id in known_reactions
		]

		for reaction in reactions:
			# Each recipe uses one type of hide.
			hide_id, quantity = next(iter(reaction.reagents.items()))
			if not npc.remove_carried_object(hide_id, game, quantity):
				continue

			level = npc.get_skill_lvl(skill_id)
			chance = min(100, max(0, level))
			success = random.randint(1, 100) <= chance
			npc.gain_skill_xp(skill_id)

			if success:
				product_id, amount = next(iter(reaction.products.items()))
				npc.add_carried_object(product_id, game, amount)
				result = f"made {product_name}: {hide_id} -> {product_id}"
			else:
				result = f"{product_name} crafting failed: {hide_id}"

			self.log_offscreen_result(game, npc, settlement, result)
			return True

		if not has_market:
			return False

		market = settlement.sub_economy
		budget = npc.wallet.get_quantity(settlement.currency)

		for reaction in reactions:
			hide_id, quantity = next(iter(reaction.reagents.items()))
			if not market.has_item(hide_id, quantity):
				continue

			if market.get_value(hide_id) * quantity > budget:
				continue

			if game.buy_item(npc, settlement, hide_id, quantity):
				self.log_offscreen_result(
					game, npc, settlement, f"bought hide: {hide_id}",
				)
				return True

		return False		
		
	def buy_offscreen_ingredient(self, game, npc, settlement, reactions, *, label):
		market = settlement.sub_economy
		budget = npc.wallet.get_quantity(settlement.currency)
		candidates = []

		for reaction in reactions:
			missing = {}
			for item_id, quantity in reaction.reagents.items():
				shortage = quantity - npc.get_unequipped_quantity(item_id)
				if shortage > 0:
					missing[item_id] = shortage

			if not missing or not all(
				market.has_item(item_id, quantity)
				for item_id, quantity in missing.items()
			):
				continue

			cost = sum(
				market.get_value(item_id) * quantity
				for item_id, quantity in missing.items()
			)
			if cost <= budget:
				candidates.append((cost, missing))

		if not candidates:
			return None

		_, missing = min(candidates, key=lambda candidate: candidate[0])
		item_id, quantity = next(iter(missing.items()))

		if not game.buy_item(npc, settlement, item_id, quantity):
			return None

		return f"bought {label}: {quantity} {item_id}"	
		
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
		
	def attempt_hunt(self, game, character, settlement, corpse_ids):
		fauna = settlement.region.resources["fauna"]
		hunting_level = character.get_skill_lvl("hunting")
		hunting_chance = min(100, max(0, (fauna + hunting_level) / 2))

		corpse_id = None

		if random.uniform(0, 100) < hunting_chance:
			item_id = random.choice(corpse_ids)
			if character.add_carried_object(item_id, game, quantity=1):
				corpse_id = item_id

		character.gain_skill_xp("hunting")
		return corpse_id

	def run_offscreen_ai(self, game, npc, settlement):
		for item_id, item_type in game.item_type_objs.items():
			if item_id != "animal_corpse" and item_type.type_id != "animal_corpse":
				continue

			if not npc.inventory.has_item(item_id):
				continue

			if not settlement.has_building("market_building"):
				return False

			if not game.sell_item(npc, settlement, item_id):
				return False

			result = f"sold carcass: {item_id}"
			break
		else:
			corpse_ids = game.get_local_corpse_ids(settlement)
			if not corpse_ids:
				return False

			corpse_id = self.attempt_hunt(game, npc, settlement, corpse_ids)
			result = f"hunted: {corpse_id}" if corpse_id else "hunt unsuccessful"

		self.log_offscreen_result(game, npc, settlement, result)
		
		return True
		
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
				and isinstance(game.item_type_objs.get(item_id), items.Map)
			),
			None,
		)

		missing_supplies = []

		if not character.inventory.has_item("ink"):
			missing_supplies.append(["ink"])

		parchment_ids = [
			item_id
			for item_id, item_type in game.item_type_objs.items()
			if item_id == "parchment"
			or getattr(item_type, "type_id", None) == "parchment"
		]

		if not any(
			character.inventory.has_item(item_id)
			for item_id in parchment_ids
		):
			missing_supplies.append(parchment_ids)

		if map_id is not None or missing_supplies:
			shops = town_map.get_buildings(is_shop=True)

			if not shops:
				character.actions.append(("idle", None))
				return

			shop = random.choice(shops)

			if map_id is not None:
				character.actions.extend([
					("travel", shop),
					("sell", (shop, map_id)),
				])
				return

			settlement = town_map.settlement
			market = settlement.sub_economy
			budget = character.wallet.get_quantity(settlement.currency)
			purchases = []

			for candidates in missing_supplies:
				affordable = [
					item_id
					for item_id in candidates
					if market.has_item(item_id, 1)
					and market.get_value(item_id) <= budget
				]

				if not affordable:
					character.actions.append(("idle", None))
					return

				item_id = min(affordable, key=market.get_value)
				budget -= market.get_value(item_id)
				purchases.append(("buy_material", (shop, item_id, 1)))

			character.actions.append(("travel", shop))
			character.actions.extend(purchases)
			return

		locations = game.get_known_locations(character)

		if not locations:
			character.actions.append(("idle", None))
			return

		location = random.choice(locations)
		character.actions.append(("make_map", location))		
				
				
	def get_parchment_ids(self, game):
		return [
			item_id
			for item_id, item_type in game.item_type_objs.items()
			if item_id == "parchment"
			or getattr(item_type, "type_id", None) == "parchment"
		]
		
	def run_offscreen_ai(self, game, npc, settlement):
		map_id = next(
			(
				item_id
				for item_id, quantity in npc.inventory.get_items()
				if quantity > 0
				and isinstance(game.item_type_objs.get(item_id), items.Map)
			),
			None,
		)

		if map_id is not None:
			if not settlement.has_building("market_building"):
				return False

			if not game.sell_item(npc, settlement, map_id):
				return False

			result = f"sold map: {map_id}"

		else:
			locations = game.get_known_locations(npc)
			if not locations:
				return False

			parchment_id = game.find_carried_parchment(npc)

			if not npc.inventory.has_item("ink"):
				result = self.buy_offscreen_supply(
					game, npc, settlement, ["ink"],
				)
			elif parchment_id is None:
				result = self.buy_offscreen_supply(
					game, npc, settlement, self.get_parchment_ids(game),
				)
			else:
				location = random.choice(locations)

				npc.remove_carried_object("ink", game, quantity=1)
				npc.remove_carried_object(parchment_id, game, quantity=1)

				map_item = game.create_map(
					location=location,
					creator=npc.full_name.strip() or "None",
					cartography_lvl=npc.get_skill_lvl("cartography"),
				)

				npc.add_carried_object(map_item.id, game, quantity=1)
				npc.gain_skill_xp("cartography")
				result = f"made map of {location.name}: {map_item.id}"

		if result is None:
			return False

		self.log_offscreen_result(game, npc, settlement, result)

		return True

	def buy_offscreen_supply(self, game, npc, settlement, candidates):
		if not settlement.has_building("market_building"):
			return None

		market = settlement.sub_economy
		budget = npc.wallet.get_quantity(settlement.currency)
		affordable = [
			item_id
			for item_id in candidates
			if market.has_item(item_id, 1)
			and market.get_value(item_id) <= budget
		]

		if not affordable:
			return None

		item_id = min(affordable, key=market.get_value)
		if game.buy_item(npc, settlement, item_id):
			return f"bought supply: {item_id}"

		return None	
		
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
		
	def run_offscreen_ai(self, game, npc, settlement):
		has_market = settlement.has_building("market_building")
		result = None

		if has_market:
			for item_id, quantity in npc.inventory.get_items():
				if quantity <= 0:
					continue

				item_type = game.item_type_objs.get(item_id)
				if (
					item_id not in self.outputs
					and getattr(item_type, "type_id", None) not in self.outputs
				):
					continue

				if game.sell_item(npc, settlement, item_id):
					result = f"sold butcher product: {item_id}"
					break

		if result is None:
			for reaction in self.crafting_reactions:
				if reaction.id not in npc.memory.known_crafting_reactions:
					continue

				if reaction.skill not in npc.skills:
					continue

				# Each butcher recipe uses a single corpse type.
				corpse_id, quantity = next(iter(reaction.reagents.items()))
				if not npc.remove_carried_object(corpse_id, game, quantity):
					continue

				level = npc.get_skill_lvl(reaction.skill)
				chance = min(100, max(0, level))
				success = random.randint(1, 100) <= chance
				npc.gain_skill_xp(reaction.skill)

				if success:
					for item_id, amount in reaction.products.items():
						if amount > 0:
							npc.add_carried_object(item_id, game, amount)
					result = f"butchered carcass: {corpse_id}"
				else:
					result = f"butchering failed: {corpse_id}"

				break

		if result is None and has_market:
			market = settlement.sub_economy
			budget = npc.wallet.get_quantity(settlement.currency)

			for reaction in self.crafting_reactions:
				if reaction.id not in npc.memory.known_crafting_reactions:
					continue

				if reaction.skill not in npc.skills:
					continue

				corpse_id, quantity = next(iter(reaction.reagents.items()))
				if (
					market.has_item(corpse_id, quantity)
					and market.get_value(corpse_id) * quantity <= budget
					and game.buy_item(npc, settlement, corpse_id, quantity)
				):
					result = f"bought carcass: {corpse_id}"
					break

		if result is None:
			return False

		self.log_offscreen_result(game, npc, settlement, result)

		return True
		
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
		
	def run_offscreen_ai(self, game, npc, settlement):
		reactions = [
			reaction
			for reaction in npc.memory.known_crafting_reactions.values()
			if reaction.skill == "brewing"
		]
		if not reactions or "brewing" not in npc.skills:
			return False

		has_market = settlement.has_building("market_building")
		wine_ids = {
			item_id
			for reaction in game.wine_reaction_objs.values()
			for item_id in reaction.products
		}
		wine_id = next(
			(
				item_id
				for item_id, quantity in npc.inventory.get_items()
				if quantity > 0 and item_id in wine_ids
			),
			None,
		)

		if wine_id is not None:
			if not has_market or not game.sell_item(npc, settlement, wine_id):
				return False

			self.log_offscreen_result(
				game, npc, settlement, f"sold wine: {wine_id}",
			)
			return True

		ready_reactions = [
			reaction
			for reaction in reactions
			if all(
				npc.get_unequipped_quantity(item_id) >= quantity
				for item_id, quantity in reaction.reagents.items()
			)
		]

		if not ready_reactions:
			if not has_market:
				return False

			result = self.buy_offscreen_ingredient(
				game, npc, settlement, reactions,
				label="brewing ingredient",
			)
			if result is None:
				return False

			self.log_offscreen_result(game, npc, settlement, result)
			return True

		reaction = random.choice(ready_reactions)
		for item_id, quantity in reaction.reagents.items():
			npc.remove_carried_object(item_id, game, quantity)

		chance = min(100, max(0, npc.get_skill_lvl("brewing")))
		success = random.randint(1, 100) <= chance
		npc.gain_skill_xp("brewing")

		if success:
			for item_id, quantity in reaction.products.items():
				if quantity > 0:
					npc.add_carried_object(item_id, game, quantity)
			result = f"brewed wine: {', '.join(reaction.products)}"
		else:
			result = f"brewing failed: {reaction.id}"

		self.log_offscreen_result(game, npc, settlement, result)
		return True
		
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
		
	def run_offscreen_ai(self, game, npc, settlement):
		has_market = settlement.has_building("market_building")

		if npc.inventory.has_item("ink"):
			if not has_market or not game.sell_item(npc, settlement, "ink"):
				return False

			result = "sold ink"

		else:
			reaction = npc.memory.known_crafting_reactions.get("make_ink")
			if reaction is None or reaction.skill not in npc.skills:
				return False

			coal_needed = reaction.reagents["coal"]
			coal_missing = coal_needed - npc.get_unequipped_quantity("coal")

			if coal_missing > 0:
				if not has_market:
					return False

				if not game.buy_item(npc, settlement, "coal", coal_missing):
					return False

				result = f"bought coal: {coal_missing}"

			else:
				if not npc.remove_carried_object("coal", game, coal_needed):
					return False

				level = npc.get_skill_lvl(reaction.skill)
				chance = min(100, max(0, level))
				success = random.randint(1, 100) <= chance
				npc.gain_skill_xp(reaction.skill)

				if success:
					ink_quantity = reaction.products["ink"]
					npc.add_carried_object("ink", game, ink_quantity)
					result = f"made ink: {ink_quantity}"
				else:
					result = "ink making failed"

		self.log_offscreen_result(game, npc, settlement, result)
		return True	
		
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
		
	def run_offscreen_ai(self, game, npc, settlement):
		return self.run_offscreen_hide_crafting(
			game, npc, settlement,
			skill_id="tanning",
			product_name="leather",
		)
		
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
		
	def run_offscreen_ai(self, game, npc, settlement):
		if npc.inventory.has_item("wood"):
			if not settlement.has_building("market_building"):
				return False

			if not game.sell_item(npc, settlement, "wood"):
				return False

			result = "sold wood"

		else:
			trees = settlement.resources["trees"]
			if trees <= 0:
				return False

			level = npc.get_skill_lvl("wood_cutting")
			chance = min(100, max(0, (trees + level) / 2))

			success = random.uniform(0, 100) < chance
			if success:
				success = npc.add_carried_object("wood", game, quantity=1)

			npc.gain_skill_xp("wood_cutting")
			result = "harvested wood" if success else "woodcutting failed"

		self.log_offscreen_result(game, npc, settlement, result)
		return True	
		
class PaperMaker(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "paper_maker"
		
		self.name = "Paper Maker"
		
		self.outputs = [
			"parchment"
		]
		
		self.starting_skills = [
			"paper_making",
		]
		
		self.starting_items = {
			"animal_hide": 5,
		}
		
		self.reactions_based_on_skill = True
		
	def add_work_ai(self, game, character, town_map):
		shops = town_map.get_buildings(is_shop=True)
		shop = random.choice(shops) if shops else None

		if shop is not None:
			for reaction in self.crafting_reactions:
				paper_id = next(iter(reaction.products))
				if character.inventory.has_item(paper_id):
					character.actions.extend([
						("travel", shop),
						("sell", (shop, paper_id)),
					])
					return

		known_reactions = character.memory.known_crafting_reactions
		reactions = [
			reaction
			for reaction in self.crafting_reactions
			if reaction.id in known_reactions
		]

		for reaction in reactions:
			hide_id = next(iter(reaction.reagents))
			if character.inventory.has_item(hide_id):
				character.actions.append(("craft", reaction.id))
				return

		if shop is not None:
			settlement = town_map.settlement
			market = settlement.sub_economy
			budget = character.wallet.get_quantity(settlement.currency)

			for reaction in reactions:
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
		
	def run_offscreen_ai(self, game, npc, settlement):
		return self.run_offscreen_hide_crafting(
			game, npc, settlement,
			skill_id="paper_making",
			product_name="parchment",
		)	
		
class WoodBurner(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "wood_burner"
		
		self.name = "Wood Burner"
		
		self.outputs = [
			"coal"
		]
		
		self.starting_skills = [
			"wood_burning",
		]
		
		self.starting_items = {
			"wood": 5,
		}
		
	def add_work_ai(self, game, character, town_map):
		shops = town_map.get_buildings(is_shop=True)

		if character.inventory.has_item("coal") and shops:
			shop = random.choice(shops)
			character.actions.extend([
				("travel", shop),
				("sell", (shop, "coal")),
			])
			return

		reaction = character.memory.known_crafting_reactions.get("make_coal")
		if reaction is None:
			character.actions.append(("idle", None))
			return

		if character.inventory.has_item("wood", 1):
			character.actions.append(("craft", reaction.id))
			return

		settlement = town_map.settlement
		market = settlement.sub_economy
		budget = character.wallet.get_quantity(settlement.currency)

		if (
			shops
			and market.has_item("wood", 1)
			and market.get_value("wood") <= budget
		):
			shop = random.choice(shops)
			character.actions.extend([
				("travel", shop),
				("buy_material", (shop, "wood", 1)),
			])
			return

		character.actions.append(("idle", None))
		
	def run_offscreen_ai(self, game, npc, settlement):
		has_market = settlement.has_building("market_building")

		if has_market and npc.inventory.has_item("coal"):
			if not game.sell_item(npc, settlement, "coal"):
				return False

			result = "sold coal"

		else:
			reaction = npc.memory.known_crafting_reactions.get("make_coal")
			if reaction is None or reaction.skill not in npc.skills:
				return False

			wood_needed = reaction.reagents["wood"]
			wood_missing = wood_needed - npc.get_unequipped_quantity("wood")

			if wood_missing > 0:
				if not has_market:
					return False

				if not game.buy_item(npc, settlement, "wood", wood_missing):
					return False

				result = f"bought wood: {wood_missing}"

			else:
				if not npc.remove_carried_object("wood", game, wood_needed):
					return False

				level = npc.get_skill_lvl(reaction.skill)
				chance = min(100, max(0, level))
				success = random.randint(1, 100) <= chance
				npc.gain_skill_xp(reaction.skill)

				if success:
					coal_quantity = reaction.products["coal"]
					npc.add_carried_object("coal", game, coal_quantity)
					result = f"made coal: {coal_quantity}"
				else:
					result = "wood burning failed"

		self.log_offscreen_result(game, npc, settlement, result)
		return True	
		
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
		
	def run_offscreen_ai(self, game, npc, settlement):
		has_market = settlement.has_building("market_building")
		ore_id = npc.find_inventory_item(game, game.ore_objs)

		if ore_id is not None:
			if not has_market or not game.sell_item(npc, settlement, ore_id):
				return False

			result = f"sold ore: {ore_id}"

		else:
			pickaxe_id = npc.find_inventory_item(game, game.pickaxe_objs)

			if pickaxe_id is None:
				if not has_market:
					return False

				market = settlement.sub_economy
				budget = npc.wallet.get_quantity(settlement.currency)
				candidates = []

				for item_id, quantity in market.inventory.items():
					if quantity <= 0:
						continue

					item = game.item_type_objs.get(item_id)
					if getattr(item, "type_id", None) != "pickaxe":
						continue

					if getattr(item, "durability", 1) <= 0:
						continue

					if market.get_value(item_id) <= budget:
						candidates.append(item_id)

				if not candidates:
					return False

				pickaxe_id = random.choice(candidates)
				if not game.buy_item(npc, settlement, pickaxe_id):
					return False

				result = f"bought pickaxe: {pickaxe_id}"

			else:
				if not game.ore_objs or not settlement.has_building("mine_building"):
					return False

				if npc.ensure_equipped(game, game.pickaxe_objs) is None:
					return False

				if game.mine(npc, settlement):
					ore_id = npc.find_inventory_item(game, game.ore_objs)
					result = f"mined ore: {ore_id}"
				else:
					result = "mining failed"

		self.log_offscreen_result(game, npc, settlement, result)
		return True
		
class Smelter(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "smelter"
		
		self.name = "Smelter"
		
		self.outputs = []
		
		self.starting_skills = [
			"smelting",
		]
		
		self.reactions_based_on_skill = True
		
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
						
	def add_work_ai(self, game, character, town_map):
		shops = town_map.get_buildings(is_shop=True)
		shop = random.choice(shops) if shops else None

		if shop is not None:
			for bar_id in game.bar_objs:
				if character.inventory.has_item(bar_id, 1):
					character.actions.extend([
						("travel", shop),
						("sell", (shop, bar_id)),
					])
					return

		known_reactions = character.memory.known_crafting_reactions
		reactions = [
			reaction
			for reaction in self.crafting_reactions
			if reaction.id in known_reactions
		]

		for reaction in reactions:
			if all(
				character.inventory.has_item(item_id, quantity)
				for item_id, quantity in reaction.reagents.items()
			):
				character.actions.append(("craft", reaction.id))
				return

		if shop is not None:
			settlement = town_map.settlement
			market = settlement.sub_economy
			budget = character.wallet.get_quantity(settlement.currency)

			for reaction in reactions:
				missing = {}
				for item_id, quantity in reaction.reagents.items():
					shortfall = quantity - character.inventory.get_quantity(item_id)
					if shortfall > 0:
						missing[item_id] = shortfall

				if not all(
					market.has_item(item_id, quantity)
					for item_id, quantity in missing.items()
				):
					continue

				cost = sum(
					market.get_value(item_id) * quantity
					for item_id, quantity in missing.items()
				)
				if cost > budget:
					continue

				character.actions.append(("travel", shop))
				character.actions.extend(
					("buy_material", (shop, item_id, quantity))
					for item_id, quantity in missing.items()
				)
				return

		character.actions.append(("idle", None))
		
	def give_starting_items(self, game, character):
		super().give_starting_items(game, character)

		known_reactions = character.memory.known_crafting_reactions
		smelting_reactions = [
			reaction
			for reaction in self.crafting_reactions
			if reaction.id in known_reactions
		]

		if not smelting_reactions:
			return

		reaction = random.choice(smelting_reactions)
		for item_id, quantity in reaction.reagents.items():
			character.add_carried_object(
				item_id,
				game,
				quantity=quantity * 5,
			)
		
	def run_offscreen_ai(self, game, npc, settlement):
		has_market = settlement.has_building("market_building")
		bar_id = npc.find_inventory_item(game, game.bar_objs)

		if has_market and bar_id is not None:
			if not game.sell_item(npc, settlement, bar_id):
				return False

			self.log_offscreen_result(
				game, npc, settlement, f"sold bar: {bar_id}",
			)
			return True

		if "smelting" not in npc.skills:
			return False

		known_reactions = npc.memory.known_crafting_reactions
		reactions = [
			reaction
			for reaction in self.crafting_reactions
			if reaction.id in known_reactions
		]

		for reaction in reactions:
			if not all(
				npc.get_unequipped_quantity(item_id) >= quantity
				for item_id, quantity in reaction.reagents.items()
			):
				continue

			for item_id, quantity in reaction.reagents.items():
				npc.remove_carried_object(item_id, game, quantity)

			level = npc.get_skill_lvl("smelting")
			chance = min(100, max(0, level))
			success = random.randint(1, 100) <= chance
			npc.gain_skill_xp("smelting")

			if success:
				bar_id, quantity = next(iter(reaction.products.items()))
				npc.add_carried_object(bar_id, game, quantity)
				result = f"smelted bar: {bar_id}"
			else:
				result = f"smelting failed: {reaction.id}"

			self.log_offscreen_result(game, npc, settlement, result)
			return True

		if not has_market:
			return False

		result = self.buy_offscreen_ingredient(
			game, npc, settlement, reactions, label="smelting reagent",
		)
		if result is None:
			return False

		self.log_offscreen_result(game, npc, settlement, result)
		return True	
		
class Coinsmith(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "coinsmith"
		
		self.name = "Coinsmith"
		
		self.starting_skills = [
			"coinsmithing",
		]
		
		self.reactions_based_on_skill = True
		
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
					
	def give_starting_items(self, game, character):
		super().give_starting_items(game, character)

		reactions = [
			reaction
			for reaction in character.memory.known_crafting_reactions.values()
			if reaction.skill == "coinsmithing"
		]

		if not reactions:
			return

		reaction = random.choice(reactions)
		for item_id, quantity in reaction.reagents.items():
			character.add_carried_object(item_id, game, quantity=quantity * 5)

	def add_work_ai(self, game, character, town_map):
		reactions = [
			reaction
			for reaction in character.memory.known_crafting_reactions.values()
			if reaction.skill == "coinsmithing"
		]
		recipes_to_restock = []

		for reaction in reactions:
			missing = {}
			for item_id, quantity in reaction.reagents.items():
				shortfall = quantity - character.inventory.get_quantity(item_id)
				if shortfall > 0:
					missing[item_id] = shortfall

			if not missing:
				character.actions.append(("craft", reaction.id))
				return

			recipes_to_restock.append(missing)

		shops = town_map.get_buildings(is_shop=True)
		if shops:
			settlement = town_map.settlement
			market = settlement.sub_economy
			budget = character.wallet.get_quantity(settlement.currency)

			for missing in recipes_to_restock:
				if not all(
					market.has_item(item_id, quantity)
					for item_id, quantity in missing.items()
				):
					continue

				cost = sum(
					market.get_value(item_id) * quantity
					for item_id, quantity in missing.items()
				)
				if cost > budget:
					continue

				shop = random.choice(shops)
				character.actions.append(("travel", shop))
				character.actions.extend(
					("buy_material", (shop, item_id, quantity))
					for item_id, quantity in missing.items()
				)
				return

		character.actions.append(("idle", None))				
		
	def run_offscreen_ai(self, game, npc, settlement):
		if "coinsmithing" not in npc.skills:
			return False

		reactions = [
			reaction
			for reaction in npc.memory.known_crafting_reactions.values()
			if reaction.skill == "coinsmithing"
		]

		for reaction in reactions:
			if not all(
				npc.get_unequipped_quantity(item_id) >= quantity
				for item_id, quantity in reaction.reagents.items()
			):
				continue

			for item_id, quantity in reaction.reagents.items():
				npc.remove_carried_object(item_id, game, quantity)

			level = npc.get_skill_lvl("coinsmithing")
			chance = min(100, max(0, level))
			success = random.randint(1, 100) <= chance
			npc.gain_skill_xp("coinsmithing")

			if success:
				coin_id, quantity = next(iter(reaction.products.items()))
				npc.add_carried_object(coin_id, game, quantity)
				result = f"minted coin: {quantity} {coin_id}"
			else:
				result = f"coinsmithing failed: {reaction.id}"

			self.log_offscreen_result(game, npc, settlement, result)
			return True

		if not settlement.has_building("market_building"):
			return False

		result = self.buy_offscreen_ingredient(
			game, npc, settlement, reactions,
			label="coinsmithing reagent",
		)
		if result is None:
			return False

		self.log_offscreen_result(game, npc, settlement, result)
		return True
		
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
		
	def add_work_ai(self, game, character, town_map):
		if character.inventory.has_item("water", 1):
			shops = town_map.get_buildings(is_shop=True)
			if shops:
				shop = random.choice(shops)
				character.actions.extend([
					("travel", shop),
					("sell", (shop, "water")),
				])
			else:
				character.actions.append(("idle", None))
			return

		if town_map.settlement.resources["water"] > 0:
			character.actions.append(("collect_water", None))
		else:
			character.actions.append(("idle", None))
		
	def run_offscreen_ai(self, game, npc, settlement):
		if npc.inventory.has_item("water"):
			if not settlement.has_building("market_building"):
				return False

			if not game.sell_item(npc, settlement, "water"):
				return False

			result = "sold water"

		else:
			water = settlement.resources["water"]
			if water <= 0:
				return False

			success = random.randint(1, 100) <= water
			if success:
				success = npc.add_carried_object("water", game, quantity=1)

			result = "collected water" if success else "water collection failed"

		self.log_offscreen_result(game, npc, settlement, result)
		return True	
		
class Forager(Profession):
	def __init__(self):
		super().__init__()

		self.id = "forager"
		
		self.name = "Forager"
		
		self.outputs = [
			"fruit"
		]
		
		self.can_craft = False
		
		self.starting_skills = [
			"foraging"
		]

	def get_local_fruit_ids(self, settlement, game):
		biome_id = settlement.region.biome.id

		return [
			fruit_id
			for fruit_id, fruit in game.fruit_objs.items()
			if fruit.can_forage and biome_id in fruit.biomes
		]

	def produce(self, settlement, game):
		fruit_ids = self.get_local_fruit_ids(settlement, game)
		if not fruit_ids:
			return

		flora = settlement.resources["flora"]
		foragers = settlement.get_active_workers(self)

		for _ in range(foragers):
			if random.randint(1, 100) <= flora:
				fruit_id = random.choice(fruit_ids)
				settlement.sub_economy.add_item(fruit_id, quantity=1)

	def add_work_ai(self, game, character, town_map):
		for item_id, quantity in character.inventory.get_items():
			fruit = game.fruit_objs.get(item_id)
			if quantity <= 0 or fruit is None or not fruit.can_forage:
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

		if self.get_local_fruit_ids(town_map.settlement, game):
			character.actions.append(("forage", None))
		else:
			character.actions.append(("idle", None))
			
	def run_offscreen_ai(self, game, npc, settlement):
		for item_id, quantity in npc.inventory.get_items():
			fruit = game.fruit_objs.get(item_id)
			if quantity <= 0 or fruit is None or not fruit.can_forage:
				continue

			if not settlement.has_building("market_building"):
				return False

			if not game.sell_item(npc, settlement, item_id):
				return False

			self.log_offscreen_result(
				game, npc, settlement, f"sold fruit: {item_id}",
			)
			return True

		fruit_ids = self.get_local_fruit_ids(settlement, game)
		if not fruit_ids:
			return False

		flora = settlement.resources["flora"]
		if flora <= 0:
			return False

		result = "foraging failed"
		if random.randint(1, 100) <= flora:
			fruit_id = random.choice(fruit_ids)
			if npc.add_carried_object(fruit_id, game, quantity=1):
				result = f"foraged fruit: {fruit_id}"

		self.log_offscreen_result(game, npc, settlement, result)
		return True
	
class Blacksmith(Profession):
	def __init__(self):
		super().__init__()

		self.id = "blacksmith"
		
		self.name = "Blacksmith"
		
		self.starting_skills = [
			"blacksmithing"
		]
		
		self.reactions_based_on_skill = True

	def get_known_recipes(self, character):
		return [
			reaction
			for reaction in character.memory.known_crafting_reactions.values()
			if reaction.skill == "blacksmithing"
		]

	def give_starting_items(self, game, character):
		super().give_starting_items(game, character)

		reactions = self.get_known_recipes(character)
		if reactions:
			reaction = random.choice(reactions)
			for item_id, quantity in reaction.reagents.items():
				character.add_carried_object(item_id, game, quantity=quantity * 5)

	def add_work_ai(self, game, character, town_map):
		shops = town_map.get_buildings(is_shop=True)
		shop = random.choice(shops) if shops else None
		pickaxe_id = character.find_inventory_item(game, game.pickaxe_objs)

		if shop is not None and pickaxe_id is not None:
			character.actions.extend([
				("travel", shop),
				("sell", (shop, pickaxe_id)),
			])
			return

		missing_by_recipe = []

		for reaction in self.get_known_recipes(character):
			missing = {}
			for item_id, quantity in reaction.reagents.items():
				shortfall = quantity - character.inventory.get_quantity(item_id)
				if shortfall > 0:
					missing[item_id] = shortfall

			if not missing:
				character.actions.append(("craft", reaction.id))
				return

			missing_by_recipe.append(missing)

		if shop is not None:
			settlement = town_map.settlement
			market = settlement.sub_economy
			budget = character.wallet.get_quantity(settlement.currency)

			for missing in missing_by_recipe:
				if not all(
					market.has_item(item_id, quantity)
					for item_id, quantity in missing.items()
				):
					continue

				cost = sum(
					market.get_value(item_id) * quantity
					for item_id, quantity in missing.items()
				)
				if cost > budget:
					continue

				character.actions.append(("travel", shop))
				character.actions.extend(
					("buy_material", (shop, item_id, quantity))
					for item_id, quantity in missing.items()
				)
				return

		character.actions.append(("idle", None))
	
	def run_offscreen_ai(self, game, npc, settlement):
		has_market = settlement.has_building("market_building")

		if has_market:
			pickaxe_id = npc.find_inventory_item(game, game.pickaxe_objs)
			if pickaxe_id is not None:
				if not game.sell_item(npc, settlement, pickaxe_id):
					return False

				self.log_offscreen_result(
					game, npc, settlement, f"sold pickaxe: {pickaxe_id}",
				)
				return True

		if "blacksmithing" not in npc.skills:
			return False

		reactions = self.get_known_recipes(npc)

		for reaction in reactions:
			if not all(
				npc.get_unequipped_quantity(item_id) >= quantity
				for item_id, quantity in reaction.reagents.items()
			):
				continue

			for item_id, quantity in reaction.reagents.items():
				npc.remove_carried_object(item_id, game, quantity)

			level = npc.get_skill_lvl("blacksmithing")
			chance = min(100, max(0, level))
			success = random.randint(1, 100) <= chance
			npc.gain_skill_xp("blacksmithing")

			if success:
				for item_id, quantity in reaction.products.items():
					if quantity > 0:
						npc.add_carried_object(item_id, game, quantity)
				result = f"forged: {', '.join(reaction.products)}"
			else:
				result = f"blacksmithing failed: {reaction.id}"

			self.log_offscreen_result(game, npc, settlement, result)
			return True

		if not has_market:
			return False

		result = self.buy_offscreen_ingredient(
			game, npc, settlement, reactions,
			label="blacksmithing reagent",
		)
		if result is None:
			return False

		self.log_offscreen_result(game, npc, settlement, result)
		return True
	
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
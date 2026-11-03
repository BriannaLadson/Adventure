import random

import aidebug

def start_ai(game, town_map):
	debug = aidebug.start_turn(game, town_map)

	for npc in town_map.settlement.npcs or []:
		if not npc.alive:
			continue

		work_ai(game, npc, town_map)

		if not npc.actions:
			choose_goal(game, npc, town_map)

		aidebug.run_action(debug, game, npc, town_map, do_ai)
		
	aidebug.finish_turn(debug)
		
def work_ai(game, npc, town_map):
	is_work_time = (
		npc.profession is not None
		and npc.work_shift.is_active(game.calendar)
	)

	if not is_work_time:
		npc.actions.clear()
		npc.current_activity = None
		return

	if not npc.actions:
		npc.profession.add_work_ai(game, npc, town_map)
	
		
def choose_goal(game, npc, town_map):
	if npc.actions:
		return
		
	available_goals = [
		goal for goal in ai_goals
		if goal.can_start(game, npc, town_map)
	]
	
	if available_goals:
		goal = random.choice(available_goals)
		goal.add_actions(game, npc, town_map)
		
def do_ai(game, npc, town_map):
	if not npc.actions:
		return

	action_id, target = npc.actions[0]
	action = action_dict[action_id]

	result = action(game, npc, town_map, target)

	if result is None:
		npc.actions.clear()
		npc.current_activity = None

	elif result:
		npc.actions.pop(0)
		npc.current_activity = None
		
class Wander:
	def can_start(self, game, npc, town_map):
		return True

	def add_actions(self, game, npc, town_map):
		dx, dy = random.choice([
			(-1, -1), (0, -1), (1, -1),
			(-1, 0), (1, 0),
			(-1, 1), (0, 1), (1, 1)
		])

		target = (npc.lx + dx, npc.ly + dy)

		npc.actions.append(("move", target))


class Idle:
	def can_start(self, game, npc, town_map):
		return True

	def add_actions(self, game, npc, town_map):
		npc.actions.append(("idle", None))
		
def move(game, npc, town_map, target):
	tx, ty = target

	if not (0 <= tx < town_map.map_size and 0 <= ty < town_map.map_size):
		return True

	if not town_map.is_walkable(tx, ty):
		return True

	player = game.player

	if (
		(player.gx, player.gy) == (npc.gx, npc.gy)
		and (player.lx, player.ly) == target
	):
		return True

	for other in town_map.settlement.npcs or []:
		if other is not npc and (other.lx, other.ly) == target:
			return True

	npc.lx = tx
	npc.ly = ty

	return True


def idle(game, npc, town_map, target):
	return True
	
def travel(game, character, town_map, building):
	goals = town_map.get_building_positions(building)
	
	if not goals:
		return None
		
	blocked = {
		(other.lx, other.ly)
		for other in town_map.settlement.npcs or []
		if other is not character
	}
	
	blocked.difference_update(
		tuple(building.door)
		for building in town_map.buildings
	)
		
	player = game.player

	if(
		player is not character
		and (player.gx, player.gy) == (character.gx, character.gy)
	):
		blocked.add((player.lx, player.ly))
		
	path = town_map.find_path(
		start = (character.lx, character.ly),
		goals = goals,
		blocked = blocked,
	)
	
	if path is None:
		return False
		
	if not path:
		return True
		
	character.lx, character.ly = path[0]
	
	return (character.lx, character.ly) in goals
	
def mine(game, character, town_map, target):
	if not game.ore_objs:
		return None

	if character.ensure_equipped(game, game.pickaxe_objs) is None:
		return None

	mines = town_map.get_buildings(
		building_type="mine_building",
	)

	at_mine = any(
		(character.lx, character.ly)
		in town_map.get_building_positions(building)
		for building in mines
	)

	if not at_mine:
		return None

	hour = (
		game.calendar.date_string(),
		game.calendar.hour,
		game.calendar.is_pm,
	)

	if character.current_activity is None:
		character.current_activity = {
			"id": "mining",
			"started": hour,
		}

		return False

	if character.current_activity["started"] == hour:
		return False

	success = game.mine(character, town_map.settlement)

	if success:
		return True

	character.current_activity["started"] = hour

	return False
	
def sell(game, character, town_map, target):
	shop, item_id = target

	if not shop.building_type.is_shop:
		return None

	positions = town_map.get_building_positions(shop)

	if (character.lx, character.ly) not in positions:
		return None

	success = game.sell_item(
		character,
		shop.settlement,
		item_id,
	)

	if not success:
		return None

	return True
	
def buy(game, character, town_map, target):
	shop, item_type_id = target

	if not shop.building_type.is_shop:
		return None

	positions = town_map.get_building_positions(shop)

	if (character.lx, character.ly) not in positions:
		return None

	settlement = shop.settlement
	sub_economy = settlement.sub_economy

	currency_quantity = character.wallet.get_quantity(
		settlement.currency,
	)

	candidates = []

	for item_id, quantity in sub_economy.inventory.items():
		if quantity <= 0:
			continue

		item = game.item_type_objs[item_id]

		if getattr(item, "type_id", None) != item_type_id:
			continue

		if getattr(item, "durability", 1) <= 0:
			continue

		price = sub_economy.get_value(item_id)

		if price <= currency_quantity:
			candidates.append(item_id)

	if candidates:
		item_id = random.choice(candidates)

		game.buy_item(
			character,
			settlement,
			item_id,
		)

	return True
		
		
def hunt(game, character, town_map, target):
	corpse_ids = game.get_local_corpse_ids(town_map.settlement)
	if not corpse_ids:
		return None

	hour = (
		game.calendar.date_string(),
		game.calendar.hour,
		game.calendar.is_pm,
	)

	if character.current_activity is None:
		character.current_activity = {
			"id": "hunting",
			"started": hour,
		}

		return False

	if character.current_activity["started"] == hour:
		return False

	fauna = town_map.settlement.region.resources["fauna"]
	hunting_level = character.get_skill_lvl("hunting")

	hunting_chance = min(
		100,
		max(0, (fauna + hunting_level) / 2),
	)

	success = random.uniform(0, 100) < hunting_chance

	if success:
		success = character.add_carried_object(
			random.choice(corpse_ids),
			game,
			quantity=1,
		)

	character.gain_skill_xp("hunting")

	if success:
		return True

	character.current_activity["started"] = hour

	return False	

def cut_tree(game, character, town_map, target):
	trees = town_map.settlement.resources["trees"]
	if trees <= 0:
		return None

	hour = (
		game.calendar.date_string(),
		game.calendar.hour,
		game.calendar.is_pm,
	)

	if character.current_activity is None:
		character.current_activity = {
			"id": "wood_cutting",
			"started": hour,
		}
		return False

	if character.current_activity["started"] == hour:
		return False

	woodcutting_level = character.get_skill_lvl("wood_cutting")
	chance = min(100, max(0, (trees + woodcutting_level) / 2))

	success = random.uniform(0, 100) < chance
	if success:
		success = character.add_carried_object("wood", game, quantity=1)

	character.gain_skill_xp("wood_cutting")

	if success:
		return True

	character.current_activity["started"] = hour
	return False	
	
def make_map(game, character, town_map, location):
	coordinates = (location.gx, location.gy)

	if character.memory.known_locations.get(coordinates) is not location:
		return None

	reagents = {
		"ink": 1,
		"parchment": 1,
	}

	for item_id, quantity in reagents.items():
		if not character.inventory.has_item(item_id, quantity):
			return None

	hour = (
		game.calendar.date_string(),
		game.calendar.hour,
		game.calendar.is_pm,
	)

	if character.current_activity is None:
		character.current_activity = {
			"id": "mapmaking",
			"started": hour,
		}

		return False

	if character.current_activity["started"] == hour:
		return False

	for item_id, quantity in reagents.items():
		character.remove_carried_object(
			item_id,
			game,
			quantity,
		)

	cartography_level = character.get_skill_lvl("cartography")

	map_item = game.create_map(
		location=location,
		creator=character.full_name.strip() or "None",
		cartography_lvl=cartography_level,
	)

	character.add_carried_object(
		map_item.id,
		game,
		quantity=1,
	)

	character.gain_skill_xp("cartography")

	return True	
	
def butcher(game, character, town_map, target):
	if not character.inventory.has_item("animal_corpse"):
		return None

	hour = (
		game.calendar.date_string(),
		game.calendar.hour,
		game.calendar.is_pm,
	)

	if character.current_activity is None:
		character.current_activity = {
			"id": "butchering",
			"started": hour,
		}

		return False

	if character.current_activity["started"] == hour:
		return False

	if not character.remove_carried_object(
		"animal_corpse",
		game,
		quantity=1,
	):
		return None

	butchering_chance = min(
		100,
		max(0, character.get_skill_lvl("butchering")),
	)

	success = random.randint(1, 100) <= butchering_chance

	if success:
		for item_id in ("animal_hide", "animal_meat"):
			character.add_carried_object(
				item_id,
				game,
				quantity=1,
			)

	character.gain_skill_xp("butchering")

	return True	
	
def buy_material(game, character, town_map, target):
	shop, item_id, quantity = target

	if not shop.building_type.is_shop:
		return None

	positions = town_map.get_building_positions(shop)

	if (character.lx, character.ly) not in positions:
		return None

	success = game.buy_item(
		character,
		shop.settlement,
		item_id,
		quantity=quantity,
	)

	if not success:
		return None

	return True
	
def craft(game, character, town_map, reaction_id):
	if reaction_id not in character.memory.known_crafting_reactions:
		return None

	reaction = game.crafting_reaction_objs.get(reaction_id)

	if reaction is None:
		return None

	if reaction.skill is not None:
		if reaction.skill not in character.skills:
			return None

	for item_id, quantity in reaction.reagents.items():
		if not character.inventory.has_item(item_id, quantity):
			return None

	if character.current_activity is None:
		character.current_activity = {
			"id": "crafting",
			"reaction_id": reaction_id,
			"ticks_remaining": reaction.ticks,
		}

		return False

	character.current_activity["ticks_remaining"] -= 1

	if character.current_activity["ticks_remaining"] > 0:
		return False

	for item_id, quantity in reaction.reagents.items():
		character.remove_carried_object(
			item_id,
			game,
			quantity=quantity,
		)

	success = True

	if reaction.skill is not None:
		skill_level = character.get_skill_lvl(reaction.skill)

		success_chance = min(
			100,
			max(0, skill_level),
		)

		success = random.randint(1, 100) <= success_chance

		character.gain_skill_xp(reaction.skill)

	if success:
		for item_id, quantity in reaction.products.items():
			character.add_carried_object(
				item_id,
				game,
				quantity=quantity,
			)

	return True
	
action_dict = {
	"move": move,
	"idle": idle,
	"travel": travel,
	"mine": mine,
	"sell": sell,
	"buy": buy,
	"hunt": hunt,
	"make_map": make_map,
	"butcher": butcher,
	"buy_material": buy_material,
	"craft": craft,
	"cut_tree": cut_tree,
}


ai_goals = [
	Wander(),
	Idle(),
]

def describe_action(action):
	if action is None:
		return "none"

	action_id, target = action

	if action_id == "travel":
		return f"travel to {target.get_name()}"

	if action_id == "sell":
		shop, item_id = target

		return f"sell {item_id} at {shop.get_name()}"
		
	if action_id == "buy":
		shop, item_type_id = target

		return f"look for {item_type_id} at {shop.get_name()}"

	return action_id

def debug_npc_turn(game, character, position_before, action):
	position_after = (character.lx, character.ly)

	next_action = (
		character.actions[0]
		if character.actions
		else None
	)

	is_work_time = character.work_shift.is_active(game.calendar)

	entry = (
		f"{game.calendar.date_string()} "
		f"{game.calendar.time_string()}\n"
		f"On shift: {is_work_time}\n"
		f"Action: {describe_action(action)}\n"
		f"Position: {position_before} -> {position_after}\n"
		f"Next: {describe_action(next_action)}\n"
		f"Activity: {character.current_activity}\n"
		f"Inventory: {list(character.inventory.get_items())}\n"
		f"Coins: {list(character.wallet.get_coins())}"
	)

	game.debug_history.append(entry)

	# Clear the terminal and return its cursor to the top.
	print("\033[2J\033[H", end="")

	print(
		f"Following: {character.full_name} "
		f"({character.profession_id})"
	)

	print(
		f"Latest {len(game.debug_history)} turns "
		f"(limit: {game.debug_action_limit})"
	)

	for entry in game.debug_history:
		print("\n" + "-" * 60)
		print(entry)

	print(flush=True)
import random

import aidebug
import entities

#Helpers
def should_address_need(npc, need_id):
	current_value = npc.needs[need_id]
	maximum_value = npc.need_definitions[need_id]["max"]

	chance = 1 - (current_value / maximum_value)

	return random.random() < chance

#Start
def start_ai(game, map_generator):
	if not game.player.is_location_local():
		return False
		
	if not isinstance(map_generator, entities.TownMapGenerator):
		return False
		
	start_town_ai(game, map_generator)
	
	return True
	
def start_town_ai(game, town_map):
	settlement = town_map.settlement

	for npc in list(settlement.npcs or []):
		if not npc.alive or not npc.is_location_local():
			continue
			
		leave_town_goal = GOALS["leave_town"]

		handling_need = need_ai(game, npc, town_map)
		
		leaving = (
			not handling_need
			and leave_town_goal.can_start(game, npc, town_map)
		)

		if leaving:
			leave_town_goal.add_actions(game, npc, town_map)
		
		elif not handling_need:
			work_ai(game, npc, town_map)
			
			if not npc.actions:
				choose_goal(game, npc, town_map)

		action_id = npc.actions[0][0] if npc.actions else "none"
		position_before = (npc.lx, npc.ly)

		do_ai(game, npc, town_map)

		if game.debug_enabled:
			aidebug.write_log(
				game,
				"town_debug_log",
				f"{game.calendar.date_string()} {game.calendar.time_string()} | "
				f"{settlement.name} | {npc.full_name} | "
				f"action: {action_id} | "
				f"position: {position_before} -> {(npc.lx, npc.ly)} | "
				f"days until departure: {getattr(npc, 'days_until_departure', None)}",
			)

		if leaving and (npc.lx, npc.ly) == npc.tile_target:
			move_npc_to_overworld(game, npc, settlement)
			
			continue

		if not npc.actions:
			npc.handling_need = False
	
def move_npc_to_overworld(game, npc, settlement):
	if not hasattr(game, "overworld_npcs"):
		game.overworld_npcs = []

	settlement.npcs.remove(npc)
	
	if npc in game.entities:
		game.entities.remove(npc)

	npc.previous_settlement_coords = (settlement.gx, settlement.gy)
	npc.settlement = None
	npc.gx, npc.gy = settlement.gx, settlement.gy
	npc.lx = npc.ly = npc.lz = None
	npc.tile_target = None
	npc.actions.clear()
	npc.current_activity = None
	npc.handling_need = False

	game.overworld_npcs.append(npc)
	
	if game.debug_enabled:
		aidebug.write_log(
			game,
			"overworld_debug_log",
			f"{game.calendar.date_string()} {game.calendar.time_string()} | "
			f"{npc.full_name} departed {settlement.name} | "
			f"overworld position: {(npc.gx, npc.gy)}",
		)
	
def choose_offscreen_goals(game, npc, settlement):
	for need_id in npc.needs:
		if not should_address_need(npc, need_id):
			continue

		goals = [
			goal for goal in need_goals
			if goal.can_start_offscreen(
				game, npc, settlement, need_id=need_id,
			)
		]
		if goals:
			return goals, need_id

	leave_town = GOALS["leave_town"]
	if leave_town.can_start_offscreen(game, npc, settlement):
		return [leave_town], None

	if npc.profession is not None and npc.work_shift.is_active(game.calendar):
		return [], None

	play_goals = [
		goal for goal in ai_goals
		if goal.can_start_offscreen(game, npc, settlement)
	]
	return play_goals, None	
	
def run_offscreen_ai(game, active_settlement):
	towns_updated = 0
	goals_completed = 0

	for settlement in game.settlements:
		if settlement is active_settlement:
			continue

		residents = [npc for npc in settlement.npcs or [] if npc.alive]
		if not residents:
			continue

		npc = random.choice(residents)
		npc.update_needs()
		towns_updated += 1

		goals, need_id = choose_offscreen_goals(game, npc, settlement)

		if goals:
			goal = random.choice(goals)
			completed = goal.run_offscreen_ai(
				game, npc, settlement, need_id=need_id,
			)
		else:
			completed = run_offscreen_work(game, npc, settlement)

		if completed:
			goals_completed += 1

	if game.debug_enabled:
		calendar = game.calendar
		aidebug.write_log(
			game,
			"overworld_debug_log",
			f"{calendar.date_string()} {calendar.time_string()} | "
			f"offscreen tick | towns updated: {towns_updated} | "
			f"goals completed: {goals_completed}",
		)
	
def run_offscreen_work(game, npc, settlement):
	profession = npc.profession
	if profession is None or not npc.work_shift.is_active(game.calendar):
		return False

	return profession.run_offscreen_ai(game, npc, settlement)	
	
def need_ai(game, npc, town_map):
	if npc.handling_need and npc.actions:
		return True

	npc.handling_need = False

	hour = (
		game.calendar.date_string(),
		game.calendar.hour,
		game.calendar.is_pm,
	)

	if npc.last_need_check == hour:
		return False

	npc.last_need_check = hour

	for need_id in npc.needs:
		if not should_address_need(npc, need_id):
			continue

		available_goals = [
			goal for goal in need_goals
			if goal.can_start(game, npc, town_map, need_id)
		]

		if not available_goals:
			continue

		goal = random.choice(available_goals)

		npc.actions.clear()
		npc.current_activity = None

		goal.add_actions(game, npc, town_map, need_id)

		if npc.actions:
			npc.handling_need = True
			return True

	return False
		
def work_ai(game, npc, town_map):
	is_work_time = (
		npc.profession is not None
		and npc.work_shift.is_active(game.calendar)
	)
	exchanging = bool(npc.actions) and npc.actions[-1][0] == "exchange_currency"

	if not is_work_time:
		if not exchanging:
			npc.actions.clear()
			npc.current_activity = None
		return

	if exchanging:
		npc.actions.clear()
		npc.current_activity = None

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

#AI Goals
class AIGoal:
	offscreen_message = "completed an offscreen goal"

	def can_start(self, game, npc, town_map, need_id=None):
		return False

	def add_actions(self, game, npc, town_map, need_id=None):
		pass
		
	def can_start_offscreen(self, game, npc, settlement, *, need_id=None):
		return False

	def run_offscreen_ai(self, game, npc, settlement, *, need_id=None):
		return False

	def log_offscreen_result(self, game, npc, settlement, details=""):
		if not game.debug_enabled:
			return

		calendar = game.calendar
		message = (
			f"{calendar.date_string()} {calendar.time_string()} | "
			f"{settlement.name} | {npc.full_name} | "
			f"{self.offscreen_message}"
		)

		if details:
			message += f" | {details}"

		aidebug.write_log(game, "overworld_debug_log", message)

class BuyNeedItem(AIGoal):
	offscreen_message = "bought an item to satisfy a need"
	
	def get_candidates(self, game, npc, town_map, need_id):
		return self.get_candidates_in_settlement(
			game, npc, town_map.settlement, need_id,
		)

	def get_candidates_in_settlement(self, game, npc, settlement, need_id):
		sub_economy = settlement.sub_economy
		money = npc.wallet.get_quantity(settlement.currency)
		candidates = []

		for item_id, quantity in sub_economy.inventory.items():
			if quantity <= 0:
				continue

			need_values = npc.get_item_need_values(item_id, game)
			if need_values.get(need_id, 0) <= 0:
				continue

			price = sub_economy.get_value(item_id)
			if price <= money:
				candidates.append(item_id)

		return candidates

	def can_start(self, game, npc, town_map, need_id):
		if not town_map.get_buildings(is_shop=True):
			return False

		return bool(self.get_candidates(game, npc, town_map, need_id))

	def add_actions(self, game, npc, town_map, need_id):
		shops = town_map.get_buildings(is_shop=True)
		candidates = self.get_candidates(game, npc, town_map, need_id)

		if not shops or not candidates:
			return

		shop = random.choice(shops)
		item_id = random.choice(candidates)

		npc.actions.extend([
			("travel", shop),
			("buy_material", (shop, item_id, 1)),
			("consume", item_id),
		])

	def can_start_offscreen(self, game, npc, settlement, *, need_id=None):
		if need_id is None or not settlement.has_building("market_building"):
			return False

		return bool(
			self.get_candidates_in_settlement(game, npc, settlement, need_id)
		)

	def run_offscreen_ai(self, game, npc, settlement, *, need_id=None):
		candidates = self.get_candidates_in_settlement(
			game, npc, settlement, need_id,
		)
		if not candidates:
			return False

		item_id = random.choice(candidates)
		if not game.buy_item(npc, settlement, item_id):
			return False

		consumed = npc.consume_item(item_id, game)
		self.log_offscreen_result(
			game, npc, settlement,
			f"item: {item_id} | need: {need_id} | consumed: {consumed}",
		)
		return True

class ConsumeCarriedItem(AIGoal):
	offscreen_message = "consumed a carried item"
	
	def can_start(self, game, npc, town_map, need_id):
		return npc.find_item_for_need(need_id, game) is not None

	def add_actions(self, game, npc, town_map, need_id):
		item_id = npc.find_item_for_need(need_id, game)

		npc.actions.append(("consume", item_id))
		
	def can_start_offscreen(self, game, npc, settlement, *, need_id=None):
		return (
			need_id is not None
			and npc.find_item_for_need(need_id, game) is not None
		)
		
	def run_offscreen_ai(self, game, npc, settlement, *, need_id=None):
		if need_id is None:
			return False

		item_id = npc.find_item_for_need(need_id, game)
		if item_id is None:
			return False

		if not npc.consume_item(item_id, game):
			return False

		self.log_offscreen_result(
			game,
			npc,
			settlement,
			f"item: {item_id} | need: {need_id} | "
			f"remaining need value: {npc.needs[need_id]}",
		)
		return True

class ExchangeCurrency(AIGoal):
	offscreen_message = "completed an offscreen currency exchange"
	
	def get_exchange_candidates(self, game, npc, bank):
		local_coin = bank.get_currency()
		if local_coin not in game.coin_objs:
			return []

		candidates = []
		for coin_id, quantity in npc.wallet.get_coins():
			if quantity <= 0 or coin_id == local_coin or coin_id not in game.coin_objs:
				continue

			quote = bank.get_exchange_quote(game, coin_id, quantity)
			if quote is not None and quote[2] > 0:
				candidates.append((coin_id, quantity))

		return candidates

	def can_start(self, game, npc, town_map):
		bank = town_map.settlement.bank
		return (
			bank is not None
			and bool(town_map.get_buildings(building_type="bank_building"))
			and bool(self.get_exchange_candidates(game, npc, bank))
		)

	def add_actions(self, game, npc, town_map):
		bank = town_map.settlement.bank
		buildings = town_map.get_buildings(building_type="bank_building")
		candidates = self.get_exchange_candidates(game, npc, bank)
		coin_id, _ = random.choice(candidates)
		building = random.choice(buildings)

		npc.actions.extend([
			("travel", building),
			("exchange_currency", (building, coin_id)),
		])

	def can_start_offscreen(self, game, npc, settlement, *, need_id=None):
		bank = settlement.bank
		return (
			bank is not None
			and settlement.has_building("bank_building")
			and bool(self.get_exchange_candidates(game, npc, bank))
		)

	def run_offscreen_ai(self, game, npc, settlement, *, need_id=None):
		bank = settlement.bank
		if bank is None or not settlement.has_building("bank_building"):
			return False

		candidates = self.get_exchange_candidates(game, npc, bank)
		if not candidates:
			return False

		coin_id, quantity = random.choice(candidates)
		local_coin = bank.get_currency()
		local_before = npc.wallet.get_quantity(local_coin)

		if not bank.exchange_currency(game, npc, coin_id, quantity):
			return False

		received = npc.wallet.get_quantity(local_coin) - local_before
		self.log_offscreen_result(
			game, npc, settlement,
			f"exchanged {quantity} {coin_id} for {received} {local_coin}",
		)
		return True

class Idle(AIGoal):
	def can_start(self, game, npc, town_map):
		return True

	def add_actions(self, game, npc, town_map):
		npc.actions.append(("idle", None))
		
class LeaveTown(AIGoal):
	def can_start(self, game, npc, town_map):
		return getattr(npc, "days_until_departure", None) == 0

	def add_actions(self, game, npc, town_map):
		position = (npc.lx, npc.ly)
		exit_tile = getattr(npc, "tile_target", None)
		npc.actions.clear()
		npc.current_activity = None

		blocked = {
			(other.lx, other.ly)
			for other in town_map.settlement.npcs or []
			if other is not npc
		}
		blocked.add((game.player.lx, game.player.ly))

		if exit_tile is not None:
			path = town_map.find_path(position, [exit_tile], blocked)
			if path is not None:
				if path:
					npc.actions.append(("move", path[0]))
				return

		npc.tile_target = None
		last = town_map.map_size - 1
		edges = [
			[(x, 0) for x in range(town_map.map_size)],
			[(x, last) for x in range(town_map.map_size)],
			[(0, y) for y in range(town_map.map_size)],
			[(last, y) for y in range(town_map.map_size)],
		]
		random.shuffle(edges)

		for edge in edges:
			goals = [
				(x, y) for x, y in edge
				if (x, y) not in blocked and town_map.is_walkable(x, y)
			]
			if not goals:
				continue

			path = town_map.find_path(position, goals, blocked)
			if path is None:
				continue

			npc.tile_target = path[-1] if path else position
			if path:
				npc.actions.append(("move", path[0]))
			return
			
	def can_start_offscreen(self, game, npc, settlement, *, need_id=None):
		return npc.days_until_departure == 0

	def run_offscreen_ai(self, game, npc, settlement, *, need_id=None):
		move_npc_to_overworld(game, npc, settlement)
		return True
		
class Wander(AIGoal):
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
		
GOALS = {
	"exchange_currency": ExchangeCurrency(),
	"wander": Wander(),
	"idle": Idle(),
	"leave_town": LeaveTown(),
	"consume_carried_item": ConsumeCarriedItem(),
	"buy_need_item": BuyNeedItem(),
}

ai_goals = [
	GOALS["wander"],
	GOALS["idle"],
	GOALS["exchange_currency"],
]

need_goals = [
	GOALS["consume_carried_item"],
	GOALS["buy_need_item"],
]

#Actions
def exchange_currency(game, npc, town_map, target):
	building, coin_id = target
	settlement = town_map.settlement
	bank = settlement.bank

	if bank is None or (npc.lx, npc.ly) not in town_map.get_building_positions(building):
		return None

	quantity = npc.wallet.get_quantity(coin_id)
	local_coin = bank.get_currency()
	local_before = npc.wallet.get_quantity(local_coin) if local_coin else 0
	success = bank.exchange_currency(game, npc, coin_id, quantity)

	if game.debug_enabled:
		if success:
			received = npc.wallet.get_quantity(local_coin) - local_before
			result = f"exchanged {quantity} {coin_id} for {received} {local_coin}"
		else:
			result = f"exchange failed: {quantity} {coin_id}"

		calendar = game.calendar
		aidebug.write_log(
			game,
			"town_debug_log",
			f"{calendar.date_string()} {calendar.time_string()} | "
			f"{settlement.name} | {npc.full_name} | {result}",
		)

	return True
	
def idle(game, npc, town_map, target):
	return True	
	
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
	settlement = town_map.settlement
	corpse_ids = game.get_local_corpse_ids(settlement)
	if not corpse_ids:
		return None

	calendar = game.calendar
	hour = (calendar.date_string(), calendar.hour, calendar.is_pm)

	if character.current_activity is None:
		character.current_activity = {
			"id": "hunting",
			"started": hour,
		}
		return False

	if character.current_activity["started"] == hour:
		return False

	corpse_id = game.profession_objs["hunter"].attempt_hunt(
		game, character, settlement, corpse_ids,
	)

	if corpse_id is not None:
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

	if coordinates not in character.memory.known_locations:
		return None

	parchment_id = next(
		(
			item_id
			for item_id, quantity in character.inventory.get_items()
			if quantity > 0
			and (
				item_id == "parchment"
				or getattr(game.item_type_objs.get(item_id), "type_id", None)
				== "parchment"
			)
		),
		None,
	)

	if parchment_id is None:
		return None

	reagents = {
		"ink": 1,
		parchment_id: 1,
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
		character.remove_carried_object(item_id, game, quantity)

	cartography_level = character.get_skill_lvl("cartography")

	map_item = game.create_map(
		location=location,
		creator=character.full_name.strip() or "None",
		cartography_lvl=cartography_level,
	)

	character.add_carried_object(map_item.id, game, quantity=1)
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
	
def collect_water(game, character, town_map, target):
	water = town_map.settlement.resources["water"]
	if water <= 0:
		return None

	hour = (
		game.calendar.date_string(),
		game.calendar.hour,
		game.calendar.is_pm,
	)

	if character.current_activity is None:
		character.current_activity = {
			"id": "water_collecting",
			"started": hour,
		}
		return False

	if character.current_activity["started"] == hour:
		return False

	if random.randint(1, 100) <= water:
		if character.add_carried_object("water", game, quantity=1):
			return True

	character.current_activity["started"] = hour
	return False
	
def forage(game, character, town_map, target):
	settlement = town_map.settlement
	fruit_ids = character.profession.get_local_fruit_ids(settlement, game)
	if not fruit_ids:
		return None

	hour = (
		game.calendar.date_string(),
		game.calendar.hour,
		game.calendar.is_pm,
	)

	if character.current_activity is None:
		character.current_activity = {
			"id": "foraging",
			"started": hour,
		}
		return False

	if character.current_activity["started"] == hour:
		return False

	flora = settlement.resources["flora"]
	foraging_level = character.get_skill_lvl("foraging")
	chance = min(100, max(0, (flora + foraging_level) / 2))

	success = False
	if random.randint(1, 100) <= chance:
		fruit_id = random.choice(fruit_ids)
		success = character.add_carried_object(fruit_id, game, quantity=1)

	character.gain_skill_xp("foraging")

	if success:
		return True

	character.current_activity["started"] = hour
	return False
	
def consume(game, character, town_map, target):
	if not character.consume_item(target, game):
		return None

	return True
	
action_dict = {
	"exchange_currency": exchange_currency,
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
	"collect_water": collect_water,
	"forage": forage,
	"consume": consume,
}

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
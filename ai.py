import random

def start_ai(game, town_map):
	for npc in town_map.settlement.npcs or []:
		if not npc.alive:
			continue

		work_ai(game, npc, town_map)

		if not npc.actions:
			choose_goal(game, npc, town_map)

		position_before = (npc.lx, npc.ly)
		action = npc.actions[0] if npc.actions else None

		do_ai(game, npc, town_map)
		
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
	pickaxe_id = character.find_inventory_item(game.pickaxe_objs)

	if pickaxe_id is None or not game.ore_objs:
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
		
	
	
action_dict = {
	"move": move,
	"idle": idle,
	"travel": travel,
	"mine": mine,
	"sell": sell,
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

	return action_id

def debug_npc_turn(game, character, position_before, action):
	position_after = (character.lx, character.ly)

	next_action = (
		character.actions[0]
		if character.actions
		else None
	)

	is_work_time = character.work_shift.is_active(game.calendar)

	print(
		f"[{character.profession_id}: {character.full_name}] "
		f"{game.calendar.time_string()} | "
		f"On shift: {is_work_time} | "
		f"Action: {describe_action(action)} | "
		f"Position: {position_before} -> {position_after} | "
		f"Next: {describe_action(next_action)} | "
		f"Activity: {character.current_activity} | "
		f"Inventory: {list(character.inventory.get_items())} | "
		f"Coins: {list(character.wallet.get_coins())}"
	)
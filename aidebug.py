from pathlib import Path


LOG_PATH = Path("town_debug.log")


def start_turn(game, town_map):
	if not game.debug_enabled:
		return None

	settlement = town_map.settlement
	calendar = game.calendar

	hour_key = (
		calendar.date_string(),
		calendar.hour,
		calendar.is_pm,
	)

	if not hasattr(game, "debug_last_logged_hour"):
		game.debug_last_logged_hour = {}

	town_key = (settlement.gx, settlement.gy)

	if game.debug_last_logged_hour.get(town_key) == hour_key:
		return None

	game.debug_last_logged_hour[town_key] = hour_key

	return {
		"game": game,
		"settlement": settlement,
		"entries": [],
	}


def run_action(debug, game, npc, town_map, do_ai):
	if debug is None:
		do_ai(game, npc, town_map)
		return

	action = npc.actions[0] if npc.actions else None
	action_text = describe_action(action)
	position_before = (npc.lx, npc.ly)

	do_ai(game, npc, town_map)

	next_action = npc.actions[0] if npc.actions else None
	profession = npc.profession
	on_shift = (
		profession is not None
		and npc.work_shift.is_active(game.calendar)
	)

	debug["entries"].append(
		f"{npc.full_name} ({npc.profession_id}) | "
		f"on shift: {on_shift} | "
		f"action: {action_text} | "
		f"next: {describe_action(next_action)} | "
		f"position: {position_before} -> {(npc.lx, npc.ly)} | "
		f"inventory: {dict(npc.inventory.get_items())} | "
		f"coins: {dict(npc.wallet.get_coins())}"
	)


def describe_action(action):
	if action is None:
		return "none"

	action_id, target = action

	if action_id == "travel":
		return f"travel to {target.get_name()}"

	if action_id in ("buy", "sell"):
		shop, item_id = target
		return f"{action_id} {item_id} at {shop.get_name()}"

	if action_id == "buy_material":
		shop, item_id, quantity = target
		return f"buy {quantity} {item_id} at {shop.get_name()}"

	if action_id == "craft":
		return f"craft {target}"

	if action_id == "make_map":
		return f"make map to {target.name}"

	return action_id


def finish_turn(debug):
	if debug is None:
		return

	settlement = debug["settlement"]
	calendar = debug["game"].calendar

	with LOG_PATH.open("a", encoding="utf-8") as log:
		log.write(
			f"\n{settlement.name} ({settlement.gx}, {settlement.gy}) | "
			f"{calendar.date_string()} {calendar.time_string()}\n"
		)

		for entry in debug["entries"]:
			log.write(entry + "\n")
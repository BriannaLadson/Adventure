import random

def start_ai(game, town_map):
	for npc in town_map.settlement.npcs or []:
		if not npc.alive:
			continue
			
		choose_goal(game, npc, town_map)
		
		do_ai(game, npc, town_map)
		
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
	
	completed = action(game, npc, town_map, target)
	
	if completed:
		npc.actions.pop(0)
		
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
	
action_dict = {
	"move": move,
	"idle": idle,
}


ai_goals = [
	Wander(),
	Idle(),
]
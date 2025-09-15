import turnsystem as turnsys

def process_cmd(event, screen, cmd):
	try:
		cmd_dict[cmd](screen, cmd)
		
		turnsys.take_turn(screen.game, screen.game.turns)
		
		screen.update_screen()
	
	except KeyError:
		pass
		
def mine(screen, cmd):
	game = screen.game
	player = game.player
	
	mine_progress = player.get_skill_progress("mining")
	
	ore_deposit = player.action_target
	
	screen.action_bar.action_target = player.action_target
	
	ore_deposit.mod_progress(mine_progress, player)
	
	player.mod_skill_xp("mining")
	
	game.turns = 1
		
def move(screen, cmd):
	game = screen.game
	player = screen.player
	
	if not player.busy:
		game.move_entity(player, cmd)
		
cmd_dict = {
	"north": move,
	"northwest": move,
	"northeast": move,
	"south": move,
	"southwest": move,
	"southeast": move,
	"west": move,
	"east": move,
	"in": move,
	"mine": mine,
}
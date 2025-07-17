def process_cmd(event, screen, cmd):
	try:
		cmd_dict[cmd](screen, cmd)
		
		screen.update_screen()
	
	except KeyError:
		pass
		
def move(screen, cmd):
	game = screen.game
	player = screen.player
	
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
}
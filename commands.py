def process_cmd(event, screen, cmd):
	if not screen.can_process_input:
		return
	
	try:
		game = screen.game
		
		cmd_dict[cmd](screen, cmd)
		
		game.inc_time()
		
		new_locations = screen.discover_locations()
		
		screen.update_screen()
		
		screen.handle_discovered_locations(new_locations)
		
	except KeyError:
		pass
		
def move(screen, cmd):
	game = screen.game
	player = screen.player
	
	game.move_entity(player, cmd)
	
	screen.update_tile_map = True
	
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
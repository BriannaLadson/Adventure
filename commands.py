def process_cmd(event, screen, cmd):
	if not screen.can_process_input:
		return
	
	try:
		game = screen.game
		
		cmd_dict[cmd](screen, cmd)
		
		dead_entities = game.inc_time()
		
		if game.player in dead_entities:
			screen.handle_player_death()
			return
			
		low_needs = game.player.get_low_needs()
		
		if low_needs:
			screen.handle_low_needs(low_needs)
			return
		
		new_locations = screen.discover_locations()
		
		screen.update_screen()
		
		building = screen.check_building_interaction()
		
		if building is not None:
			screen.handle_building_interaction(building)
			
			return
		
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
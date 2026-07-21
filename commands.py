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
	
def pickup_item(screen, cmd):
	game = screen.game
	player = screen.player
	
	if player.lx == None or player.ly == None or player.lz == None:
		return
	
	settlement = game.get_settlement_by_coors(player.gx, player.gy)
	
	coors = (
		player.lx,
		player.ly,
		player.lz,
	)
	
	if coors not in settlement.dropped_items:
		return
		
	tile_inventory = settlement.dropped_items[coors]
		
	second_inv_text = f"Tile ({coors[0]}, {coors[1]}, {coors[2]})"
		
	screen.pickup_item(player.inventory, tile_inventory, "You", second_inv_text)
	
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
	"pickup_item": pickup_item,
}
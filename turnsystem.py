def take_turn(game, turns):
	for turn in range(turns):
		game.advance_minutes(1)
		
	game.turns = 0
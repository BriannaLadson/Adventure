import entities

def generate_world(game):
	generate_civilizations(game)
	generate_capitals(game)
	generate_settlements(game)
	
def generate_civilizations(game):
	game.civilizations = []
	
	for race in game.race_objs.values():
		for _ in range(race.civilization_number):
			game.generate_civilization(race)
		
def generate_capitals(game):
	for civ in game.civilizations:
		capital = game.generate_settlement(civ.culture)
		
		if not capital == None:
			capital.is_capital = True
			civ.capital = capital
			
def generate_settlements(game):
	for civ in game.civilizations:
		for _ in range(civ.culture.settlement_number):
			settlement = game.generate_settlement(civ.culture)
			
			if not settlement == None:
				civ.settlements.append(settlement)
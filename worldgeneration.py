import entities
import institutions

def generate_world(game):
	generate_civilizations(game)
	generate_capitals(game)
	generate_settlements(game)
	generate_institutions(game)
	
	for _ in range(game.initial_production_cycles):
		game.run_settlement_production()
	
def generate_civilizations(game):
	game.civilizations = []
	
	for race in game.race_objs.values():
		for _ in range(race.civilization_number):
			game.generate_civilization(race)
		
def generate_capitals(game):
	for civ in game.civilizations:
		capital = game.generate_settlement(civ, civ.culture, is_capital=True)
		
		if not capital == None:
			civ.capital = capital
			
def generate_settlements(game):
	for civ in game.civilizations:
		for _ in range(civ.culture.settlement_number):
			settlement = game.generate_settlement(civ, civ.culture)
			
			if not settlement == None:
				civ.settlements.append(settlement)
				
def generate_institutions(game):
	for settlement in game.settlements:
		if settlement.has_building("bank_building"):
			settlement.bank = institutions.Bank(settlement)
import random

class Profession:
	def __init__(self):
		self.id = "profession"
		
		self.name = "Profession"
		
		self.outputs = []
		
		self.can_craft = True
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		workers = settlement.get_profession_quantity(self)

		for _ in range(workers):
			item_id = random.choice(self.outputs)
			item_type = game.item_type_objs[item_id]
			reagents = getattr(item_type, "reagents", {})

			if not reagents:
				sub_economy.add_item(item_id)
				continue

			can_make = all(
				sub_economy.has_item(reagent_id, amount)
				for reagent_id, amount in reagents.items()
			)

			if can_make:
				for reagent_id, amount in reagents.items():
					sub_economy.remove_item(reagent_id, amount)
					sub_economy.change_modifier(reagent_id, -amount)

				sub_economy.add_item(item_id)

			else:
				for reagent_id, amount in reagents.items():
					if not sub_economy.has_item(reagent_id, amount):
						sub_economy.change_modifier(reagent_id, amount)
		
class Hunter(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "hunter"
		
		self.name = "Hunter"
		
		self.can_craft = False
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		hunters = settlement.get_profession_quantity(self)
		fauna = settlement.resources["fauna"]
	
		animal_corpse_quantity = int(hunters * (fauna / 100)) * 8
		
		sub_economy.add_item("animal_corpse", quantity=animal_corpse_quantity)
		
class Cartographer(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "cartographer"
		
		self.name = "Cartographer"
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		cartographers = settlement.get_profession_quantity(self)
		
		for i in range(cartographers):
			parchment_quantity = sub_economy.get_quantity("parchment")
			ink_quantity = sub_economy.get_quantity("ink")
			
			if parchment_quantity < 1:
				sub_economy.change_modifier("parchment", 1)
				
			if ink_quantity < 1:
				sub_economy.change_modifier("ink", 1)
			
			if parchment_quantity >= 1 and ink_quantity >= 1:
				sub_economy.remove_item("parchment", 1)
				sub_economy.remove_item("ink", 1)
				
				sub_economy.change_modifier("parchment", -1)
				sub_economy.change_modifier("ink", -1)
				
				location = game.get_random_location()
				cartography_lvl = random.randint(1, 100)
				
				map_item = game.create_map(location, cartography_lvl=cartography_lvl, settlement=settlement)
				
				sub_economy.add_item(map_item.id)
				
				
				
		
class Butcher(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "butcher"
		
		self.name = "Butcher"
		
		self.outputs = [
			"animal_hide",
			"animal_meat",
		]
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		butchers = settlement.get_profession_quantity(self)
		
		for _ in range(butchers):
			has_corpse = sub_economy.has_item("animal_corpse", 1)
			
			if has_corpse:
				sub_economy.remove_item("animal_corpse", 1)
				sub_economy.change_modifier("animal_corpse", -1)
				
				sub_economy.add_item("animal_hide", 1)
				sub_economy.add_item("animal_meat", 3)
				
			else:
				sub_economy.change_modifier("animal_corpse", 1)
		
class InkMaker(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "ink_maker"
		
		self.name = "Ink Maker"
		
		self.outputs = [
			"ink",
		]
		
class Tanner(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "tanner"
		
		self.name = "Tanner"
		
		self.outputs = [
			"animal_leather"
		]
		
class TreeCutter(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "tree_cutter"
		
		self.name = "Tree Cutter"
		
		self.can_craft = False
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		tree_cutters = settlement.get_profession_quantity(self)
		
		trees = settlement.resources["trees"]
		
		wood_quantity = int(tree_cutters * (trees / 100)) * 8
		
		sub_economy.add_item("wood", quantity=wood_quantity)
		
class PaperMaker(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "paper_maker"
		
		self.name = "Paper Maker"
		
		self.outputs = [
			"parchment"
		]
		
class WoodBurner(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "wood_burner"
		
		self.name = "Wood Burner"
		
		self.outputs = [
			"coal"
		]
		
class Miner(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "miner"
		
		self.name = "Miner"
		
		self.outputs = [
			"gold_ore",
		]
		
		self.can_craft = False
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		miners = settlement.get_profession_quantity(self)
		
		mineral = settlement.resources["mineral"]
		
		ore_quantity = int(miners * (mineral / 100))
		
		for _ in range(ore_quantity):
			ore = random.choice(self.outputs)
			
			sub_economy.add_item(ore, quantity=1)
			
class Smelter(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "smelter"
		
		self.name = "Smelter"
		
		self.outputs = [
			"gold_bar",
		]
			
class Coinsmith(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "coinsmith"
		
		self.name = "Coinsmith"
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		coinsmiths = settlement.get_profession_quantity(self)
		
		for _ in range(coinsmiths):
			has_gold_bar = sub_economy.has_item("gold_bar", 1)
			has_coal = sub_economy.has_item("coal", 1)
			
			if has_gold_bar and has_coal:
				sub_economy.remove_item("gold_bar", 1)
				sub_economy.remove_item("coal", 1)
				
				sub_economy.change_modifier("gold_bar", -1)
				sub_economy.change_modifier("coal", -1)
				
				settlement.gold += 1
				
			else:
				if not has_gold_bar:
					sub_economy.change_modifier("gold_bar", 1)
					
				if not has_coal:
					sub_economy.change_modifier("coal", 1)
					
class WaterCollector(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "water_collector"
		
		self.name = "Water Collector"
		
		self.outputs = [
			"water"
		]
		
		self.can_craft = False
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		water_collectors = settlement.get_profession_quantity(self)
		
		water = settlement.resources["water"]
		
		water_quantity = int(water_collectors * (water / 100))
		
		sub_economy.add_item("water", quantity=water_quantity)
		
class Forager(Profession):
	def __init__(self):
		super().__init__()
		
		self.id = "forager"
		
		self.name = "Forager"
		
		self.outputs = [
			"fruit",
			"water",
		]
		
		self.can_craft = False
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		foragers = settlement.get_profession_quantity(self)
		
		flora = settlement.resources["flora"]
		water = settlement.resources["water"]
		
		chance = int((flora + water) / 2)
		
		forage_quantity = int(foragers * chance)
		
		for _ in range(forage_quantity):
			forage_item = random.choice(self.outputs)
			
			sub_economy.add_item(forage_item, quantity=1)
		
PROFESSIONS = {
	"hunter": Hunter(),
	"water_collector": WaterCollector(),
	"miner": Miner(),
	"tree_cutter": TreeCutter(),
	"forager": Forager(),
	"wood_burner": WoodBurner(),
	"butcher": Butcher(),
	"ink_maker": InkMaker(),
	"tanner": Tanner(),
	"paper_maker": PaperMaker(),
	"cartographer": Cartographer(),
	"smelter": Smelter(),
	"coinsmith": Coinsmith(),
}
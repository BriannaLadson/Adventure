import random

class Profession:
	def __init__(self):
		self.id = "profession"
		
		self.name = "Profession"
		
		self.outputs = []
		
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
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		hunters = settlement.get_profession_quantity(self)
		fauna = settlement.resources["fauna"]
	
		animal_corpse_quantity = int(hunters * (fauna / 100))
		
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
			"animal_hide"
		]
		
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
		
	def produce(self, settlement, game):
		sub_economy = settlement.sub_economy
		
		tree_cutters = settlement.get_profession_quantity(self)
		
		trees = settlement.resources["trees"]
		
		wood_quantity = int(tree_cutters * (trees / 100))
		
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
		
PROFESSIONS = {
	"hunter": Hunter(),
	"butcher": Butcher(),
	"ink_maker": InkMaker(),
	"tanner": Tanner(),
	"tree_cutter": TreeCutter(),
	"paper_maker": PaperMaker(),
	"wood_burner": WoodBurner(),
	"cartographer": Cartographer(),
}
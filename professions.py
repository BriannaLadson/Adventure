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
}
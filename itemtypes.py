class ItemType:
	def __init__(self):
		self.id = "item_type"
		
		self.name = "Item Type"
		
		self.base_value = 1
		
		self.creator = None
		
		self.description = ""
		
		self.actions = []
		
class AnimalCorpse(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "animal_corpse"
		
		self.name = "Animal Corpse"
		
		self.base_value = 2
		
class AnimalHide(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "animal_hide"
		
		self.name = "Animal Hide"
		
		self.reagents = {
			"animal_corpse": 1,
		}
		
		self.base_value = 2
		
class AnimalLeather(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "animal_leather"
		
		self.name = "Animal Leather"
		
		self.reagents = {
			"animal_hide": 1,
		}
		
		self.base_value = 4
		
class Coal(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "coal"
		
		self.name = "Coal"
		
		self.reagents = {
			"wood": 1,
		}
		
		self.base_value = 2
		
class Fruit(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "fruit"
		
		self.name = "Fruit"
		
		self.need_values = {
			"hunger": 15,
		}
		
		self.base_value = 2
		
		self.actions = [
			"consume",
		]
		
class GoldBar(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "gold_bar"
		
		self.name = "Gold Bar"
		
		self.reagents = {
			"coal": 1,
			"gold_ore": 1,
		}
		
		self.base_value = 10
		
class GoldOre(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "gold_ore"
		
		self.name = "Gold Ore"
		
		self.base_value = 5
		
class Ink(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "ink"
		
		self.name = "Ink"
		
		self.reagents = {
			"coal": 1,
		}
		
		self.base_value = 4
		
class AnimalMeat(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "animal_meat"
		
		self.name = "Animal Meat"
		
		self.need_values = {
			"hunger": 25,
		}
		
		self.base_value = 3
		
		self.actions = [
			"consume",
		]
		
class Parchment(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "parchment"
		
		self.name = "Parchment"
		
		self.base_value = 8
		
class Water(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "water"
		
		self.name = "Water"
		
		self.need_values = {
			"thirst": 25,
		}
		
		self.actions = [
			"consume",
		]
		
class Wood(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "wood"
		
		self.name = "Wood"
		
ITEM_TYPES = {
	"animal_corpse": AnimalCorpse(),
	"animal_hide": AnimalHide(),
	"animal_leather": AnimalLeather(),
	"animal_meat": AnimalMeat(),
	"coal": Coal(),
	"fruit": Fruit(),
	"gold_bar": GoldBar(),
	"gold_ore": GoldOre(),
	"ink": Ink(),
	"parchment": Parchment(),
	"water": Water(),
	"wood": Wood(),
}
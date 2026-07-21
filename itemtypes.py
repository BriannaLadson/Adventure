class ItemType:
	def __init__(self):
		self.id = "item_type"
		
		self.name = "Item Type"
		
		self.base_value = 1
		
		self.creator = None
		
		self.description = ""
		
		self.actions = [
			"drop",
		]
		
class BarType(ItemType):
	def __init__(self, *args):
		super().__init__()
		
		self.id = args[0]
		
		self.name = args[1]
		
		self.reagents = args[2]
		
		self.base_value = args[3]
		
class CoinType(ItemType):
	def __init__(self, *args):
		super().__init__()
		
		self.id = args[0]
		
		self.name = args[1]
		
		self.reagents = args[2]
		
		self.base_value = args[3]
		
class OreType(ItemType):
	def __init__(self, *args):
		super().__init__()
		
		self.id = args[0]
		
		self.name = args[1]
		
		self.base_value = args[2]
		
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
			"drop",
		]
		
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
			"drop",
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
			"drop",
		]
		
class Wine(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "wine"
		
		self.name = "Wine"
		
		self.base_value = 10
		
		self.reagents = {
			"fruit": 1,
		}
		
		self.need_values = {
			"alcohol": 25,
		}
		
		self.actions = [
			"consume",
			"drop",
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
	"ink": Ink(),
	"parchment": Parchment(),
	"water": Water(),
	"wine": Wine(),
	"wood": Wood(),
}
class ItemType:
	def __init__(self):
		self.id = "item_type"
		
		self.name = "Item Type"
		
		self.base_value = 1
		
		self.creator = None
		
class AnimalCorpse(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "animal_corpse"
		
		self.name = "Animal Corpse"
		
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
		
class Ink(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "ink"
		
		self.name = "Ink"
		
		self.reagents = {
			"coal": 1,
		}
		
		self.base_value = 4
		
class Parchment(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "parchment"
		
		self.name = "Parchment"
		
		self.base_value = 8
		
class Wood(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "wood"
		
		self.name = "Wood"
		
ITEM_TYPES = {
	"animal_corpse": AnimalCorpse(),
	"animal_hide": AnimalHide(),
	"animal_leather": AnimalLeather(),
	"coal": Coal(),
	"ink": Ink(),
	"parchment": Parchment(),
	"wood": Wood(),
}
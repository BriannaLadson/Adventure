class ItemType:
	def __init__(
		self,
		id = "item_type",
		name = "Item Type",
		base_value = 1,
		weight = 1,
		categories = None,
		actions = None,
		description = "",
		properties = None,
		can_forage = False,
		type_id=None,
	):
		self.id = id
		
		self.name = name
		
		self.type_id = type_id or id
		
		self.base_value = base_value
		
		self.weight = weight
		
		self.categories = categories or []
		
		self.actions = actions or [
			"drop",
		]
		
		self.description = description
		
		self.properties = properties or {}
		
		self.can_forage = can_forage
		
		self.creator = None
		
class WineType(ItemType):
	VALUE_MULTIPLIER = 2
	
	def __init__(self, fruit):
		super().__init__(
			id = f"{fruit.id}_wine",
			name = f"{fruit.name} Wine",
			type_id = "wine",
			base_value = fruit.base_value * self.VALUE_MULTIPLIER,
			weight = 2,
		)
		
		self.fruit = fruit.id
		

		
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
		
		self.weight = 0.1
		
class FruitType(ItemType):
	def __init__(
		self,
		id,
		name,
		base_value = 1,
		weight = 1,
		can_forage = True,
	):
		super().__init__(
			id = id,
			name = name,
			type_id = "fruit",
			base_value = base_value,
			weight = weight,
			can_forage = can_forage,
		)
		
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
		
		self.weight = 20
		
class AnimalHide(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "animal_hide"
		
		self.name = "Animal Hide"
		
		self.reagents = {
			"animal_corpse": 1,
		}
		
		self.base_value = 2
		
		self.weight = 5
		
class AnimalLeather(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "animal_leather"
		
		self.name = "Animal Leather"
		
		self.reagents = {
			"animal_hide": 1,
		}
		
		self.base_value = 4
		
		self.weight = 3
		
class Coal(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "coal"
		
		self.name = "Coal"
		
		self.reagents = {
			"wood": 1,
		}
		
		self.base_value = 2
		
		self.weight = 3
		
		
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
		
		self.base_value = 3
		
		self.actions = [
			"consume",
			"drop",
		]
		
		self.weight = 5
		
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
		
		self.actions = [
			"consume",
			"drop",
		]
		
		self.weight = 2
		
class Wine(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "wine"
		
		self.name = "Wine"
		
		self.base_value = 10
		
		self.reagents = {
			"fruit": 1,
		}
		
		self.actions = [
			"consume",
			"drop",
		]
		
		self.weight = 2
		
class Wood(ItemType):
	def __init__(self):
		super().__init__()
		
		self.id = "wood"
		
		self.name = "Wood"
		
		self.weight = 5
		
ITEM_TYPES = {
	"animal_corpse": AnimalCorpse(),
	"animal_hide": AnimalHide(),
	"animal_leather": AnimalLeather(),
	"animal_meat": AnimalMeat(),
	"coal": Coal(),
	"ink": Ink(),
	"parchment": Parchment(),
	"water": Water(),
	"wine": Wine(),
	"wood": Wood(),
}
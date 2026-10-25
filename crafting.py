class CraftingReaction:
	def __init__(
		self,
		id,
		name,
		reagents,
		products,
		skill=None,
		ticks=1
	):
		self.id = id
		
		self.name = name
		
		self.reagents = reagents
		
		self.products = products
		
		self.skill = skill
		
		self.ticks = ticks
import uuid

class Item:
	def __init__(self):
		self.creator = None
		
		self.value = 1
		
		self.actions = []
		
		self.description = ""

class Map(Item):
	def __init__(self, location, gx, gy, creator=None, cartography_lvl=1, value=1):
		super().__init__()
		
		self.id = f"map_{uuid.uuid4().hex[:8]}"
		
		self.location = location
		
		self.name = f"Map to {location.name}"
		
		self.gx = gx
		self.gy = gy
		
		self.true_gx = location.gx
		self.true_gy = location.gy
		
		self.cartography_lvl = cartography_lvl
		
		self.creator = creator
		
		self.marked_incorrect = False
		
		self.value = value
		
		self.description = (
			f"Coordinates: ({self.gx},{self.gy})"
		)
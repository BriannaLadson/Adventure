class Inventory:
	def __init__(self, inventory=None):
		if inventory is None:
			inventory = {}
			
		self.inventory = inventory
		
	def get_quantity(self, item_id):
		return self.inventory.get(item_id, 0)
		
	def set_quantity(self, item_id, quantity):
		if quantity <= 0:
			self.inventory.pop(item_id, None)
			
		else:
			self.inventory[item_id] = quantity
		
	def add_item(self, item_id, quantity=1):
		self.inventory[item_id] = (
			self.get_quantity(item_id) + quantity
		)
			
		return True
		
	def remove_item(self, item_id, quantity=1):
		if self.get_quantity(item_id) < quantity:
			return False
			
		self.inventory[item_id] -= quantity
		
		if self.inventory[item_id] <=0:
			del self.inventory[item_id]
			
		return True
		
	def has_item(self, item_id, quantity=1):
		return self.get_quantity(item_id) >= quantity
		
	def get_items(self):
		return self.inventory.items()
		
	def clear(self):
		self.inventory.clear()
		
	def get_item_ids(self):
		return self.inventory.keys()
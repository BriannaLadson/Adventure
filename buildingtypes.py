class BuildingType:
	def __init__(self):
		self.id = "building_type"
		
		self.name = "Building Type"
		
		self.color = "#FFFFFF"
		
		self.size = (6, 10)
		
		self.popup_type = None
		
		self.settlement = None
		
class BankBuilding(BuildingType):
	def __init__(self):
		super().__init__()
		
		self.id = "bank_building"
		
		self.name = "Bank"
		
		self.color = "#7A8B99"
		
		self.size = (6, 10)
		
		self.popup_type = "bank"
		
class MarketBuilding(BuildingType):
	def __init__(self):
		super().__init__()
		
		self.id = "market_building"
		
		self.name = "Market"
		
		self.color = "#C2A14A"
		
		self.size = (6, 10)
		
		self.popup_type = "trade"
		
BUILDING_TYPES = {
	"bank_building": BankBuilding(),
	"market_building": MarketBuilding(),
}
class BuildingType:
	def __init__(self):
		self.id = "building_type"
		
		self.name = "Building Type"
		
		self.color = "#FFFFFF"
		
		self.size = (6, 10)
		
		self.popup_type = None
		
		self.settlement = None
		
class MarketBuilding(BuildingType):
	def __init__(self):
		super().__init__()
		
		self.id = "market_building"
		
		self.name = "Market"
		
		self.color = "#C2A14A"
		
		self.size = (6, 10)
		
		self.popup_type = "trade"
		
BUILDING_TYPES = {
	"market_building": MarketBuilding(),
}
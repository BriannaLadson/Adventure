class Trait:
	def __init__(self, name):
		self.name = name

class WorkTrait(Trait):
	def __init__(self, name, start_hour, end_hour):
		super().__init__(name)
		
		self.start_hour = start_hour
		self.end_hour = end_hour
		
	def is_active(self, calendar):
		hour = calendar.hour % 12
		
		if calendar.is_pm:
			hour += 12
			
		if self.start_hour < self.end_hour:
			return self.start_hour <= hour < self.end_hour
			
		return hour >= self.start_hour or hour < self.end_hour
		
WORK_SHIFTS = [
	WorkTrait("1st Shift", 6, 14),
	WorkTrait("2nd Shift", 14, 22),
	WorkTrait("3rd Shift", 22, 6),
]
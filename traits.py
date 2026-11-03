class Trait:
	def __init__(self, name):
		self.name = name
		
class HandednessTrait(Trait):
	def __init__(self, name, hand_levels, preferred_hand_skill=None):
		super().__init__(name)

		self.hand_levels = hand_levels
		self.preferred_hand_skill = preferred_hand_skill

	def apply(self, character):
		for skill_id, level in self.hand_levels.items():
			skill = character.skills[skill_id]

			skill["level"] = level
			skill["xp"] = 0
			skill["max_xp"] = (level + 1) * 100


HANDEDNESS_TRAITS = [
	HandednessTrait(
		"Ambidextrous",
		{
			"left_hand": 100,
			"right_hand": 100,
		},
	),
	HandednessTrait(
		"Left-Handed",
		{
			"left_hand": 100,
			"right_hand": 1,
		},
		preferred_hand_skill="left_hand",
	),
	HandednessTrait(
		"Right-Handed",
		{
			"left_hand": 1,
			"right_hand": 100,
		},
		preferred_hand_skill="right_hand",
	),
]

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
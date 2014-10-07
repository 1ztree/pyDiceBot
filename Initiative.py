import Character

class Initiative:

	is_combat = False
	
	def __init__(self):
		self.initiative_order = []
	
	# Get the initiative order and return the array detailing the order.
	def getOrder(self):
		return self.initiative_order
	
	# Parses a regex to add new characters to the initiative list.
	def addInitiative(self, regex):
		group_size = 0
		m = re.match("#Roll ([1-9][0-9]?)?\s?(.*)?\s?([1-9][0-9]?)D([1-9][0-9]?)\s?\+?\s?([1-9][0-9]?)?", regex)
		group_size = int(m.group(1))
		name = m.group(2)
		num_dice = m.group(3)
		type_dice = m.group(4)
		mod = m.group(5) 
		each_roll = []
		total_roll = 0
		if group_size:
			n = 0
			while n < group_size:
				each_roll = rollDice(type_dice, int(num_dice))
				total_roll = totalRoll(each_roll, mod)
				char = Character(name, total_roll)
				self.initiative_order.add(char)
				n += 1
		else:
			each_roll = rollDice(type_dice, int(num_dice))
			total_roll = totalRoll(each_roll, mod)
			char = Character(name, total_roll)
			self.initiative_order.append(char)
		
	def startCombat(self):
		is_combat = True
	
	def endCombat(self):
		is_combat = False

	# Takes the type of dice to be rolled, and the number of dice to be rolled, and returns a list of random die rolls.
	# rollDice : int, int -> List 
	def rollDice(type_dice, n):
			# Seed the RNG with the current system time
			random.seed()
			each_roll = []
			while n > 0 :
				each_roll.append(random.randint(1, int(type_dice)))
				n = n - 1
			return each_roll
	
	# Totals up a given roll.
	# totalRoll : List[int], int -> int
	def totalRoll(rolls, mod):
		total_roll = 0
		for roll in rolls:
			total_roll = total_roll + roll
		if (mod == 0):
			return total_roll
		else:
			return total_roll + mod
			
	def updateInitiative(self, new_round):
		if new_round:
			for char in self.initiative_order:
				char = char - 10
				if char.getInit() <= 0:
					self.initiative_order.remove(char)
		self.initiative_order = qsort(self.initiative_order)
			
	def qsort(inlist):
    if inlist == []: 
        return []
    else:
        pivot = inlist[0].getInit()
        lesser = qsort([x for x in inlist[1:].getInit() if x < pivot])
        greater = qsort([x for x in inlist[1:] if x >= pivot])
        return lesser + [pivot] + greater
		

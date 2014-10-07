class Character:
	
	def __init__(self, name, init):
		self.name = name
		self.init = init
	
	def getName(self):
		return self.name
	
	def getInit(self):
		return self.init
		
	def __lt__(self, right):
		return self.init < right.getInit()
		
	def __ge__(self, right):
		return self.init >= right.getInit()
		
	def __eq__(self, right):
		return self.init == right.getInit()
		
	def __sub__(self, right):
		return self.init - right

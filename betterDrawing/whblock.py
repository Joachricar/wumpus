from whpoint import Point

##############################################
# Block
# t = type
# e = explored
##############################################
class Block():
	def __init__(self, t, p):
		self.t = t
		self.references = 0
		self.e = False
		self.p = p
	
	def __init__(self, t, x, y):
		self.t = t
		self.references = 0
		self.e = False
		self.p = Point(x, y)
	
	def setType(self, t):
		if self.t == "wall":
			return
		
		if self.t == "empty" and t == "wall":
			self.t = "wall"
		
		elif self.t == "empty":
			return
		else:
			self.t = t
	
	def isSafe(self):
		if self.t == "empty":
			return True
		return False

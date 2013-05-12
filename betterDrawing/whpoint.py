##############################################
# Point class
# Keeps track of a point and can turn and move
##############################################
class Point():
	def __init__(self, x, y):
		self.x = x
		self.y = y
		
	def turnLeft(self):
		new_dir_x = self.y
		new_dir_y = -self.x
		
		self.y = new_dir_y
		self.x = new_dir_x
	
	def turnRight(self):
		new_dir_x = -self.y
		new_dir_y = self.x
		
		self.y = new_dir_y
		self.x = new_dir_x
	
	def move(self, direction):
		self.x += direction.x
		self.y += direction.y
	
	def back(self, direction):
		self.x -= direction.x
		self.y -= direction.y

	def clone(self):
		return Point(self.x, self.y)

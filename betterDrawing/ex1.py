import sys
#import and init pygame
import pygame
pygame.init() 

n = 40 # 40x40 map
block = 20 # blocksize = 20px

#create the screen
window = pygame.display.set_mode((block*n, block*n)) 

class Block():
	def __init__(self, t):
		self.t = t
	

class Board():
	#the board
	def __init__(self, n, w):
		#self.map = [ [ 0 for i in range(n) ] for j in range(n) ]
		self.wumpus = w
		self.size = n
		self.map = []                      
		for i in range (0, n): 
			new = [] 
			for j in range (0, n):
				new.append(Block("empty"))
			self.map.append(new) 
		"""
		# fill edges with blocks
		for i in range(self.size):
			#t = 
			self.map[0][i] = Block("wall")
			self.map[self.size-1][i] = Block("wall")
			self.map[i][0] = Block("wall")
			self.map[i][self.size-1] = Block("wall")
		"""
		for i in range(self.size):
			#t = 
			self.map[0][i] = Block("wall")
			self.map[self.size-1][i] = Block("wall")
			self.map[i][0] = Block("wall")
			self.map[i][self.size-1] = Block("wall")
		
	def update(self):
		# percept elns
		print "lol"
	
	def draw(self):
		for i in range(self.size):
			for j in range(self.size):
				t=self.map[i][j]
				
				if t.t=="wall":
					pygame.draw.rect(window, (255, 0, 0), (i*block, j*block, block, block))
				if t.t=="empty":
					pygame.draw.rect(window, (0, 0, 255), (i*block, j*block, block, block))
				

class Wumpus():
	def __init__(self, x, y):
		self.pos_x = x
		self.pos_y = y

	def update(self, percepts):
		print "lol"

def events():
	for event in pygame.event.get(): 
		if event.type == pygame.QUIT: 
			sys.exit(0) 



# draw a line - see http://www.pygame.org/docs/ref/draw.html for more 
# pygame.draw.line(window, (255, 255, 255), (0, 0), (30, 50))

w = Wumpus(1,1)
b = Board(n, w)

#input handling (somewhat boilerplate code):
while True: 
	events()
	b.update()
	b.draw()
	#draw it to the screen
	pygame.display.flip() 

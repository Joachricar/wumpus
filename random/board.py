import pygame

##############################################
# The Board
# Contains the actual map("cave") data 
# and the wumpus status
##############################################
class Board():
	def __init__(self, n):
		self.restart(n)
	
	def restart(self, n):
		self.size = n
		self.home = n
		self.numpit = (n.x+n.y)/2
		self.numwalls = (n.x+n.y)/2
		self.createMap()
		self.goldTaken = False
		self.running = True
	
	# Create map objects
	def createMap(self):
		self.map = []
		
		for i in range (0, n.x): 
			new = [] 
			for j in range (0, n.y):
				new.append(Block("empty"))
			self.map.append(new) 
		
		self.initWalls()
		self.initPitfalls()
		self.placeOnce("wumpus")
		self.placeOnce("gold")
	
	# Create the wumpus hunter based on
	# which tiles are free
	def createHunter(self):
		self.hdir = Point(0,1)
		self.hpos = self.getRandomAvailable()
		
		return Wumpus(self.hpos.clone(), self.hdir.clone(), self.size)
	
	# Draw the map and wumpus
	def drawMap(self):
		for i in range(self.size.x):
			for j in range(self.size.y):
				t=self.map[i][j]
				if t.t=="wall":
					color=(200, 200, 200)
				if t.t=="empty":
					color=(0, 0, 0)
				elif t.t == "pit":
					color=(0, 0, 200)
				elif t.t == "wumpus":
					color=(0, 200, 0)
				elif t.t == "gold":
					color=(200, 200, 0)
				self.drawTile(i, j, color)
	def drawHunter(self):
		self.drawTile(self.hpos.x, self.hpos.y, (200, 0, 0))
	
	# Draw a tile
	# x, y 	= position
	# c 	= color
	def drawTile(self, x, y, c):
		pygame.draw.rect(window, c, (x*block, y*block, block, block))
	
	# Create walls
	# Insert randomly placed walls
	def initWalls(self):
		for i in range(self.size.x):
			self.map[0][i] = Block("wall")
			self.map[self.size.x-1][i] = Block("wall")

		for i in range(self.size.y):
			self.map[i][0] = Block("wall")
			self.map[i][self.size.y-1] = Block("wall")
		
		for i in range(self.numwalls):
			self.setTile(random.randrange(0, self.size.x), random.randrange(0, self.size.y), "wall")
	
	# Randomly place pitfalls on the map
	def initPitfalls(self):
		for i in range(self.numpit):
			self.setTile(random.randrange(0, self.size.x), random.randrange(0, self.size.y), "pit")
	
	# Set the type of a tile
	# x, y		= position
	# t			= type
	# override	= override tile if not empty
	def setTile(self, x, y, t, override = False):
		if override:
			self.map[x][y].t = t
			return True
		elif self.map[x][y].t =="empty":
			self.map[x][y].t = t
			return True
		return False
	
	# Place a tile on first available spot
	def placeOnce(self, t):
		while True:
			if self.setTile(random.randrange(1, self.size.x), random.randrange(1,self.size.y), t):
				break
	
	# Return a list of perceptions available to the hunter
	# If the hunter bumps, it shouldn't get perception from the wall's tile
	def percept(self):
		tile = self.map[self.hpos.x][self.hpos.y]
		percepts=[]
		if tile.t == "wall":
			percepts.append("bump")
			return percepts
		if tile.t == "gold":
			percepts.append("gold")
			self.goldTaken = True
		
		for x in surr:
			tile = self.map[self.hpos.x + x.x][self.hpos.y + x.y]
			if tile.t == "emtpy" or tile.t == "gold" or tile.t == "wall":
				continue
			
			if tile.t == "wumpus":
				if "smell" in percepts:
					continue
				percepts.append("smell")
			
			elif tile.t == "pit":
				if "pit" in percepts:
					continue
				percepts.append("breeze")
		
		return percepts
	
	# Get perception from a tile
	def getPercept(self, x, y):
		tile = self.map[x][y]
		if tile.t != "empty" and tile.t != "gold" and tile.t != "wall":
			return tile.t
	
	def getRandomAvailable(self):
		while True:
			x = random.randrange(1, self.size.x)
			y = random.randrange(1, self.size.y)
			tile = self.map[x][y]
			if tile.t == "empty":
				return Point(x, y)

	def updateHunter(self, action):
		cmd = action.split(" ")
		if cmd[0] == "turn":
			if cmd[1] == "left":
				self.hdir.turnLeft()
			elif cmd[1] == "right":
				self.hdir.turnRight()
		
		elif cmd[0] == "forward":
			self.hpos.move(self.hdir)
		
		elif cmd[0] == "back":
			self.hpos.back(self.hdir)
		
		self.updateState()
	
	def updateState(self):
		tile = self.map[self.hpos.x][self.hpos.y]
		if tile.t == "wumpus":
			self.gameOver()
		elif tile.t == "pit":
			self.gameOver()
	
	def gameOver(self):
		self.running = False

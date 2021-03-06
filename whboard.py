from whblock import Block
from whpoint import Point
from whhunter import Hunter
import random

##############################################
# The Board
# Contains the actual map("cave") data 
# and the wumpus status
##############################################
class Board():
	def __init__(self, n, surr):
		self.surr = surr
		
		# Last
		self.restart(n)
		
		
	def restart(self, n):
		self.size = n
		self.wp = 0.06
		self.pp = 0.06
		
		numsq = n.x*n.y
		self.numpit = int(numsq * self.pp)
		self.numwalls = int(numsq * self.wp)
		self.createMap()
		self.goldTaken = False
		self.running = True
	
	# Create map objects
	def createMap(self):
		self.map = []
		
		for i in range (0, self.size.x): 
			new = [] 
			for j in range (0, self.size.y):
				new.append(Block("empty", i, j))
			self.map.append(new) 
		
		self.initWalls()
		self.initPitfalls()
		self.hdir = Point(0,1)
		self.hpos = self.getRandomAvailable(True)
		self.home = self.hpos.clone()
		self.clearHome()
		self.placeOnce("wumpus")
		self.placeOnce("gold")
	
	# Create the wumpus hunter based on
	# which tiles are free
	def createHunter(self):
		return Hunter(self.hpos.clone(), self.hdir.clone(), self.size, self.surr)
	
	def clearHome(self):
		t = self.home
		self.map[t.x+1][t.y].t = "empty"
		self.map[t.x-1][t.y].t = "empty"
		self.map[t.x+1][t.y+1].t = "empty"
		self.map[t.x+1][t.y-1].t = "empty"
		self.map[t.x-1][t.y+1].t = "empty"
		self.map[t.x-1][t.y-1].t = "empty"
		self.map[t.x][t.y+1].t = "empty"
		self.map[t.x][t.y-1].t = "empty"
		self.map[t.x][t.y].t = "empty"
		
	def drawHunter(self):
		self.drawTile(self.hpos.x, self.hpos.y, (200, 0, 0))
	def drawHome(self):
		self.drawTile(self.home.x, self.home.y, (200, 0, 200))
	
	# Draw a tile
	# x, y 	= position
	# c 	= color
	def drawTile(self, x, y, c):
		pygame.draw.rect(window, c, (x*block, y*block, block, block))
	
	# Create walls
	# Insert randomly placed walls
	def initWalls(self):
		for i in range(self.size.x):
			self.map[0][i] = Block("wall", 0, i)
			self.map[self.size.x-1][i] = Block("wall", self.size.x-1, i)

		for i in range(self.size.y):
			self.map[i][0] = Block("wall", i, 0)
			self.map[i][self.size.y-1] = Block("wall", i, self.size.y-1)
		
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
		
		for x in self.surr:
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
		return None
	
	def getRandomAvailable(self, safety=False):
		while True:
			x = random.randrange(1, self.size.x)
			y = random.randrange(1, self.size.y)
			tile = self.map[x][y]
			if tile.t == "empty":
				if safety:
					safe = True
					for i in self.surr:
						tr = self.getPercept(tile.p.x+i.x, tile.p.y+i.y)
						if tr != None:
							safe = False
					if safe:
						return Point(x, y)
				else:
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
		
		elif cmd[0] == "grab":
			if self.map[self.hpos.x][self.hpos.y].t == "gold":
				self.goldTaken = True
			self.map[self.hpos.x][self.hpos.y].t = "empty"
			
		
		elif cmd[0] == "climb":
			if self.hpos.x == self.home.x and self.hpos.y == self.hpos.y:
				self.running = False
		
		self.updateState()
	
	def updateState(self):
		tile = self.map[self.hpos.x][self.hpos.y]
		if tile.t == "wumpus":
			self.gameOver()
		elif tile.t == "pit":
			self.gameOver()
	
	def gameOver(self):
		self.running = False
	


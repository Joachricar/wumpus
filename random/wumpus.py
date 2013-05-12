# TODO:
# * Create map for "hunter"
# 	* Explore tiles
#	* Set tile-safety
# * Add references to tile

import sys
#import and init pygame
import pygame
import random
import time
from point import Point
pygame.init()

wp = 0.06
pp = 0.06
##############################################
# Block
# t = type
# e = explored
##############################################
class Block():
	def __init__(self, t):
		self.t = t
		self.references = 0
		self.e = False
	
	def setType(self, t):
		if self.t == "wall":
			return
		
		if self.t == "empty" and t == "wall":
			self.t = "wall"
		
		elif self.t == "empty":
			return
		else:
			self.t = t
	
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
		
		numsq = n.x*n.y
		self.numpit = int(numsq * pp)
		self.numwalls = int(numsq * wp)
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
		self.home = self.hpos.clone()
		return Wumpus(self.hpos.clone(), self.hdir.clone(), self.size)

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
		
		elif cmd[0] == "grab":
			self.map[self.hpos.x][self.hpos.y].t = "empty"
		
		elif cmd[0] == "climb":
			if self.hpos.x == self.home.x and self.hpos.y == self.hpos.y:
				self.running = False
				self.goldTaken = True
		
		
		self.updateState()
	
	def updateState(self):
		tile = self.map[self.hpos.x][self.hpos.y]
		if tile.t == "wumpus":
			self.gameOver()
		elif tile.t == "pit":
			self.gameOver()
	
	def gameOver(self):
		self.running = False
	

##############################################
# Wumpus-class
# Should keep a map of what's discovered and 
# do actions upon perceptions from the "board"
##############################################
class Wumpus():
	def __init__(self, hpos, hdir, size):
		self.home = hpos.clone()
		self.hpos = hpos
		self.hdir = hdir
		self.size = size
		self.hasGold = False
		self.shots = 1
		self.path = []
		self.map = []
		self.initMap()
	
	# Set all blocks to unkown
	# except the border which are walls
	def initMap(self):
		for i in range (0, self.size.x): 
			new = [] 
			for j in range (0, self.size.y):
				new.append(Block("unknown"))
			self.map.append(new) 
			
		for i in range(self.size.x):
			self.map[0][i] = Block("wall")
			self.map[self.size.x-1][i] = Block("wall")

		for i in range(self.size.y):
			self.map[i][0] = Block("wall")
			self.map[i][self.size.y-1] = Block("wall")
	
	# Do actions based on perceptions picked up from the environment
	# If there's nothing percepted, it means all surrounding squares are safe(no wumpus or pits)
	# If a bump is percepted, the square in front is a wall
	# If gold is percepted, the current square contains gold.
	# If we're following a path, continue following it. A path should always be safe.
	# When all perceptions has been "analyzed", find the nearest undiscovered square and move towards it
	def update(self, percepts):
		self.map[self.hpos.x][self.hpos.y].e = True
		
		if not percepts:
			self.setSurroundings("empty")
		
		if self.hasGold:
			if self.hpos.x == self.home.x and self.hpos.y == self.home.y:
				return "climb"
		
		if self.path:
			return self.followPath()
		
		if "bump" in percepts:
			self.setTile("wall")
			self.hpos.back(self.hdir)
			return "back"
		
		if "gold" in percepts:
			self.goHome()
			self.hasGold = True
			return "grab"

		if "breeze" in percepts:
			self.setSurroundings("pit")
			
		if "smell" in percepts:
			self.setSurroundings("wumpus")
		
		next = self.hpos.clone()
		next.move(self.hdir)
		if self.isSafe(next.x, next.y):
			x = random.randrange(0,5)
			if x == 0:
				self.hdir.turnLeft()
				return "turn left"
			if x == 1:
				self.hdir.turnRight()
				return "turn right"
			if x >= 2:
				self.hpos.move(self.hdir)
				return "forward"
		else:
			x = random.randrange(0,2)
			if x == 0:
				self.hdir.turnLeft()
				return "turn left"
			if x == 1:
				self.hdir.turnRight()
				return "turn right"
	
	def goHome(self):
		print "EG GJENG HEIM!"
		
	# Check if a square is safe
	# A square is safe if it is empty
	# Why?
	# Because when the hunter percept nothing, all surrounding squares are marked as empty.
	# If it percept something, they're not. So the surrounding squares of the hunter will never be unknown.
	def isSafe(self, x, y):
		tile = self.map[x][y]
		if tile.t == "empty":
			return True
		else:
			return False
	
	# Move towards the next square in the path.
	# Should return 
	def followPath(self):
		print "PATH"
		
	def setTile(self, t):
		self.map[self.hpos.x][self.hpos.y].setType(t)
	
	def setSurroundings(self, t):
		for x in surr:
			px = self.hpos.x + x.x
			py = self.hpos.y + x.y
			
			if px >= self.size.x or py >= self.size.y or px <= 0 or py <= 0:
				continue
			
			tile = self.map[px][py]
			tile.setType(t)

	def findPath(self):
		print "lol"
	

####################################################
##### Main Program #################################
####################################################

# Surrounding blocks
surr = [Point(0,1), Point(1,0), Point(0, -1), Point(-1,0)]

#create the screen
block = 5 # blocksize = 10px
n = Point(160,160) # 40x40 map
window = pygame.display.set_mode((block*n.x, block*n.y)) 

b = Board(n)
w = b.createHunter()

myfont = pygame.font.SysFont("Arial", 30)
# apply it to text on a label
gameWon = myfont.render("YAAAAY!!!1", 1, (255, 255, 0))
gameOver = myfont.render("Game Over!", 1, (255, 255, 0))
drawHunterMap = True

def drawTile(x, y, c):
	pygame.draw.rect(window, c, (x*block, y*block, block, block))

def drawMap(src):
	mp = src.map
	
	for i in range(n.x):
		for j in range(n.y):
			t=mp[i][j]
			if t.t=="wall":
				color=(100, 100, 100)
			if t.t=="empty":
				color=(255, 255, 255)
			elif t.t == "pit":
				color=(100, 100, 255)
			elif t.t == "wumpus":
				color=(255, 100, 100)
			elif t.t == "gold":
				color=(255, 255, 0)
			elif t.t == "unknown":
				color=(0,0,0)
				
			drawTile(i, j, color)
			

# Poll events from pygame
def events():
	global b
	global w
	global drawHunterMap
	for event in pygame.event.get(): 
		if event.type == pygame.QUIT: 
			sys.exit(0)
		keys = pygame.key.get_pressed()
		if keys[pygame.K_RETURN]:
			if b.running == False:
				b.restart(n)
				w = b.createHunter()
		if keys[pygame.K_r]:
			b.restart(n)
			w = b.createHunter()
		if keys[pygame.K_e]:
			drawHunterMap = not drawHunterMap

while True:
	events()
	
	if drawHunterMap:
		drawMap(w)
	else:
		drawMap(b)
	
	b.drawHunter()
	b.drawHome()
	
	if b.running:
		b.updateHunter(w.update(b.percept()))
	else:
		if b.goldTaken:
			window.blit(gameWon, (100, 100))
		else:
			window.blit(gameOver, (100, 100))
	
	pygame.display.flip()
	#time.sleep(0.02)
	
	

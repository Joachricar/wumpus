import sys
import pygame
import random
import time
import Queue

pygame.init()

wp = 0.06
pp = 0.06

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
		return Wumpus(self.hpos.clone(), self.hdir.clone(), self.size)
	
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
		return None
	
	def getRandomAvailable(self, safety=False):
		while True:
			x = random.randrange(1, self.size.x)
			y = random.randrange(1, self.size.y)
			tile = self.map[x][y]
			if tile.t == "empty":
				if safety:
					safe = True
					for i in surr:
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
		self.retreat = False
		self.map[self.hpos.x][self.hpos.y].e = True
		self.setSurroundings("empty")
	
	# Set all blocks to unkown
	# except the border which are walls
	def initMap(self):
		for i in range (0, self.size.x): 
			new = [] 
			for j in range (0, self.size.y):
				new.append(Block("unknown", i, j))
			self.map.append(new) 
			
		for i in range(self.size.x):
			self.map[0][i] = Block("wall", 0, i)
			self.map[self.size.x-1][i] = Block("wall", self.size.x-1, i)

		for i in range(self.size.y):
			self.map[i][0] = Block("wall", i, 0)
			self.map[i][self.size.y-1] = Block("wall", i, self.size.y-1)
	
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
		
		if self.path:
			return self.followPath()
		
		if self.retreat:
			if self.hpos.x == self.home.x and self.hpos.y == self.home.y:
				return "climb"
		
		if self.hasGold:
			if self.hpos.x == self.home.x and self.hpos.y == self.home.y:
				return "climb"
		
		if "bump" in percepts:
			self.setTile("wall")
			self.hpos.back(self.hdir)
			return "back"
		
		if "gold" in percepts:
			self.hasGold = True
			print "Found gold!"
			self.path = self.findPath(self.home)
			if self.path:
				self.path.pop(0)
			return "grab"

		if "breeze" in percepts:
			self.setSurroundings("pit")
			
		if "smell" in percepts:
			self.setSurroundings("wumpus")
		
		self.path = self.findPath()
		
		if self.path:
			self.path.pop(0)
		else:
			self.retreat = True
			self.goHome()
		return self.followPath()
		
	def goHome(self):
		self.path = self.findPath(self.home)
		if self.path:
			self.path.pop(0)
		
	# Check if a square is safe
	# A square is safe if it is empty
	# Why?
	# Because when the hunter percept nothing, all surrounding squares are marked as empty.
	# If it percept something, they're not. So the surrounding squares of the hunter will never be unknown.
	def isSafe(self, x, y):
		tile = self.map[x][y]
		
		if tile.t == "empty":
			return True
		elif tile.t == "unknown":
			return True
		elif not tile.t == "pit" or not tile.t == "wumpus" or not tile.t == "wall":
			return False
		else:
			return False
	
	# Move towards the next square in the path.
	# Should return 
	def followPath(self):
		if not self.path:
			return "grab"
		
		next = self.path[0]
		
		nnx = (next.x - self.hpos.x)
		nny = (next.y - self.hpos.y)
		
		#nnx = (self.hpos.x - next.x)
		#nny = (self.hpos.y - next.y)
		
		direction = Point(nnx, nny)
		
		if direction.x == self.hdir.x and direction.y == self.hdir.y:
			self.path.pop(0)
			return self.forward()
		else:
		# WARNING: NASTY CODE!!!!!!!!!!!!!!!!!
			if direction.x == -1:
				if self.hdir.y == -1:
					return self.turnLeft()
				if self.hdir.y == 1:
					return self.turnRight()
			
			if direction.x == 1:
				if self.hdir.y == -1:
					return self.turnRight()
				if self.hdir.y == 1:
					return self.turnLeft()
			
			if direction.y == -1:
				if self.hdir.x == -1:
					return self.turnRight()
				if self.hdir.x == 1:
					return self.turnLeft()
			
			if direction.y == 1:
				if self.hdir.x == -1:
					return self.turnLeft()
				if self.hdir.x == 1:
					return self.turnRight()
		
		return self.turnLeft()
		
	def turnLeft(self):
		self.hdir.turnLeft()
		return "turn left"
	def turnRight(self):
		self.hdir.turnRight()
		return "turn right"
	def forward(self):
		self.hpos.move(self.hdir)
		return "forward"
	
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
	
	# find path to next undiscovered and safe square
	def findPath(self, target = None):
		q = []
		visited = [False for x in range(self.size.x * self.size.y)]
		paths = [[]]*(self.size.x * self.size.y)
		
		#print self.hpos.x, " ", self.hpos.y
		#print self.hdir.x, " ", self.hdir.y
		
		q.append(self.hpos)
		paths[self.size.x*self.hpos.y + self.hpos.x].append(self.hpos)
		
		ret = -2
		count = 0
		while q:
			count += 1
			asd = q.pop(0)
			temp = self.runBFS(asd, visited, q, paths, target)
			
			if temp > -1:
				ret = temp
				break
		
		if ret < 0:
			return None
		
		return paths[ret]
	
	# do that bfs thang
	def runBFS(self, current, visited, q, paths, target = None):
		
		t = self.map[current.x][current.y]
		c = current.y * self.size.x + current.x
		if visited[c]:
			return -1
		elif (target == None and not t.e) or (target != None and target.x == current.x and target.y == current.y):
			return c
		else:
			visited[c] = True
			for neigh in self.getUndiscoveredOrSafeNeighbours(current.x, current.y):
				path = paths[(self.size.x * neigh.y) + neigh.x]
				path = []
				path.extend(paths[current.x+(self.size.x*current.y)])
				path.append(neigh)
				paths[neigh.y*self.size.x+neigh.x] = path
				q.append(neigh)
		return -1
				
	# get all adjacent neighbours which are safe or undiscovered
	def getUndiscoveredOrSafeNeighbours(self, x, y):
		lst = []
		for s in surr:
			tile = self.map[x+s.x][y+s.y]
			if tile.isSafe():
				lst.append(tile.p)
		
		return lst

####################################################
##### Main Program #################################
####################################################

# Surrounding blocks
surr = [Point(0,1), Point(1,0), Point(0, -1), Point(-1,0)]

#create the screen
block = 3 # blocksize = 10px
n = Point(300,300) # 40x40 map
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

def drawHunter(src):
	drawTile(src.hpos.x, src.hpos.y, (0, 255, 0))

def drawHome(src):
	drawTile(src.home.x, src.home.y, (255, 0, 255))
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

def rotate(l,n):
    return l[n:] + l[:n]

def drawPath(w):
	if not w.path:
		return
	for x in w.path:
		drawTile(x.x, x.y, (255, 0, 0))
	

wins = 0
loss = 0	
while True:
	events()
	
	#print w.hpos.x, " ", w.hpos.y
	
	if drawHunterMap:
		drawMap(w)
	else:
		drawMap(b)
	
	drawHunter(b)
	drawHome(b)
	drawPath(w)
	if b.running:
		perc = b.percept()
		action = w.update(perc)
		b.updateHunter(action)
	else:
		global b
		global w
		if b.goldTaken:
			window.blit(gameWon, (100, 100))
			wins += 1
		else:
			window.blit(gameOver, (100, 100))
			loss += 1
		print wins, "/", (loss+wins)
		time.sleep(4)
		b.restart(n)
		w = b.createHunter()
	
	pygame.display.flip()
	rotate(surr, 1)
	#time.sleep(0.02)

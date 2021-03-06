from whpoint import Point
from whblock import Block
##############################################
# Wumpus-class
# Should keep a map of what's discovered and 
# do actions upon perceptions from the "board"
##############################################
class Hunter():
	def __init__(self, hpos, hdir, size, surr):
		self.surr = surr
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
		for x in self.surr:
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
		for s in self.surr:
			tile = self.map[x+s.x][y+s.y]
			if tile.isSafe():
				lst.append(tile.p)
		
		return lst

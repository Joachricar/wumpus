import sys
import pygame
import time
import Queue
import threading
from whboard import Board
from whblock import Block
from whpoint import Point

pygame.init()

class WHServer(threading.Thread):
	def init(self, window, b, w, block, n):
		self.window = window
		self.b = b
		self.w = w
		self.block = block
		self.n = n
		
  	def run(self):
  		global count
  		last = int(round(time.time() * 1000))
  		while True:
			if drawHunterMap:
				drawMap2(w)
			else:
				drawMap2(b)

			drawHunter(b)
			drawHome(b)
			drawPath(w)
			
			millis = int(round(time.time() * 1000))
			a = (count/(((millis-last)/1000)+1))
			count = 0
			last = millis
			s = "mps " + str(a)
			mps = myfont.render(s, 1, (255, 255, 0))
			window.blit(mps, (10, 10))
			pygame.display.flip()
####################################################
##### Main Program #################################
####################################################

# Surrounding blocks
surr = [Point(0,1), Point(1,0), Point(0, -1), Point(-1,0)]

#create the screen
block = 2 # blocksize = 10px
n = Point(500,500) # 40x40 map
window = pygame.display.set_mode((block*n.x, block*n.y)) 

b = Board(n, surr)
w = b.createHunter()

myfont = pygame.font.SysFont("Arial", 30)
# apply it to text on a label
gameWon = myfont.render("YAAAAY!!!1", 1, (255, 255, 0))
gameOver = myfont.render("Game Over!", 1, (255, 255, 0))
drawHunterMap = True
display = True

def drawTile(x, y, c):
	pygame.draw.rect(window, c, (x*block, y*block, block, block))

def drawMap(src):
	mp = src.map
	
	# draw background
	#pygame.draw.rect(window, (255,255,255), (0,0,n.x*block, n.y*block))
	for i in range(n.x):
		for j in range(n.y):
			t=mp[i][j]
			if t.t=="wall":
				color=(100, 100, 100)
			elif t.t == "empty":
				color=(255,255,255)
			elif t.t == "pit":
				color=(0, 0, 255)
			elif t.t == "wumpus":
				color=(255, 100, 100)
			elif t.t == "gold":
				color=(255, 255, 0)
			elif t.t == "unknown":
				color=(0,0,0)
				
			drawTile(i, j, color)

def drawMap2(src):
	mp = src.map
	
	# draw background
	pygame.draw.rect(window, (255,255,255), (0,0,n.x*block, n.y*block))
	for i in range(n.x):
		
		count = 0
		for j in range(n.y):
			color = None
			t=mp[i][j]
			
			if t.t == "empty":
				if count > 0:
					start = j-count
					pygame.draw.rect(window, (0,0,0), (i*block,start*block,block,(count)*block))
					count = 0
				continue
			elif t.t == "unknown":
				count += 1
				continue
			elif t.t=="wall":
				color=(100, 100, 100)
			elif t.t == "pit":
				color=(0, 0, 255)
			elif t.t == "wumpus":
				color=(255, 100, 100)
			elif t.t == "gold":
				color=(255, 255, 0)
			else:
				print t.t
				continue
			
			if color != (0,0,0):
				if count > 0:
					start = j-count
					pygame.draw.rect(window, (0,0,0), (i*block,start*block,block,(count)*block))
					count = 0
				drawTile(i,j,color)

def drawHunter(src):
	drawTile(src.hpos.x, src.hpos.y, (0, 255, 0))

def drawHome(src):
	drawTile(src.home.x, src.home.y, (255, 0, 255))
# Poll events from pygame
def events():
	global b
	global w
	global drawHunterMap
	global display
	
	for event in pygame.event.get(): 
		if event.type == pygame.QUIT:
			drawer.stop()
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
		if keys[pygame.K_d]:
			display = not display

def rotate(l,n):
    return l[n:] + l[:n]

def drawPath(w):
	if not w.path:
		return
	for x in w.path:
		drawTile(x.x, x.y, (255, 0, 0))
	

wins = 0
loss = 0

drawer = WHServer()
drawer.init(window, b, w, block, n)
drawer.start()

count = 0

while True:
	events()
	
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
	
	#rotate(surr, 1)
	#time.sleep(0.1)
	count += 1

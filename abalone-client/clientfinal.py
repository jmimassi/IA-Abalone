import socket 
from threading import Thread
import sys
import random
import copy
import time
from math import sqrt
symbols = ['B', 'W']
from collections import defaultdict
import socket as s
import json
import time
#################### GAME.PY


class GameWin(Exception):
	def __init__(self, winner, lastState):
		self.__winner = winner
		self.__state = lastState

	@property
	def winner(self):
		return self.__winner

	@property
	def state(self):
		return self.__state

	def __str__(self):
		return '{} win the game'.format(self.winner)

class BadMove(Exception):
	pass

class GameDraw(Exception):
	def __init__(self, lastState):
		self.__state = lastState

	@property
	def state(self):
		return self.__state

class BadGameInit(Exception):
	pass



#################### JSON NETWORK


class NotAJSONObject(Exception):
	pass

class Timeout(Exception):
	pass

def sendJSON(socket, obj):
	message = json.dumps(obj)
	if message[0] != '{':
		raise NotAJSONObject('sendJSON support only JSON Object Type')
	message = message.encode('utf8')
	total = 0
	while total < len(message):
		sent = socket.send(message[total:])
		total += sent

def receiveJSON(socket, timeout = 1):
	finished = False
	message = ''
	data = ''
	start = time.time()
	while not finished:
		message += socket.recv(4096).decode('utf8')
		if len(message) > 0 and message[0] != '{':
			raise NotAJSONObject('Received message is not a JSON Object')
		try:
			data = json.loads(message)
			finished = True
		except json.JSONDecodeError:
			if time.time() - start > timeout:
				raise Timeout()
	return data

def fetch(address, data, timeout=1):
	'''
		Request response from address. Data is included in the request
	'''
	socket = s.socket()
	socket.connect(address)
	sendJSON(socket, data)
	response = receiveJSON(socket, timeout)
	return response

##################### IA





directions = {			#
	'NE': (-1,  0),
	'SW': ( 1,  0),
	'NW': (-1, -1),
	'SE': ( 1,  1),
	 'E': ( 0,  1),
	 'W': ( 0, -1)
}

opposite = {
	'NE': 'SW',
	'SW': 'NE',
	'NW': 'SE',
	'SE': 'NW',
	'E': 'W',
	'W': 'E'
}

def getDirectionName(directionTuple): 
	for dirName in directions:
		if directionTuple == directions[dirName]:
			return dirName
	raise BadMove('{} is not a direction'.format(directionTuple))

def computeAlignement(marbles): #sert à determiner la direction d'une train de marbre 
	marbles = sorted(marbles, key=lambda L: L[0]*9+L[1])
	D = set()
	for i in range(len(marbles)-1):
		direction = (marbles[i+1][0]-marbles[i][0], marbles[i+1][1]-marbles[i][1])
		if direction not in directions.values():
			return None
		D.add(direction)
	return getDirectionName(D.pop()) if len(D) == 1 else None



def checkMarbles(state, move):
	marbles = move['marbles']
	color = symbols[state['current']]
	if not 0 <= len(marbles) < 4:
		raise BadMove('You can only move 1, 2, or 3 marbles')

	for pos in marbles:
		if getColor(state, pos) != color:
			raise BadMove('Marble {} is not yours'.format(pos))
		
def isOnBoard(pos):
	l, c = pos
	if min(pos) < 0:
		return False
	if max(pos) > 8:
		return False
	if abs(c-l) >= 5:
		return False
	return True

def addDirection(pos, direction):
	D = directions[direction]
	return (pos[0] + D[0], pos[1] + D[1])

def moveOneMarble(state, pos, direction):
	li, ci = pos
	ld, cd = addDirection(pos, direction)
	color = getColor(state, pos)
	try:
		destStatus = getStatus(state, (ld, cd))
	except:
		destStatus = 'X'
	
	if color != 'W' and color != 'B':
		raise BadMove('There is no marble here {}'.format(pos))
	if destStatus == 'W' or destStatus == 'B':
		raise BadMove('There is already a marble here {}'.format((ld, cd)))
	
	res = copy.copy(state)
	res['board'] = copy.copy(res['board'])
	res['board'][li] = copy.copy(res['board'][li])
	res['board'][li][ci] = 'E'

	if destStatus == 'E':
		res['board'][ld] = copy.copy(res['board'][ld])
		res['board'][ld][cd] = color

	return res

def opponent(color):
	if color == 'W':
		return 'B'
	return 'W'

def getStatus(state, pos):
	if not isOnBoard(pos):
		raise BadMove('The position {} is outside the board'.format(pos))
	return state['board'][pos[0]][pos[1]]

def isEmpty(state, pos):
	return getStatus(state, pos) == 'E'

def isFree(state, pos):
	if isOnBoard(pos):
		return isEmpty(state, pos)
	else:
		return True

def getColor(state, pos):
	status = getStatus(state, pos)
	if status == 'W' or status == 'B':
		return status
	raise BadMove('There is no marble here {}'.format(pos))

def moveMarblesTrain(state, marbles, direction):
	if direction in ['E', 'SE', 'SW']:
		marbles = sorted(marbles, key=lambda L: -(L[0]*9+L[1]))
	else:
		marbles = sorted(marbles, key=lambda L: L[0]*9+L[1])

	color = getColor(state, marbles[0])

	pos = addDirection(marbles[0], direction)
	toPush = []
	while not isFree(state, pos):
		if getColor(state, pos) == color:
			raise BadMove('You can\'t push your own marble')
		toPush.append(pos)
		pos = addDirection(pos, direction)

	if len(toPush) >= len(marbles):
		raise BadMove('you can\'t push {} opponent\'s marbles with {} marbles {}'.format((toPush), (marbles),(direction)))

	state = moveMarbles(state, list(reversed(toPush)) + marbles, direction)

	return state

def moveMarbles(state, marbles, direction):
	for pos in marbles:
		state = moveOneMarble(state, pos, direction)
	return state

def sameLine(direction1, direction2):
	if direction1 == direction2:
		return True
	if direction1 == opposite[direction2]:
		return True
	return False

def isWinning(state):
	toCount = opponent(symbols[state['current']])
	count = 0
	for line in state['board']:
		for case in line:
			if case == toCount:
				count += 1
	return count < 9



def Abalone(players):
	if len(players) != 2:
		raise BadGameInit('Tic Tac Toe must be played by 2 players')

	state = {
		'players': players,
		'current': 0,
		'board': [
			['W', 'W', 'W', 'W', 'W', 'X', 'X', 'X', 'X'],
			['W', 'W', 'W', 'W', 'W', 'W', 'X', 'X', 'X'],
			['E', 'E', 'W', 'W', 'W', 'E', 'E', 'X', 'X'],
			['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'X'],
			['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E'],
			['X', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E'],
			['X', 'X', 'E', 'E', 'B', 'B', 'B', 'E', 'E'],
			['X', 'X', 'X', 'B', 'B', 'B', 'B', 'B', 'B'],
			['X', 'X', 'X', 'X', 'B', 'B', 'B', 'B', 'B']
		]
	}

	def next(state, move):
		if move is None:
			raise BadMove('None is not a valid move')

		checkMarbles(state, move)
		marbles = move['marbles']

		if len(marbles) != 0:
			marblesDir = computeAlignement(marbles)
			if marblesDir is None and len(marbles) > 1:
				raise BadMove('The marbles you want to move must be aligned')

			if len(marbles) == 1:
				state = moveOneMarble(state, marbles[0], move['direction'])
			elif sameLine(move['direction'], marblesDir):
				state = moveMarblesTrain(state, marbles, move['direction'])
			else:
				state = moveMarbles(state, marbles, move['direction'])

			if isWinning(state):
				raise GameWin(state['current'], state)
		
		state['current'] = (state['current'] + 1) % 2
		return state

	return state, next






def IsMovePossible(state, pos, direction):	#sert à savoir si le move du marbre donné est possible dans la direction donnée
	li, ci = pos
	ld, cd = addDirection(pos, direction)
	try :
		color = getColor(state, pos)
	except : 
		color = 'None'
	try:
		destStatus = getStatus(state, (ld, cd))
	except:
		destStatus = 'X'
	
	if color != 'W' and color != 'B':
		return state['board'], False
	if destStatus == 'W' or destStatus == 'B':
		return state['board'], False
	if destStatus == 'X':
		return state['board'], False

	
	res = copy.copy(state)
	res['board'] = copy.copy(res['board'])
	res['board'][li] = copy.copy(res['board'][li])
	res['board'][li][ci] = 'E'

	

	if destStatus == 'E':
		res['board'][ld] = copy.copy(res['board'][ld])
		res['board'][ld][cd] = color

	return res, True



def PossibleMoves(state,marble):	#répertorie tout les moves possibles pour le marbre donné en fonction du tableau du jeu
	possiblemoves = []
	dir = ['NE','SW','NW','SE','E','W']
	i = 0
	while i < 6 :
		board, poss = IsMovePossible(state,marble,dir[i])
		if poss == True :
				possiblemoves.append(dir[i])
				i += 1
		else :
			i+= 1
	return possiblemoves





def posofmarbles(board):	#détermmine la position des marbres
	whites = []
	blacks = []
	i = 0
	lines = 0
	for line in board :
		i = 0
		for elem in line :
			if elem == 'W':
				whites.append([lines,i])
			if elem == 'B':
				blacks.append([lines,i])
			else : 
				pass
			i += 1
		lines += 1
	return whites, blacks




def allMarbleTrains(board):	#détermine tout les trains de marbres et renvoie leur positions
	blancs, noirs = posofmarbles(board)
	trainsblancst2 = []
	trainsblancst3 = []
	trainsnoirst2 = []
	trainsnoirst3 = []
	for elem in blancs :
		i = 0
		while i < len(blancs): 
			if computeAlignement([elem,blancs[i]]) != None and elem != blancs[i]:
				trainsblancst2.append([elem,blancs[i]])
			i += 1
	
	for elem in trainsblancst2 :
		j = 0 
		while j < len(blancs): 
			if computeAlignement(elem+[blancs[j]]) != None and elem != blancs[j]:
				trainsblancst3.append(elem+[blancs[j]])
			j += 1

	for elem in noirs :
		i = 0
		while i < len(noirs): 
			if computeAlignement([elem,noirs[i]]) != None and elem != noirs[i]:
				trainsnoirst2.append([elem,noirs[i]])
			i += 1
	for elem in trainsnoirst2 :
		j = 0 
		while j < len(noirs): 
			if computeAlignement(elem+[noirs[j]]) != None and elem != noirs[j]:
				trainsnoirst3.append(elem+[noirs[j]])
			j += 1


	return trainsblancst3 + trainsblancst2, trainsnoirst3 + trainsnoirst2






def IsMovePossiblebis(state, marbles, direction):	#vérifie si le mouvement du train de marbre donné est possible dans la direction donnée
	if direction in ['E', 'SE', 'SW']:
		marbles = sorted(marbles, key=lambda L: -(L[0]*9+L[1]))
	else:
		marbles = sorted(marbles, key=lambda L: L[0]*9+L[1])
	color = getColor(state, marbles[0])
	li1, ci1 = marbles[0]
	li2, ci2 = marbles[1]
	ld1, cd1 = addDirection(marbles[0],direction)
	ld2, cd2 = addDirection(marbles[1],direction)
	try :
		li3, ci3 = marbles[2]
		ld3, cd3 = addDirection(marbles[2],direction)
	except : 
		pass
	try : 
		dest2 = getStatus(state,list(addDirection(marbles[1],direction)))
	except BadMove :
		dest2 = 'X'
	try : 
		dest1 = getStatus(state,list(addDirection(marbles[0],direction)))
	except BadMove :
		dest1 = 'X'
	try : 
		dest3 = getStatus(state,list(addDirection(marbles[2],direction)))
	except BadMove :
		dest3 = 'X'
	except IndexError :
		pass
	# print(marbles,computeAlignement(marbles),direction)
	if dest1 == 'X':
		return state['board'], 'A'
	if  dest1 == 'W' and str(computeAlignement(marbles)) != str(direction) and str(computeAlignement(marbles)) != str(opposite[direction]) : 
		return state['board'], 'B'
	if dest1 == 'B' and str(computeAlignement(marbles)) != str(direction) and str(computeAlignement(marbles)) != str(opposite[direction]) :
		return state['board'], 'C'
	
	if dest2 == 'X':
		return state['board'], 'D'
	# print(dest1)
	if  dest2 == 'W' and (li1,ci1) != (ld2,cd2) :
		return state['board'], 'E'
	if  dest2 == 'B' and (li1,ci1) != (ld2,cd2)  :
		return state['board'], 'f'
	try :
		if  dest3 == 'W' and (li2,ci2) != (ld3,cd3) :
			return state['board'], False
	except : 
		pass
	try :
		if  dest3 == 'B' and (li2,ci2) != (ld3,cd3)  :
			return state['board'], False
	except :
		pass
	try : 
		if dest3 == 'X' :
			return state['board'], False
	except : 
		pass
	


	pos = addDirection(marbles[0], direction)
	toPush = []
	while not isFree(state, pos):
		if getColor(state, pos) == color:
			return state['board'], False
		toPush.append(pos)
		pos = addDirection(pos, direction)

	if len(toPush) >= len(marbles):
		return state['board'], False
	
	state = moveMarbles(state, list(reversed(toPush)) + marbles, direction)

	return state, True





def PossibleMovesBis(state,marble):	#vérifie tout les coups possibles pour un train de marbre donné
	possiblemoves = []
	dir = ['NE','SW','NW','SE','E','W']
	i = 0
	while i < 6 :
		board, poss = IsMovePossiblebis(state,marble,dir[i])
		if poss == True :
				possiblemoves.append(dir[i])
				i += 1
		else :
			i+= 1
	return possiblemoves



def allWhiteMoves(state):	#donne tout les coups possibles pour le joueur blanc
	white , _ = allMarbleTrains(state['board'])
	white2 , _ = posofmarbles(state['board'])
	allWmoves = []
	for elem in white :
		if computeAlignement(elem) in ['E', 'SE', 'SW']:
			elem = sorted(elem, key=lambda L: -(L[0]*9+L[1]))
		else:
			elem = sorted(elem, key=lambda L: L[0]*9+L[1])
		for dirt in PossibleMovesBis(state,elem):
			allWmoves.append([elem,dirt])
	for elem in white2 :
		for dir in PossibleMoves(state,elem) :
			allWmoves.append([[elem],dir])
	return allWmoves

def allBlackMoves(state):	#donne tout les coups possibles pour le joueur noir
	_ , black = allMarbleTrains(state['board'])
	_ , black2 = posofmarbles(state['board'])
	allBmoves = []
	for elem in black :
		if computeAlignement(elem) in ['E', 'SE', 'SW']:
			elem = sorted(elem, key=lambda L: -(L[0]*9+L[1]))
		else:
			elem = sorted(elem, key=lambda L: L[0]*9+L[1])
		for dirt in PossibleMovesBis(state,elem):
			allBmoves.append([elem,dirt])
	for elem in black2 :
		for dir in PossibleMoves(state,elem) :
			allBmoves.append([[elem],dir])
	return allBmoves



def randomWhiteMove(state) :	#renvoie un move aléatoire pour le joueur blanc, cette fonction a un but de test 
	moves = allWhiteMoves(state)
	isAmove = False
	while isAmove == False :
		move = random.choice(moves)
		if move[1] != list():
			isAmove = True

	return move

def randomBlackMove(state) :	#renvoie un move aléatoire pour le joueur noir, cette fonction a un but de test 
	moves = allBlackMoves(state)
	isAmove = False
	while isAmove == False :
		move = random.choice(moves)
		if move[1] != list():
			isAmove = True

	return move




def getPlayerColor(state,name = None):	#renvoie la couleur du joueur en fonction de l'état du jeu
	if state['players'][0] == name :
		return 'black'
	else : 
		return 'white'
	


def apply(state,move):	#fonction permettant de ne pas avoir à utiliser différentes fonction suivant si l'on bouge un ou plusieurs marbres
	if len(move[0]) == 1:
		return moveOneMarble(state,move[0][0],move[1])
	else : 
		return moveMarblesTrain(state,move[0],move[1])

def gameOver(state):	#détermine si le jeu est fini, avec un gagnant, on ne prend pas encore compte le match nul 
	whites, blacks = posofmarbles(state['board'])
	if len(whites) <= 8 :
		return True, 'black'
	if len(blacks) <= 8 :
		return True, 'white'
	else :
		return False, None

def moves(state,player):	#retourne tout les coups possibles en fonction du joueur, sert à devoir éviter d'appeler 2 fonction différentes
	if player == 'black' :
		return allBlackMoves(state)
	else : 
		return allWhiteMoves(state)

def otherplayer(player) : 	#renvoie l'autre joueur
	if player == 'black' : 
		return 'white'
	if player == 'white' :
		return 'black'
	else :
		raise IndexError

def estimateBoard(state,player):
	game, winner = gameOver(state)
	if game == True and winner == player :
		return 1
	if game == False :
		return 0
	else :
		return -1
	



def timeit(fun):	#sert à chronométrer une autre fonction, a but de test principalement
	def wrapper(*args, **kwargs):
		start = time.time()
		res = fun(*args, **kwargs)
		print('Executed in {}s'.format(time.time() - start))
		return res
	return wrapper

def heurestic(state,player):	#heuristique servant ici à évaluer les différents coups en fonction de l'état de jeu après avoir fait le coup 
	game , winner = gameOver(state)
	if game :
		if winner == player :
			return 1000000
		return -1000000
	white, black = posofmarbles(state['board'])
	whites = 0
	blacks = 0
	if player == 'black':
		for elem in black :
			blacks += distancefromcenter(elem)
		return -(blacks - 100*(len(black)-len(white)))
	else : 
		for elem in white : 
			whites += distancefromcenter(elem)
		return -(whites - 100*(len(white)-len(black)))







def distancefromcenter(pion):	#renvoie la distance par rapport au centre d'un pion
	li, co = pion
	return sqrt((li-4)**2+(co-4)**2)





def negamaxfinal(state,player,timeout = 2.85):		#fonctin déterminant le meilleur coup possible de manière itérative en recherchant les coups avec la mailleure heurisique
	cache = defaultdict(lambda : 0)
	start = time.time()
	def cachedNegamaxWithPruningLimitedDepth(state, player,depth = 3, alpha = float('-inf') , beta = float('inf')):
		
		over , winner = gameOver(state)
		if depth == 0 or over:
			res = -heurestic(state,player), None, over
		else :
			theValue, theMove, theOver = float('-inf'), None, True
			possibilities = [(move, apply(state, move)) for move in moves(state,player)]
			possibilities.sort(key=lambda poss: cache[tuple(poss[1])])
			for move, successor in reversed(possibilities):
				if time.time() - start > 2.85 :
					break
				value, _ ,over = cachedNegamaxWithPruningLimitedDepth(successor,otherplayer(player), depth-1, -beta, -alpha)
				theOver = theOver and over
				if value > theValue:
					theValue, theMove = value, move
				alpha = max(alpha, theValue)
				if alpha >= beta:
					break
			res = -theValue, theMove, theOver
		cache[tuple(state)] = res[0]
		return res
	value, move = 0, None
	depth = 1
	start = time.time()
	over = False
	oldvalue = 0 
	oldmove = None
	while value > -1000000 and time.time() - start < timeout and not over :
		value, move, over = cachedNegamaxWithPruningLimitedDepth(state,player,depth)
		if (value, move) != (float('inf'),None) : 
			oldvalue = value
			oldmove = move
		depth += 1
	return oldvalue, oldmove


@timeit
def wrapperbis(*args,fun = negamaxfinal):	#fonction à but de test pour negamaxfinal
	return negamaxfinal(*args)



################### CLIENT


s = socket.socket()
s.connect(('127.0.0.1',3000))

def inscription(port = 3100, name = "195048,195178"):
	sendJSON(s,{
	"request": "subscribe",
	"port": port,
	"name": name,
	"matricules": ["12345", "67890"]
	})
	recu = receiveJSON(s)
	reponse = str(recu['response'])
	print(reponse)


def getPlayerColor(state,name = None):
	if state['players'][0] == name :
		return 'black'
	else : 
		return 'white'





def processRequest(client,address):
	'''
		Route request to request handlers
	'''
	print('a')
	print('request from')
	
	request = receiveJSON(client)
		
	if request['request'] == 'ping':
		print('ok')
		sendJSON(client,{'response':'pong'})
	elif request['request'] == 'play' :
		state = request['state']
		print('moving')
		if getPlayerColor(state,name) == 'black' :
			_, move = negamaxfinal(state,'black')
		else :
			move = randomWhiteMove(state)
		print(state)
		print(move[0])
		print(move[1])
		sendJSON(client,{
		"response": "move",
		"move": {
		"marbles": move[0],
		"direction": move[1]
		},
		"message": "I am a robot"
		}
		)
			
	else:
		raise ValueError('Unknown request \'{}\''.format(request['request']))


def listenForRequests(port = 3100 ):
	'''
		Start thread to listen to requests.
		Returns a function to stop the thread.
	'''
	running = True
	def processClients():
		with socket.socket() as s:
			s.bind(('0.0.0.0', port))
			s.settimeout(1)
			s.listen()
			print('Listen to', port)
			while running:
				try:
					client, address = s.accept()
					with client:
						processRequest(client, address)
				except socket.timeout:
					pass
	
	listenThread = Thread(target=processClients, daemon=True)
	listenThread.start()
	listenThread.join()

























if __name__ == '__main__':
	args = sys.argv[1:]
	port = 3100
	name = "195048,195178"
	for arg in args:
		if arg.startswith('-name='):
			name = str(arg[len('-name='):])
		else : 
			port = int(arg)
	inscription(port,name)
	listenForRequests(port)

import game
import random
import copy
import time

symbols = ['B', 'W']

directions = {
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
	raise game.BadMove('{} is not a direction'.format(directionTuple))

def computeAlignement(marbles):
	marbles = sorted(marbles, key=lambda L: L[0]*9+L[1])
	D = set()
	for i in range(len(marbles)-1):
		direction = (marbles[i+1][0]-marbles[i][0], marbles[i+1][1]-marbles[i][1])
		if direction not in directions.values():
			return None
		D.add(direction)
	return getDirectionName(D.pop()) if len(D) == 1 else None

# print(computeAlignement([(0,0),(1,1)]))

def checkMarbles(state, move):
	marbles = move['marbles']
	color = symbols[state['current']]
	if not 0 <= len(marbles) < 4:
		raise game.BadMove('You can only move 1, 2, or 3 marbles')

	for pos in marbles:
		if getColor(state, pos) != color:
			raise game.BadMove('Marble {} is not yours'.format(pos))
		
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
		raise game.BadMove('There is no marble here {}'.format(pos))
	if destStatus == 'W' or destStatus == 'B':
		raise game.BadMove('There is already a marble here {}'.format((ld, cd)))
	
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
		raise game.BadMove('The position {} is outside the board'.format(pos))
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
	raise game.BadMove('There is no marble here {}'.format(pos))

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
			raise game.BadMove('You can\'t push your own marble')
		toPush.append(pos)
		pos = addDirection(pos, direction)

	if len(toPush) >= len(marbles):
		raise game.BadMove('you can\'t push {} opponent\'s marbles with {} marbles {}'.format((toPush), (marbles),(direction)))

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
		raise game.BadGameInit('Tic Tac Toe must be played by 2 players')

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

	# move = {
	# 	'marbles': [],
	# 	'direction': ''
	# }

	def next(state, move):
		if move is None:
			raise game.BadMove('None is not a valid move')

		checkMarbles(state, move)
		marbles = move['marbles']

		if len(marbles) != 0:
			marblesDir = computeAlignement(marbles)
			if marblesDir is None and len(marbles) > 1:
				raise game.BadMove('The marbles you want to move must be aligned')

			if len(marbles) == 1:
				state = moveOneMarble(state, marbles[0], move['direction'])
			elif sameLine(move['direction'], marblesDir):
				state = moveMarblesTrain(state, marbles, move['direction'])
			else:
				state = moveMarbles(state, marbles, move['direction'])

			if isWinning(state):
				raise game.GameWin(state['current'], state)
		
		state['current'] = (state['current'] + 1) % 2
		return state

	return state, next

Game = Abalone

#if __name__=='__main__':
	#def show(state):
		#print('\n'.join([' '.join(line) for line in state['board']]))
		#print()

	#state, next = Abalone(['LUR', 'LRG'])

	#state['board'][3][3] = 'B'
	#state['board'][4][3] = 'W'

	#show(state)

	 #state = moveMarblesTrain(state, [(0, 3), (1, 3), (2, 3)], 'SW')
	#show(state)
	#state = moveMarblesTrain(state, [(1, 3), (2, 3), (3, 3)], 'SW')
	#show(state)
	#state = moveMarblesTrain(state, [(2, 3), (3, 3), (4, 3)], 'SW')
	#show(state)
	#state = moveMarblesTrain(state, [(3, 3), (4, 3), (5, 3)], 'SW')
	#show(state)






















def moveOneMarble2(state, pos, direction):
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



def possmoves(state,marble):
	possiblemoves = []
	dir = ['NE','SW','NW','SE','E','W']
	i = 0
	while i < 6 :
		board, poss = moveOneMarble2(state,marble,dir[i])
		if poss == True :
				possiblemoves.append(dir[i])
				i += 1
		else :
			i+= 1
	return possiblemoves







state2 = {
		'players': ['1','2'],
		'current': 0,
		'board': [
			['E', 'E', 'E', 'E', 'E', 'X', 'X', 'X', 'X'],
			['E', 'W', 'W', 'W', 'W', 'W', 'X', 'X', 'X'],
			['E', 'E', 'W', 'E', 'E', 'E', 'E', 'X', 'X'],
			['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'X'],
			['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E'],
			['X', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E'],
			['X', 'X', 'E', 'E', 'B', 'B', 'B', 'W', 'W'],
			['X', 'X', 'X', 'B', 'B', 'B', 'B', 'B', 'B'],
			['X', 'X', 'X', 'X', 'B', 'B', 'B', 'B', 'B']
		]
	}


# print(possmoves(state,(1,0)))

def posofmarbles(board):
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

# print(posofmarbles(state['board']))

# def estimateBoard(board):
# 	whites = 0
# 	blacks = 0
# 	i = 0
# 	lines = 0
# 	for line in board :
# 		i = 0
# 		for elem in line :
# 			if elem == 'W':
# 				whites += 1
# 			if elem == 'B':
# 				blacks += 1
# 			else : 
# 				pass
# 			i += 1
# 		lines += 1
# 	return int(blacks - whites)

# blancs, noirs = posofmarbles(state['board'])

# print(noirs)
# for elem in noirs :
# 	print(possmoves(state,elem))



# print(estimateBoard(state['board']))


def allMarbleTrains(board):
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


	return trainsblancst2 + trainsblancst3, trainsnoirst2 + trainsnoirst3


# blan , noi = allMarbleTrains(state['board'])
# for elem in blan :
# 	print(elem)



def moveMarblesTrain2(state, marbles, direction):
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
	except game.BadMove :
		dest2 = 'X'
	try : 
		dest1 = getStatus(state,list(addDirection(marbles[0],direction)))
	except game.BadMove :
		dest1 = 'X'
	try : 
		dest3 = getStatus(state,list(addDirection(marbles[2],direction)))
	except game.BadMove :
		dest3 = 'X'
	except IndexError :
		pass
	# print(marbles,computeAlignement(marbles),direction)
	if dest1 == 'X':
		return state['board'], False
	if  dest1 == 'W' and str(computeAlignement(marbles)) != str(direction) : 
		return state['board'], False
	if dest1 == 'B' and str(computeAlignement(marbles)) != direction :
		return state['board'], False
	if dest2 == 'X':
		return state['board'], False
	# print(dest1)
	if  dest2 == 'W' and (li1,ci1) != (ld2,cd2) :
		return state['board'], False
	if  dest2 == 'B' and (li1,ci1) != (ld2,cd2)  :
		return state['board'], False
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


# print(allMarbleTrains(state['board']))


def possmoves2(state,marble):
	possiblemoves = []
	dir = ['NE','SW','NW','SE','E','W']
	i = 0
	while i < 6 :
		board, poss = moveMarblesTrain2(state,marble,dir[i])
		if poss == True :
				possiblemoves.append(dir[i])
				i += 1
		else :
			i+= 1
	return possiblemoves

# print(possmoves2(state,[(6,3),(6,4),(6,5)]))

def allWhiteMoves(state):
	white , _ = allMarbleTrains(state['board'])
	white2 , _ = posofmarbles(state['board'])
	allWmoves = []
	for elem in white :
		if computeAlignement(elem) in ['E', 'SE', 'SW']:
			elem = sorted(elem, key=lambda L: -(L[0]*9+L[1]))
		else:
			elem = sorted(elem, key=lambda L: L[0]*9+L[1])
		for dirt in possmoves2(state,elem):
			allWmoves.append([elem,dirt])
	for elem in white2 :
		for dir in possmoves(state,elem) :
			allWmoves.append([[elem],dir])
	return allWmoves

def allBlackMoves(state):
	_ , black = allMarbleTrains(state['board'])
	_ , black2 = posofmarbles(state['board'])
	allBmoves = []
	for elem in black :
		if computeAlignement(elem) in ['E', 'SE', 'SW']:
			elem = sorted(elem, key=lambda L: -(L[0]*9+L[1]))
		else:
			elem = sorted(elem, key=lambda L: L[0]*9+L[1])
		for dirt in possmoves2(state,elem):
			allBmoves.append([elem,dirt])
	for elem in black2 :
		for dir in possmoves(state,elem) :
			allBmoves.append([[elem],dir])
	return allBmoves

# print(allBlackMoves(state))

def randomWhiteMove(state) :
	moves = allWhiteMoves(state)
	isAmove = False
	while isAmove == False :
		move = random.choice(moves)
		if move[1] != list():
			isAmove = True

	return move

def randomBlackMove(state) :
	moves = allBlackMoves(state)
	isAmove = False
	while isAmove == False :
		move = random.choice(moves)
		if move[1] != list():
			isAmove = True

	return move



# print(randomWhiteMove(state))
# print(randomBlackMove(state))


# print(allWhiteMoves(state))




def getPlayerColor(state,name = None):
	if state['players'][0] == name :
		return 'black'
	else : 
		return 'white'
	
# print(getPlayerColor(state))

# for elem in allWhiteMoves(state) :
# 	print(elem)


# for elem in (allBlackMoves(state)):
# 	print(elem)

# def bestBlackMove(state):
# 	indice = 0
# 	max = 0
# 	i = 0
# 	value = 0
# 	for elem in allBlackMoves(state) : 
		
# 		if len(elem[0]) == 1 :
# 			_state = copy.deepcopy(state)
# 			value = int(estimateBoard(moveMarbles(_state,elem[0],elem[1])))
# 			if value > max : 
# 				max = value
# 				indice = i
		

# 		else : 
# 			_state = copy.deepcopy(state)
# 			value = int(estimateBoard(moveMarbles(_state,sorted(elem[0]),elem[1])))
# 			if value > max : 
# 				max = value
# 				indice = i
# 		i += 1
# 	if max == 0 and state != _state :
# 		return random.choice(allBlackMoves(state)),max
	
# 	return allBlackMoves(state)[indice],estimateBoard(_state['board'])
		
# print(estimateBoard(state['board']))
# print(bestBlackMove(state))

# print(allBlackMoves(state))



# print(moveMarblesTrain(state,[[6, 4], [6, 5], [6, 6]], 'E'))
# print(estimateBoard(moveMarblesTrain(state,[[6, 4], [6, 5], [6, 6]], 'E')['board']))

def apply(state,move):
	if len(move[0]) == 1:
		return moveOneMarble(state,move[0][0],move[1])
	else : 
		return moveMarblesTrain(state,move[0],move[1])

def gameOver(state):
	whites, blacks = posofmarbles(state['board'])
	if len(whites) <= 8 :
		return True, 'black'
	if len(blacks) <= 8 :
		return True, 'white'
	else :
		return False, None

def moves(state,player): 
	if player == 'black' :
		return allBlackMoves(state)
	else : 
		return allWhiteMoves(state)

def otherplayer(player) : 
	if player == 'black' : 
		return 'white'
	if player == 'white' :
		return 'black'
	else :
		return None

def estimateBoard(state,player):
	game, winner = gameOver(state)
	if game == True and winner == player :
		return 1
	if game == False :
		return 0
	else :
		return -1

# blancs, noirs = posofmarbles(state['board'])


def timeit(fun):
	def wrapper(*args, **kwargs):
		start = time.time()
		res = fun(*args, **kwargs)
		print('Executed in {}s'.format(time.time() - start))
		return res
	return wrapper


def negamax(state, player,depht = 3, alpha = float('-inf') , beta = float('inf')):
	game, winner = gameOver(state)
	if depht == 0:
		return -estimateBoard(state,winner), None

	theValue, theMove = float('-inf'), None
	for move in moves(state,player):
		successor = apply(state,move)
		value, _ = negamax(successor, otherplayer(player),depht-1,-beta,-alpha)
		if value > theValue:
			theValue, theMove = value, move
		alpha = max(alpha, theValue)
		if alpha >= beta:
			break
	return -theValue, theMove

@timeit
def wrapperbis(*args,fun = negamax):
	return negamax(*args)
	
print(wrapperbis(state2,'black'))

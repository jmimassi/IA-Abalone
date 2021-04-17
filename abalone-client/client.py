import socket 
import json
import time
from threading import Thread, Timer
import sys
import IA
import jsonNetwork 
import random


s = socket.socket()
s.connect(('127.0.0.1',3000))

def inscription(port = 3100, name = "195048,195178"):
	jsonNetwork.sendJSON(s,{
	"request": "subscribe",
	"port": port,
	"name": name,
	"matricules": ["12345", "67890"]
	})
	recu = jsonNetwork.receiveJSON(s)
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
	
	request = jsonNetwork.receiveJSON(client)
		
	if request['request'] == 'ping':
		print('ok')
		jsonNetwork.sendJSON(client,{'response':'pong'})
	elif request['request'] == 'play' :
		state = request['state']
		print('moving')
		if getPlayerColor(state,name) == 'black' :
			move = IA.randomBlackMove(state)
		else :
			move = IA.randomWhiteMove(state)
		print(move[0])
		print(move[1])
		jsonNetwork.sendJSON(client,{
		"response": "move",
		"move": {
		"marbles": move[0],
		"direction": move[1]
		},
		"message": "Fun message"
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








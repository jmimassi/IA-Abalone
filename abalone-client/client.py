import socket 
import json
import time
from threading import Thread, Timer

import jsonNetwork 
s = socket.socket()
s.connect(('127.0.0.1',3000))

def inscription(port):
	jsonNetwork.sendJSON(s,{
	"request": "subscribe",
	"port": port,
	"name": "fun_name_for_the_client",
	"matricules": ["12345", "67890"]
	})
	recu = jsonNetwork.receiveJSON(s)
	reponse = str(recu['response'])
	print(reponse)
	Thread(target=pong).start()




def processRequest(client,address):
	'''
		Route request to request handlers
	'''
	print('a')
	print('request from')
	
	request = jsonNetwork.receiveJSON(client)
		
	if request['request'] == 'pong':
		print('ok')
		jsonNetwork.sendJSON(client,{'response':'pong'})
			
	else:
		raise ValueError('Unknown request \'{}\''.format(request['request']))


def listenForRequests(port = 3001):
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
				client, address = s.accept()
				with client:
					processRequest(client, address)
	
	listenThread = Thread(target=processClients, daemon=True)
	listenThread.start()

	def stop():
		nonlocal running
		running = False
		listenThread.join()

	return stop




def pong():
	print('a')
	demande = jsonNetwork.receiveJSON(s)
	print('reveived')
	print(str(demande['response']))
	if demande['request'] == 'ping':
		jsonNetwork.sendJSON(s,{'response':'pong'})
		print('ahah')
	else : 
		print('None')




inscription(3100)



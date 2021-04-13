import socket 
import json
import time
from threading import Thread, Timer
import sys

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
	for arg in args:
		port = int(arg)
	inscription(port)
	listenForRequests(port)







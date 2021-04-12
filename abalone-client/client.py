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
	


def listenForRequests():
	def pong():
		recu = jsonNetwork.receiveJSON(s)
		print(str(recu['response']))
		if recu['response'] == 'ping':
			jsonNetwork.sendJSON(s,{'response':'pong'})
		else : 
			print('None')
	
	listenThread = Thread(target=pong, daemon=True)
	listenThread.start()

	def stop():
		listenThread.join()

	return stop



inscription(3100)


import socket 
import json
import time

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

inscription(3100)
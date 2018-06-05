#!/usr/bin/env python
import pika
from flask import stream_with_context, request, Response, json

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='192.168.99.100'))
channel = connection.channel()

data = {  
    "id": "1uTiEsvrhj2zVqEAfPTBwC1NemgFwaatV",         
    "accessToken": "ya29.GlvEBRgnXpNYvVAvXO6an2J019L2TUL5Zp_Uhv2ebpDXT3D1bCNuDBS5RTCMN8HaHGKZBGf3I7dYBEoGqLbhmAcgW7ChgAx9rv9skTpWcO-ELeEKC7HzokWVOKER",         
    "description": "This is description about me"     
} 

message = json.dumps(data) 
channel.queue_declare(queue='findSegments')

channel.basic_publish(exchange='',
                      routing_key='findSegments',
                      body=message)
print(" [x] Sent 'Hello World!'")
connection.close()
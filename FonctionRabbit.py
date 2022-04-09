#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='creation')
channel.queue_declare(queue='suppression')
channel.queue_declare(queue='travail_finis')
channel.queue_declare(queue='modification')
channel.queue_declare(queue='rename')
channel.queue_declare(queue='publication')

channel.basic_publish(exchange='', routing_key='creation', body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()
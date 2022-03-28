#!/usr/bin/env python
import pika, sys, os

list_queue =["generale","creation","suppression","travail_finis","modification","rename","publication"]

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()



    def callback(ch, method, properties, body):
        match method.routing_key :
            case "creer":
                return print("Non louis")
            case "creation":
                return print("Création de la vm")

        print(" [x] Received %r" % body)

    for queue in list_queue:
        channel.queue_declare(queue=queue)
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
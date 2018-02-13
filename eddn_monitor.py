#!/usr/bin/python

import settings
import zmq
import zlib
import simplejson
import pprint
import time
import eddn_journal

pp = pprint.PrettyPrinter(indent=2)

def main():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.setsockopt(zmq.SUBSCRIBE, "")
    while True:
        try:
            subscriber.connect(settings.eddn_relay)
            poller = zmq.Poller()
            poller.register(subscriber, zmq.POLLIN)
            while True:
                socks = dict(poller.poll(settings.eddn_timeout))
                if socks:
                    if socks.get(subscriber) == zmq.POLLIN:
                        msg = subscriber.recv(zmq.NOBLOCK)
                        msg = zlib.decompress(msg)
                        data = simplejson.loads(msg)
                        if data['$schemaRef'] == 'https://eddn.edcd.io/schemas/journal/1':
                            eddn_journal.process(data)
                        else:
                            pp.pprint(data['$schemaRef'])
                else:
                    print 'Disconnect from EDDN (After timeout)'
                    sys.stdout.flush()
                    subscriber.disconnect(settings.eddn_relay)
                    break
        except zmq.ZMQError, e:
            print 'Disconnect from EDDN (After ZMQError)'
            print 'ZMQSocketException: ' + str(e)
            sys.stdout.flush()
            subscriber.disconnect(settings.eddn_relay)
            time.sleep(10)

if __name__ == '__main__':
    main()

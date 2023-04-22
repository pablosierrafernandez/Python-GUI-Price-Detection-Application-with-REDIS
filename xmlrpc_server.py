from distutils.command.config import config
from xmlrpc.server import SimpleXMLRPCServer
import logging
import xmlrpc.client
import config
import pandas as pd
import redis
from operator import itemgetter
import json
import time
headers=['Local time','Ask','Bid','AskVolume','BidVolume']

# Start the server
try:
   proxy = xmlrpc.client.ServerProxy('http://localhost:'+str(config.CLUSTER))
   host=proxy.get_next_host()
   print(proxy.put_server(host))
   host_link="http://localhost:"+str(host)
   # Set up logging
   logging.basicConfig(level=logging.INFO)
   r = redis.StrictRedis(host='localhost', port=int(config.REDISPORT), decode_responses=True)
   r.set("worker:"+str(host), host_link)
   server = SimpleXMLRPCServer(
    ('localhost', int(host)),
    logRequests=True,
)
  
   def get_min(json_file, price):
      start_time = time.time()
      dict=json.loads(r.get(json_file))
      minim=min(dict[price].values())
      return minim, time.time() - start_time

   server.register_function(get_min)
   
   def get_max(json_file, price):
      start_time = time.time()
      dict=json.loads(r.get(json_file))
      maxim=min(dict[price].values())
      return maxim, time.time() - start_time

   server.register_function(get_max)


   server.serve_forever()
except KeyboardInterrupt:
   r.delete("worker:"+str(host))
   r.connection_pool.disconnect()

   proxy.close_server(host)
   server.shutdown() 
   print('Exiting')


########################################################################################




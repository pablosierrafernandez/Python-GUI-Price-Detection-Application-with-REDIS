from xmlrpc.server import SimpleXMLRPCServer
import logging
import config

## Variables
array_ip=[]


# Set up logging
logging.basicConfig(level=logging.INFO)

server = SimpleXMLRPCServer(
    ('localhost', config.CLUSTER),
    logRequests=True,
)


# FUNCIONES PUBLICAS

#----FUNCIONES DE SERVERS
def get_next_host():
    if not array_ip:
        return config.CLUSTER+1
    else:
        host=array_ip[-1]
        host=int(host)+1
        return host
server.register_function(get_next_host)

#pillar server
def put_server(server_name):
    #logging.info('get_server(%s)', server_name)
    add_server(server_name)
    return server_name


server.register_function(put_server)

#borrar server
def close_server(server_name):
    #logging.info('close_server(%s)', server_name)
    remove_server(server_name)
    print(server_name, " disconnected")
    return server_name

server.register_function(close_server)
#------FUNCIONES PARA CLIENTE
#listar direcciones, devuelve las direcciones conectadas
def get_servers():
    return array_ip

server.register_function(get_servers)


#### funciones del cluster propias

def add_server(url):
    array_ip.append(url)

def remove_server(url):
    array_ip.remove(url)

# Start the server
try:
    print('Use Control-C to exit')
    server.serve_forever()
except KeyboardInterrupt:
    print('Exiting')
    print(array_ip)
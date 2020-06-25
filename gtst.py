import time
from simple_socket.tcp_client import SimpleTCPClient, SimpleSSLClient
from simple_socket.tcp_server import SimpleTCPServer, SimpleSSLServer
import socket

server = SimpleSSLServer(3888, trace=True)
print('server=', server)
serverReceivedConnection = False
serverReceivedDisconnection = False


def ServerConnection(c, state):
    print('ServerConnection(', c, state)
    global serverReceivedConnection
    global serverReceivedDisconnection

    if state == 'Connected':
        serverReceivedConnection = True
    elif state == 'Disconnected':
        serverReceivedDisconnection = True

    print('serverReceivedConnection=', serverReceivedConnection)
    print('serverReceivedDisconnection=', serverReceivedDisconnection)


server.onConnected = ServerConnection
server.onDisconnected = ServerConnection


def ServerRx(c, data):
    c.Send(b'echo ' + data)  # echo the data


server.onReceive = ServerRx
client = SimpleSSLClient(socket.gethostname(), 3888, autoConnect=False, trace=True)
print('client.Hostname=', client.Hostname)

clientRecievedEcho = False


def ClientRx(_, data):
    print('ClientRx(', data)
    global clientRecievedEcho
    if b'echo test' == data:
        clientRecievedEcho = True


client.onReceive = ClientRx


def ClientConnection(_, state):
    print('ClientConnection(', state)


client.onConnected = ClientConnection
client.onDisconnected = ClientConnection

res = client.Connect()
print('res=', res)
if 'Disconnected' in res:
    raise ConnectionError()

time.sleep(1)
client.Send('test')
time.sleep(1)

assert serverReceivedConnection
assert clientRecievedEcho

client.Disconnect()
time.sleep(1)
assert serverReceivedDisconnection
print('end test')
# SimpleTCPClient

import random
from simple_socket.tcp_client import SimpleTCPClient
client = SimpleTCPClient('10.8.27.171', 23)
print('client.Hostname=', client.Hostname)

# by default, the client will connect and attempt to maintain its connection.
# if you want to manually control the connection, pass autoConnect=False
# then use the .Connect() and .Disconnect() methods to manage your connection manually

client.onConnected = lambda _, state: print('The client is', state)
client.onDisconnected = lambda _, state: print('The client is', state)

client.onReceive = lambda _, data: print('Rx:', data)

while True:
    cmd = random.choice(['q', 'n', 'i'])
    print('sending:', cmd)
    if 'Connected' in client.ConnectionStatus:
        client.Send(cmd)
    time.sleep(5)

# SimpleUDPClient

from simple_socket.udp_client import SimpleUDPClient

client1 = SimpleUDPClient('localhost', sendIPPort=1025, receiveIPPort=1024)


def Client1HandleReceive(interface, data):
    client1.Send('From client1 echo: {}'.format(data.decode()))


client1.onReceive = Client1HandleReceive
print('client1=', client1)

client2 = SimpleUDPClient('localhost', sendIPPort=1024, receiveIPPort=1025)
client2.onReceive = lambda _, data: print('Rx:', data)
print('client2=', client2)
while True:
    client2.Send(f'From client2: The time is {time.asctime()}\r\n')
    time.sleep(3)



# simple_tcp

import random

client = SimpleTCPClient('10.8.27.171', 23)


# by default, the client will connect and attempt to maintain its connection.
# if you want to manually control the connection, pass autoConnect=False
# then use the .Connect() and .Disconnect() methods to manage your connection manually

# you can stack decorators for events
@client.onConnected
@client.onDisconnected
def HandleConnectionChange(_, state):
    print('The client is', state)


# or you can single-stack decorators
@client.onReceive
def HandleReceive(_, data):
    print('The client received this data:', data)


# you could replace the above with
# def HandleReceive(_, data):
#   print('Rx:', data)
# client.onReceive = HandleReceive

while True:
    cmd = random.choice(['q', 'n', 'i'])
    print('sending:', cmd)
    if 'Connected' in client.ConnectionStatus:
        client.Send(cmd)
    time.sleep(5)

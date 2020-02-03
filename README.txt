# simple_tcp

import random
# from simple_tcp.tcp_client import SimpleTCPClient
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

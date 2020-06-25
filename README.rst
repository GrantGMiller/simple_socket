SimpleTCPClient
===============

.. code:: python

    import random
    import time
    from simple_socket.tcp_client import SimpleTCPClient # try also SimpleSSLClient for semi-secure communication (it does not verify the cert)

    client = SimpleTCPClient('192.168.254.254', 1885)
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

SimpleUDPClient
===============

.. code:: python

    from simple_socket.udp_client import SimpleUDPClient
    import time

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

SimpleTCPServer
===============

.. code:: python

    from simple_socket.tcp_server import SimpleTCPServer # try also SimpleSSLServer for semi-secure communication (it uses a self-signed cert)
    server = SimpleTCPServer(3888)

    server.onConnected = lambda client, state: print('Client {} is {}'.format(client, state))
    server.onDisconnected = lambda client, state: print('Client {} is {}'.format(client, state))


    def HandleRx(client, data):
        print('Server received {} from {}'.format(data, client))
        client.Send(b'Echo: ' + data + b'\r\n')

        if b'q' in data:
            # the server can force-close a connection
            # in this case,
            # the server will disconnect a client if they send the letter 'q'
            client.Disconnect()


    server.onReceive = HandleRx


from simple_socket.tcp_server import SimpleSSLServer, SimpleTCPServer

server = SimpleSSLServer(1885, listenAddress='192.168.68.105')
server.onConnected = lambda client, state: print(client, state)
server.onReceive = lambda client, data: print(client, data)

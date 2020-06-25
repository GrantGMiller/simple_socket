import socket
import time
from threading import Timer
import ssl


class Client:
    def __init__(self, parent, sock, ipAddress, servicePort):
        self._parent = parent
        self.sock = sock
        self.ipAddress = ipAddress
        self.servicePort = servicePort

        self.sock.settimeout(0.1)

    def Print(self, *a, **k):
        if self._parent.trace:
            print(*a, **k)

    def Send(self, data):
        self.Print('Client.Send(', self, data)
        if not isinstance(data, bytes):
            data = data.encode(encoding='iso-8859-1')

        self.sock.send(data)

    def Recv(self):
        try:
            data = self.sock.recv(1024)
            self.Print('Client.Recv(', self, ', data=', data)
            if data == b'':
                # client has disconnected
                self.Disconnect()
                return data
            else:
                return data
        except Exception as e:
            if 'timed out' in str(e):
                pass
            else:
                self.Print('Client.Recv e=', e)
                self.Disconnect()
                raise e

    def Disconnect(self):
        self.Print('Client.Disconnect(', self)
        self._parent._NewConnectionStatus(self, 'Disconnected')
        self.sock.close()


class _BaseTCPServer:
    def __init__(self, listenport, maxClients=None, disconnectDeadClients=True, trace=False):
        self._listenport = listenport
        self._maxClients = maxClients or 10
        self._disconnectDeadClients = disconnectDeadClients
        self.trace = trace

        self._clients = {
            # clientSocket: clientObj,
        }

        self._onConnectedCallback = None
        self._onDisconnectedCallback = None
        self._connectionStatus = ''

        self._onReceiveCallback = None
        self._timerParseReceive = None

        self._timerAutoConnect = None
        self._running = True

    def Stop(self):
        self._running = True


    def Print(self, *a, **k):
        if self.trace:
            print(*a, **k)

    @property
    def Clients(self):
        return set(self._clients.values())

    @property
    def ListenIPAddress(self):
        return socket.gethostbyname(socket.gethostname())

    @property
    def ListenPort(self):
        return self._listenport

    @property
    def onConnected(self):
        return self._onConnectedCallback

    @onConnected.setter
    def onConnected(self, callback):
        self._onConnectedCallback = callback
        for client in self._clients.values():
            if self._onConnectedCallback:
                self._onConnectedCallback(client, 'Connected')

    @property
    def onDisconnected(self):
        return self._onDisconnectedCallback

    @onDisconnected.setter
    def onDisconnected(self, callback):
        self._onDisconnectedCallback = callback

    @property
    def onReceive(self):
        return self._onReceiveCallback

    @onReceive.setter
    def onReceive(self, callback):
        self._onReceiveCallback = callback

    def _NewConnectionStatus(self, client, newState):
        self.Print('Server _NewConnectionStatus(', client, newState)
        if newState == 'Disconnected':
            self._clients.pop(client.sock, None)
            if self.onDisconnected:
                self.onDisconnected(client, 'Disconnected')
        elif newState == 'Connected':
            self._clients[client.sock] = client
            if self.onConnected:
                self.onConnected(client, 'Connected')

    def _GetClient(self, clientSock, address):
        c = self._clients.get(clientSock, None)
        if c is None:
            c = Client(
                parent=self,
                sock=clientSock,
                ipAddress=address[0],
                servicePort=address[1],
            )
            self._clients[clientSock] = c
            self._NewConnectionStatus(c, 'Connected')
            return c

    def _RestartReceiveLoop(self):
        if self._running is False:
            self._sock.close()
            return

        if self._timerParseReceive is None:
            self._timerParseReceive = Timer(0.1, self._ParseReceiveData)
            self._timerParseReceive.start()

        elif self._timerParseReceive.is_alive():
            self._timerParseReceive.cancel()
            self._timerParseReceive = None
            self._RestartReceiveLoop()
        else:
            self._timerParseReceive = None
            self._RestartReceiveLoop()

    def _StopReceiveLoop(self):
        if self._timerParseReceive and self._timerParseReceive.isAlive():
            self._timerParseReceive.cancel()
        self._timerParseReceive = None

    def _ParseReceiveData(self):
        try:
            # self.Print('Check for any new clients')
            clientsock, address = self._sock.accept()  # accept any clients that are trying to connect
            self.Print('Server has new client: clientsock=', clientsock, ', address=', address)
            self._GetClient(clientsock, address)
        except:
            pass

        # process any newly received data from clients
        if self._onReceiveCallback:
            for c in self._clients.copy().values():
                try:
                    data = c.Recv()  # may fail due to socket closure
                except Exception as e:
                    print('Client {} Receive Exception: {}'.format(c, e))
                    data = b''

                if data:
                    try:
                        self._onReceiveCallback(c, data)  # might fail due to user callback
                    except Exception as e:
                        print('Callback Error:', e)

        self._RestartReceiveLoop()

    def Connect(self, timeout=None):
        self.Print('Connect(timeout=', timeout)
        try:
            if self._sock is None:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(timeout or 10)
            self._sock.connect((self._hostname, self._ipport))
            self._NewConnectionStatus('Connected')
        except Exception as e:
            self.Print('Connection Error:', e)
            if 'A connect request was made on an already connected socket' in str(e):
                self._NewConnectionStatus('Connected')
                return 'Connected'

            self._NewConnectionStatus('Disconnected:' + str(e))

        return self._connectionStatus

    @property
    def ConnectionStatus(self):
        return self._connectionStatus

    def Disconnect(self):
        if 'Disconnected' in self._connectionStatus:
            return self._connectionStatus

        try:
            if self._sock is not None:
                self._sock.shutdown(1)
                self._sock.close()
        except Exception as e:
            pass

        self._NewConnectionStatus('Disconnected')
        self._sock = None
        return self._connectionStatus


class SimpleTCPServer(_BaseTCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(0.1)
        self._sock.bind((socket.gethostname(), self._listenport))
        self._sock.listen(self._maxClients)

        self._RestartReceiveLoop()


class SimpleSSLServer(_BaseTCPServer):
    '''
    Consider generating your own self-signed cert

    Install OpenSSL
    win64_url = 'https://slproweb.com/download/Win64OpenSSL-1_1_1g.msi'
    win32_url = 'https://slproweb.com/download/Win32OpenSSL-1_1_1g.msi'

    Generate your own certs
    openssl req -x509 -newkey rsa:4096 -keyout private.key -out cert.pem -days 365

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Print('SimpleSSLServer.__init__(', *args)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(0.1)
        self._sock.bind((socket.gethostname(), self._listenport))

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('cert.pem', 'private.key', password='simple_socket')

        self._sock = context.wrap_socket(
            self._sock,
            server_side=True,
        )  # self._sock now an ssl server

        self._sock.listen(self._maxClients)
        self._RestartReceiveLoop()


if __name__ == '__main__':
    import random

    # from simple_socket.tcp_server import SimpleTCPServer
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

    from simple_socket.tcp_client import SimpleTCPClient
    import random

    clients = []
    for i in range(3):
        client = SimpleTCPClient(socket.gethostname(), 3888)

        client.onConnected = lambda _, state, i=i: print('The client', i, 'is', state)
        client.onDisconnected = lambda _, state, i=i: print('The client', i, 'is', state)

        client.onReceive = lambda _, data, i=i: print('Client {} Rx:{}'.format(i, data))

        clients.append(client)

    while True:
        for index, client in enumerate(clients.copy()):
            if client.ConnectionStatus == 'Connected':
                client.Send('Client {} says the time is {}'.format(index, time.asctime()))
                time.sleep(1)
                if random.randint(0, 3) == 0:
                    client.Disconnect()

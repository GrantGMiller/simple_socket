import socket
import time
from threading import Timer
import ssl


class _BaseTCPClient:
    def __init__(self, hostname, ipport, autoConnect=True, trace=False):
        self._hostname = hostname
        self._ipport = ipport
        self._autoConnect = autoConnect
        self._trace = trace

        self._sock = None

        self._onConnectedCallback = None
        self._onDisconnectedCallback = None
        self._connectionStatus = ''

        self._onReceiveCallback = None
        self._timerParseReceive = None

        self._timerAutoConnect = None

        self._running = True

        if self._autoConnect:
            self.Connect(1)

    def Stop(self):
        self._running = False

    @property
    def Hostname(self):
        return self._hostname

    @property
    def IPPort(self):
        return self._ipport

    @property
    def onConnected(self):
        return self._onConnectedCallback

    @onConnected.setter
    def onConnected(self, callback):
        self._onConnectedCallback = callback
        if 'Connected' in self._connectionStatus:
            if self._onConnectedCallback:
                self._onConnectedCallback(self, self._connectionStatus)

    @property
    def onDisconnected(self):
        return self._onDisconnectedCallback

    @onDisconnected.setter
    def onDisconnected(self, callback):
        self._onDisconnectedCallback = callback
        if 'Disconnected' in self._connectionStatus:
            if self._onDisconnectedCallback:
                self._onDisconnectedCallback(self, self._connectionStatus)

    @property
    def onReceive(self):
        return self._onReceiveCallback

    @onReceive.setter
    def onReceive(self, callback):
        self._onReceiveCallback = callback

    def _NewConnectionStatus(self, newState):
        if newState != self._connectionStatus:
            self._connectionStatus = newState
            if 'Connected' in self._connectionStatus:
                if self._onConnectedCallback:
                    self._onConnectedCallback(self, 'Connected')

                self._RestartReceiveLoop()

            elif 'Disconnected' in self._connectionStatus:
                if self._onDisconnectedCallback:
                    self._onDisconnectedCallback(self, 'Disconnected')

                self._StopReceiveLoop()

        if self._autoConnect and 'Disconnected' in self._connectionStatus:
            if self._timerAutoConnect and self._timerAutoConnect.is_alive():
                self._timerAutoConnect.cancel()
            self._timerAutoConnect = Timer(5, self.Connect)
            self._timerAutoConnect.start()

    def _RestartReceiveLoop(self):
        if self._running is False:
            self._sock.close()
            return

        if self._timerParseReceive is None:
            self._timerParseReceive = Timer(0.5, self._ParseReceiveData)
            self._timerParseReceive.start()

        elif self._timerParseReceive.is_alive():
            self._timerParseReceive.cancel()
            self._timerParseReceive = None
            self._RestartReceiveLoop()
        else:
            self._timerParseReceive = None
            self._RestartReceiveLoop()

    def _StopReceiveLoop(self):
        if self._timerParseReceive and self._timerParseReceive.is_alive():
            self._timerParseReceive.cancel()
        self._timerParseReceive = None

    def Print(self, *a, **k):
        if self._trace:
            print(*a, **k)

    def _ParseReceiveData(self):
        try:
            rxData = self._sock.recv(1024)
            if rxData == b'':
                self.Disconnect()
            else:
                self.Print('Client Rx:', rxData)

            if self._onReceiveCallback:
                # do callback in its own thread to prevent blocking
                Timer(0, self._onReceiveCallback, args=(self, rxData)).start()

        except Exception as e:
            if 'timed out' in str(e):
                pass

        if 'Connected' in self._connectionStatus:
            self._RestartReceiveLoop()

    def Connect(self, timeout=None):
        raise NotImplementedError

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

    def Send(self, data):
        if isinstance(data, str):
            data = data.encode(encoding='iso-8859-1')

        try:
            self._sock.send(data)
        except:
            try:
                self.Disconnect()
            except:
                pass

    def __del__(self):
        self.Stop()

    def __str__(self):
        return f'<{type(self)}: Hostname={self.Hostname}, IPPort={self.IPPort}, ConnectionStatus={self.ConnectionStatus}, id={id(self)}>'


class SimpleTCPClient(_BaseTCPClient):
    def Connect(self, timeout=None):
        self.Print('Client Connect(timeout=', timeout)
        try:
            if self._sock is None:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(timeout or 10)
            self._sock.connect((self._hostname, self._ipport))
            self._NewConnectionStatus('Connected')
        except Exception as e:
            print('Client Connection Error:', e)
            if 'A connect request was made on an already connected socket' in str(e):
                self._NewConnectionStatus('Connected')
                return 'Connected'

            self._NewConnectionStatus('Disconnected:' + str(e))

        return self._connectionStatus


class SimpleSSLClient(_BaseTCPClient):
    def Connect(self, timeout=None):
        self.Print('\nssl.OPENSSL_VERSION=', ssl.OPENSSL_VERSION)
        self.Print('Client Connect(timeout=', timeout)
        try:
            if self._sock is None:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                self._sock = context.wrap_socket(
                    self._sock,
                    server_hostname=self.Hostname,
                )  # self._sock is now an SSL client

            self._sock.settimeout(timeout or 10)
            self._sock.connect((self._hostname, self._ipport))
            self._NewConnectionStatus('Connected')
        except Exception as e:
            print('Connection Error:', e)
            if 'A connect request was made on an already connected socket' in str(e):
                self._NewConnectionStatus('Connected')
                return 'Connected'

            self._NewConnectionStatus('Disconnected:' + str(e))

        return self._connectionStatus


if __name__ == '__main__':
    import random

    # from simple_socket.tcp_client import SimpleTCPClient
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

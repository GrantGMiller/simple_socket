import socket
import time
from threading import Timer


class SimpleUDPClient:
    def __init__(self, hostname, sendIPPort, receiveIPPort=0, trace=False):
        self._hostname = hostname
        self._sendIPPort = sendIPPort
        self._receiveIPPort = receiveIPPort

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(('', self._receiveIPPort))

        self._onConnectedCallback = None
        self._onDisconnectedCallback = None
        self._connectionStatus = ''

        self._onReceiveCallback = None
        self._timerParseReceive = None

        self._timerAutoConnect = None

        self._RestartReceiveLoop()

    @property
    def Hostname(self):
        return self._hostname

    @property
    def IPPort(self):
        return self._sendIPPort

    def StartLogging(self):
        pass

    def StopLogging(self):
        pass

    @property
    def onReceive(self):
        return self._onReceiveCallback

    @onReceive.setter
    def onReceive(self, callback):
        self._onReceiveCallback = callback

    def _RestartReceiveLoop(self):
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
        if self._timerParseReceive and self._timerParseReceive.isAlive():
            self._timerParseReceive.cancel()
        self._timerParseReceive = None

    def _ParseReceiveData(self):
        try:
            rxData, otherClientAddress = self._sock.recvfrom(1024)
            if rxData == b'':
                pass
            if self._onReceiveCallback:
                # do callback in its own thread to prevent blocking
                Timer(0, self._onReceiveCallback, args=(self, rxData)).start()
        except Exception as e:
            if 'timed out' in str(e):
                pass

        self._RestartReceiveLoop()

    def Send(self, data):
        if isinstance(data, str):
            data = data.encode(encoding='iso-8859-1')

        try:
            self._sock.sendto(data, (self._hostname, self._sendIPPort))
            return True
        except Exception as e:
            return False


if __name__ == '__main__':
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

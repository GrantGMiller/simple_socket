import time

import pytest

from simple_socket.tcp_client import SimpleTCPClient, SimpleSSLClient
from simple_socket.tcp_server import SimpleTCPServer, SimpleSSLServer
import socket


def test_SimpleTCPClientAndServer():
    server = SimpleTCPServer(1885, trace=True)

    serverReceivedConnection = False
    serverReceivedDisconnection = False

    def ServerConnection(c, state):
        print('ServerConnection(', c, state)
        nonlocal serverReceivedConnection
        nonlocal serverReceivedDisconnection

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
    client = SimpleTCPClient(socket.gethostname(), 1885, trace=True)

    clientRecievedEcho = False

    def ClientRx(_, data):
        print('ClientRx(', data)
        nonlocal clientRecievedEcho
        if b'echo test' == data:
            clientRecievedEcho = True

    client.onReceive = ClientRx

    def ClientConnection(_, state):
        print('ClientConnection(', state)

    client.onConnected = ClientConnection
    client.onDisconnected = ClientConnection

    while client.ConnectionStatus == 'Disconnected' or serverReceivedConnection:
        print('Waiting for connection')
        time.sleep(1)

    time.sleep(1)
    client.Send('test')
    time.sleep(1)

    assert serverReceivedConnection
    assert clientRecievedEcho

    client.Disconnect()
    time.sleep(1)
    assert serverReceivedDisconnection

    server.Stop()
    client.Stop()


def test_SSLServerClient():
    server = SimpleSSLServer(3888, trace=True)

    serverReceivedConnection = False
    serverReceivedDisconnection = False

    def ServerConnection(c, state):
        print('ServerConnection(', c, state)
        nonlocal serverReceivedConnection
        nonlocal serverReceivedDisconnection

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
        nonlocal clientRecievedEcho
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

    server.Stop()
    client.Stop()


def test_SMD():
    client = SimpleTCPClient('192.168.68.143', 23)
    client.onConnected = lambda _, state: print('SMD:', state)
    client.onDisconnected = lambda _, state: print('SMD:', state)

    def HandleRX(intf, data):
        print('HandleRX(', data)
        if 'Password:' in data.decode():
            print('sending password *****')
            intf.Send('extron\r')

    client.onReceive = HandleRX

    while 'Disconnected' in client.ConnectionStatus:
        print('waiting for connection')
        time.sleep(1)

    for i in range(3):
        time.sleep(1)
        msg = 'q'
        print('Send(', msg)
        client.Send(msg)

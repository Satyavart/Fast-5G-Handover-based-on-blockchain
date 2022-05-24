from HSSutility.p2p import MyOwnPeer2PeerNode
import argparse
import time


def start_server(host,port,name):    
    node = MyOwnPeer2PeerNode(host,port,name)
    node.start()
    #node.connect_with_node(di,dp)

    while True:
        a = input("> ")
        if a == "exit":
            break
    node.stop()

parser = argparse.ArgumentParser()
parser.add_argument("-i","--host",dest="ip",help="Enter the ip of ME")
parser.add_argument("-p","--port",dest="port",help="Enter the port of the ME")
parser.add_argument("-n","--name",dest="name",help="Enter name of ME")

server = parser.parse_args()
start_server(server.ip,int(server.port),server.name)

# python HSS.py -i 127.0.0.1 -p 9015 -n HSS_123
from MEutility.p2p import MyOwnPeer2PeerNode
import argparse
import time



def start_server(host,port,name,di,dp,home):    
    node = MyOwnPeer2PeerNode(host,port,name,home)
    node.start()
    node.connect_with_node(di,dp)
    node.registration()


    while True:
        a = input("> ")
        if a == "exit":
            break
        elif a == "its":
            print(node.initial_time_stamp)
        elif a == "handover":
            print("Enter Destination")
            c = int(input("to >> "))
            node.handover(c)
        elif a == "current":
            print("Currently connected to "+node.nodes_outbound[0].name)
    node.stop()

parser = argparse.ArgumentParser()
parser.add_argument("-i","--host",dest="ip",help="Enter the ip of ME")
parser.add_argument("-p","--port",dest="port",help="Enter the port of the ME")
parser.add_argument("-n","--name",dest="name",help="Enter name of ME")
parser.add_argument("-di","--destination_ip",dest="d_ip",help="Enter ip of destination")
parser.add_argument("-dp","--destination_port",dest="d_port",help="Enter port of destination")
parser.add_argument("-ho","--home_hss_name",dest="home",help="Enter name of home HSS")

server = parser.parse_args()

start_server(server.ip,int(server.port),server.name,server.d_ip,int(server.d_port),server.home)

# python ME.py -i 127.0.0.1 -p 9012 -n ME_Samsung -di 127.0.0.1 -dp 9020 -ho HSS_123

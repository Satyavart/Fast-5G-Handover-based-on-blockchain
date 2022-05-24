from eNButility.p2p import MyOwnPeer2PeerNode
import argparse
import sqliteDatabase



def start_server(host,port,name,di,dp):
    node = MyOwnPeer2PeerNode(host,port,name)

    node.start()
    node.connect_with_node(di,dp)
    #print(node.nodes_outbound[0].name)
    sqliteDatabase.save(host,port,name,node.id,node.initial_time_stamp,node.nodes_outbound[0].name)


    while True:
        a = input("> ")
        if a == "exit":
            break

    node.stop()

parser = argparse.ArgumentParser()
parser.add_argument("-i","--host",dest="ip",help="Enter the ip of server")
parser.add_argument("-p","--port",dest="port",help="Enter the port of the server")
parser.add_argument("-n","--name",dest="name",help="Enter name of server")
parser.add_argument("-di","--destination_ip",dest="d_ip",help="Enter ip of destination")
parser.add_argument("-dp","--destination_port",dest="d_port",help="Enter port of destination")

server = parser.parse_args()

start_server(server.ip,int(server.port),server.name,server.d_ip,int(server.d_port))

# python eNB.py -i 127.0.0.1 -p 9020 -n eNB_1 -di 127.0.0.1 -dp 9001
# python eNB.py -i 127.0.0.1 -p 9033 -n eNB_2 -di 127.0.0.1 -dp 9002
# python eNB.py -i 127.0.0.1 -p 9034 -n eNB_3 -di 127.0.0.1 -dp 9002
# python eNB.py -i 127.0.0.1 -p 9053 -n eNB_4 -di 127.0.0.1 -dp 9003
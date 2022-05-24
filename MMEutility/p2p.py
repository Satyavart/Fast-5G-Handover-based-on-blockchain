'''
Author: Satyavart 
Email: satyavarty591@gmail.com
'''


from MMEutility.node import Node
import time
import os
import csv
import hashlib
import random 
from colour import *
import sqliteDatabase

class MyOwnPeer2PeerNode (Node):

    # Python class constructor
    def __init__(self, host, port, name):
        super(MyOwnPeer2PeerNode, self).__init__(host, port, name)
        print("MyPeer2PeerNode: Started")
        sqliteDatabase.save(host,port,name,self.id,self.initial_time_stamp)
        self.saved_message = []


    # all the methods below are called when things happen in the network.
    # implement your network node behavior to create the required functionality.

    def outbound_node_connected(self, node):
        if self.debug:
            prRed("outbound_node_connected: ","end")
            print(node.id)
        else:
            prRed("outbound_node_connected: ")

    def inbound_node_connected(self, node):
        if self.debug:
            prRed("inbound_node_connected: ","end")
            print(node.id)
        else:
            prRed("inbound_node_connected: ")

    def inbound_node_disconnected(self, node):
        if self.debug:
            prRed("inbound_node_disconnected: ","end")
            print(node.id)
        else:
            prRed("inbound_node_disconnected: ")

    def outbound_node_disconnected(self, node):
        if self.debug:
            prRed("inbound_node_disconnected: ","end")
            print(node.id)
        else:
            prRed("outbound_node_disconnected: ")


    #print messages
    def node_message(self, node, data):
        prPurple("message from " + node.name + " : " + data["Type"]) 
        self.process(data)
        if self.debug == True:
            print(data)
        if self.logs == True:
            f = open(os.path.join(os.getcwd()+"/logs",self.name+"_logs.txt"), "a")
            f.write(time.asctime( time.localtime(time.time())) + " FROM " + node.name + " to " + self.name + " " + str(data) + "\n")
            f.close()



    def node_disconnect_with_outbound_node(self, node):
        print("node wants to disconnect with oher outbound node: " + node.id)

    def node_request_to_stop(self):
        print("node is requested to stop!")
        sqliteDatabase.delete(self.id,self.type)


    def hash(self,a):
        a = hashlib.md5(a.encode())
        return a.hexdigest()

    def process(self, data):
        if data["Type"] == "Registration":
            if data["Count"] == 2:
                data["Path"].append(self.id)
                data["Count"] = 3
                n = self.nodes_outbound[0]
                self.send_to_node(n, data)

            elif data["Count"] == 4:
                data["Count"] = 5
                for node in self.nodes_inbound:
                    if node.id == data["Path"][-1]:
                        data["Path"].pop()
                        self.send_to_node(node, data)

        elif data["Type"] == "HSS_auth_request" or data["Type"] == "HSS_auth_response":
            if data["Count"] == 2:
                data["Path"].append(self.id)
                data["Count"] = 3
                n = self.nodes_outbound[0]
                self.send_to_node(n, data)

            elif data["Count"] == 4:
                data["Count"] = 5
                for node in self.nodes_inbound:
                    if node.id == data["Path"][-1]:
                        data["Path"].pop()
                        self.send_to_node(node, data)

        elif data["Type"] == "Key_Broadcast":
            for node in self.nodes_inbound:
                val = data["id"] + "+" + self.id + "+" + node.id
                data["PID"] = self.hash(val)
                self.send_to_node(node, data)


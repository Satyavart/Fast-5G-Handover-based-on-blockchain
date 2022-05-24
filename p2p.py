'''
Author: Satyavart 
Email: satyavarty591@gmail.com
'''


from node import Node
import time
import os
import csv
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
        prPurple("message from " + node.name) 
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


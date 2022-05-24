'''
Author: Satyavart 
Email: satyavarty591@gmail.com
'''


from eNButility.node import Node
import time
import os
import csv
import random 
import hashlib
from colour import *
from message import eNB_auth_response_message
import sqliteDatabase
from eNButility.Cipher import AESCipher

class MyOwnPeer2PeerNode (Node):

    # Python class constructor
    def __init__(self, host, port, name):
        super(MyOwnPeer2PeerNode, self).__init__(host, port, name)
        print("MyPeer2PeerNode: Started")
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
        self.process(data, node)
        if self.debug == True:
            print(data)
        if self.logs == True:
            f = open(os.path.join(os.getcwd()+"/logs",self.name+"_logs.txt"), "a")
            f.write(time.asctime( time.localtime(time.time())) + " FROM " + node.name + " to " + self.name + " " + str(data) + "\n")
            f.close()

    def random_with_N_digits(self,n):
        return ''.join(["{}".format(random.randint(0, 9)) for num in range(0, n)])


    def hash(self,a):
        a = hashlib.md5(a.encode())
        return a.hexdigest()

    def xor(self,a,b):
        if len(b) > len(a):
            return self.xor(b, a)
        c = ""
        n = len(a)
        while(len(b)<n): 
            b+=b
        for i in range(n):
            c += chr(ord(a[i])^ord(b[i]))
        return c


    def node_disconnect_with_outbound_node(self, node):
        print("node wants to disconnect with oher outbound node: " + node.id)

    def node_request_to_stop(self):
        print("node is requested to stop!")
        sqliteDatabase.delete(self.id,self.type)

    def process(self, data, node):
        if data["Type"] == "Registration":
            if data["Count"] == 1:
                data["Path"].append(self.id)
                data["Count"] = 2
                n = self.nodes_outbound[0]
                self.send_to_node(n, data)
            
            elif data["Count"] == 5:
                data["Count"] = 6
                for node in self.nodes_inbound:
                    if node.id == data["Path"][-1]:
                        data["Path"].pop()
                        self.send_to_node(node, data)

        elif data["Type"] == "HSS_auth_request" or data["Type"] == "HSS_auth_response":
            if data["Count"] == 1:
                data["Path"].append(self.id)
                data["Count"] = 2
                n = self.nodes_outbound[0]
                self.send_to_node(n, data)
            
            elif data["Count"] == 5:
                data["Count"] = 6
                for n in self.nodes_inbound:
                    if n.id == data["Path"][-1]:
                        data["Path"].pop()
                        self.send_to_node(n, data)

        elif data["Type"] == "Key_Broadcast":
            sav = {
                "PID": data["PID"],
                "hk": data["hk"],
                "session_key": None
            }
            self.buffer[self.hash(data["id"])] = sav
        
        elif data["Type"] == "eNB_auth_request":
            info = self.buffer[self.hash(node.id)]
            hk = info["hk"]

            #Step 1: verify Tc
            dec = AESCipher(hk)
            val = dec.decrypt(data["H_req"]).split("+")
            id = val[0]
            Tc = float(val[1])
            Th = time.time()
            if Th - Tc > 3:
                return
                #Auth failed --> replay attack prone
            
            #step 2: verify V2
            temp = id + "+" + str(Tc)
            r2 = self.xor(data["R2"], self.hash(temp))
            V2 = self.hash(temp+"+"+r2)
            if V2 != data["V2"]:
                return
            
            #Step 3: verify PID
            temp2  = node.id + "+" + self.nodes_outbound[0].id + "+" + self.id
            PID = self.hash(temp2)
            if PID != info["PID"]:
                return

            #Step 4: create session key
            r3 = self.random_with_N_digits(32)
            R3 = self.xor(r3,self.hash(id+"+"+str(Th)))
            self.buffer[self.hash(node.id)]["session_key"] = self.hash(r2 + "+" + r3)
            H_res = dec.encrypt(id + "+" +str(Th)).decode()
            
            #step 5: send response
            msg = eNB_auth_response_message(R3,H_res)
            self.send_to_node(node, msg)

        elif data["Type"] == "Disconnection":
            self.nodes_inbound = []
            time.sleep(4)
            try:
                self.delete_closed_connections()
                print("Connection deleted")
            except Exception as e:
                pass








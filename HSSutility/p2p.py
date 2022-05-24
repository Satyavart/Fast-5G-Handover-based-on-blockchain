'''
Author: Satyavart 
Email: satyavarty591@gmail.com
'''


from HSSutility.node import Node
from Crypto import Random
from Crypto.Cipher import AES
import base64
import hashlib
import time
import json
import os
import csv
import random 
from colour import *
from message import HSS_auth_response_message, broadcast_key
import sqliteDatabase
from random import randint


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
        self.process(data,node)
        if self.debug == True:
            print(data)
        if self.logs == True:
            f = open(os.path.join(os.getcwd()+"/logs",self.name+"_logs.txt"), "a")
            f.write(time.asctime( time.localtime(time.time())) + " FROM " + node.name + " to " + self.name + " " + str(data) + "\n")
            f.close()

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

    def aesencrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def aesdecrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def random_with_N_digits(self,n):
        return ''.join(["{}".format(randint(0, 9)) for num in range(0, n)])

    #Blockchain Ledger
    def register_an_user(self,data):
        #Step 1: Validate user
        #Step 2: create random number
        r = self.random_with_N_digits(32)
        
        #step 3: create Temporary ID
        Tr = time.time()
        val = data["ID"] + "+" + r + "+" + str(Tr)
        TID = self.aesencrypt(val).decode()

        #Step 4: Create initial block of blockchain of a specific user
        val = data["ID"] + "+" + str(Tr)
        B0 = self.hash(val)
        sav = {
            "p_time": None,
            "p_MME": None,
            "blockchain": [B0]
        }
        self.user[data["ID"]] = sav
        self.len_of_blockchain += 1
        #print(self.user)

        #step 5: return tid and r for user validation
        data["Result"] = "success"
        data["TID"] = TID
        data["ID"] = None
        data["r"] = r
        return data

    def authenticate_user(self, data, node):
        data["R0"] = json.loads(data["R0"])
        #step 1: verify time stamp --> avoid replay attack
        if time.time() - data["Tu"] > 3:
            #invalid user .... request drop
            return None
        # print("Step 1 success")
        #step 2: Decrypt TID
        val = self.aesdecrypt(data["TID"]).split('+')
        id = val[0]
        r = val[1]
        Tr = val[2]
        # print("Step 2 success")

        #step 3: Check if user have an active access
        if data["Tu"]-float(Tr) > 135000:
            return None
        # print("Step 3 success")
        
        #step 4: calculate values to verify user by V0
        Ki = self.hash(id + "+" + r)
        r0 = self.xor(self.hash(Ki),data["R0"])
        val = id + "+" + r0 + "+" + str(data["Tu"])
        V0 = self.hash(val)
        if V0 != data["V0"]:
            #Data Tampered --> Request drop
            return None
        # print("Step 4 success")
        
        #Step 5: Verify blockchain ... Ledger part
        previous_block = self.user[id]["blockchain"][-1]
        if self.len_of_blockchain > 1:
            predicted_block = self.hash(self.user[id]["blockchain"][-2] + "+" + Tr)
            if predicted_block != previous_block:
                return None
        else:
            predicted_block = self.hash(id + "+" + Tr)
            if predicted_block != previous_block:
                return None
        # print("Step 5 success")
        
        #Step 6: Create new values
        Bi = self.hash(previous_block+ "+" + Tr)
        ri = self.random_with_N_digits(32)
        val = id + "+" + ri + "+" + Tr
        T = self.aesencrypt(val).decode()
        kih = self.hash(Ki)
        TID_new = self.xor(T,kih)
        r_new = self.xor(ri, kih)
        t_new = time.time()
        hk = self.hash(str(randint(1,100000000))) #handover key
        val = id + "+" + T + "+" + ri + "+" + hk + "+" + str(t_new)
        Vi = self.hash(val)
        HK = self.xor(hk,kih)
        # print("Step 6 success")

        #Step 7: Update values and block addition
        self.user[id]["p_time"] = t_new        
        self.user[id]["p_MME"] = node.name
        self.user[id]["blockchain"].append(Bi)
        print(self.user[id]["blockchain"])
        self.len_of_blockchain += 1
        # print("Step 7 success")

        #step 8: Update value in the message to send
        msg = HSS_auth_response_message(TID_new, r_new, Vi, t_new, HK, data["Path"])
        msg2 = broadcast_key(id,hk)
        return [msg, msg2]

    def process(self, data, prev_node):
        if data["Type"] == "Registration":
            if data["Count"] == 3:
                data = self.register_an_user(data)
                data["Count"] = 4
                for n in self.nodes_inbound:
                    if n.id == data["Path"][-1]:
                        data["Path"].pop()
                        self.send_to_node(n, data)
        
        elif data["Type"] == "HSS_auth_request":
            if data["Count"] == 3:
                # print("data -> "+str(data))
                # print("node -> " +prev_node.id)
                msg = self.authenticate_user(data,prev_node)
                if msg == None:
                    return
                msg1 = msg[0]
                msg2 = msg[1]
                #print(msg1)
                #print(msg2)
                for n in self.nodes_inbound:
                    if n.id == msg1["Path"][-1]:
                        msg1["Path"].pop()
                        self.send_to_node(n, msg1)
                        self.send_to_node(n, msg2)

        
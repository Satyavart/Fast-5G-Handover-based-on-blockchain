'''
Author: Satyavart 
Email: satyavarty591@gmail.com
'''


from MEutility.node import Node
import time
import os
import csv
import hashlib
from MEutility.Cipher import AESCipher
import random 
from colour import *
import sqliteDatabase
from message import *
from random import randint


class MyOwnPeer2PeerNode (Node):

    # Python class constructor
    def __init__(self, host, port, name, home):
        super(MyOwnPeer2PeerNode, self).__init__(host, port, name, home)
        print("MyPeer2PeerNode: Started")
        sqliteDatabase.save(host,port,name,self.id,self.initial_time_stamp,self.home)
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

    def handover(self,des):
        try:
            self.previous_connected_node = self.nodes_outbound[0]
        except Exception as e:
            pass
        self.connect_with_node("127.0.0.1",des)
        self.authenticate(des)
        

    def node_disconnect_with_outbound_node(self, node):
        prRed("node wants to disconnect with oher outbound node: " ,"end")
        print(node.id)

    def node_request_to_stop(self):
        print("node is requested to stop!")
        sqliteDatabase.delete(self.id,self.type)

    def random_with_N_digits(self,n):
        return ''.join(["{}".format(randint(0, 9)) for num in range(0, n)])


    def registration(self):
        message = registration_message(self.id)
        n = self.nodes_outbound[0]
        self.send_to_node(n, message)
    
    def process(self, data, node):
        if data["Type"] == "Registration":
            if data["Result"] == "success":
                prGreen("Registration Successful")
                self.TID = data["TID"]
                self.r = data["r"]

        elif data["Type"] == "HSS_auth_response":
            if data["Result"] == "success":
                #verify data
                Ki = self.hash(self.id + "+" + self.r)
                T = self.xor(data["ETID"],self.hash(Ki))
                r = self.xor(data["ER"],self.hash(Ki))
                hk = self.xor(data["HK"],self.hash(Ki))
                Th = data["T_new"]
                self.hk = hk
                val = self.id + "+" + T + "+" + r + "+" + hk + "+" + str(Th)
                Vi = self.hash(val)
                if Vi != data["Vi"] or time.time()-Th > 3:
                    prRed("HSS Auth Failed")
                prGreen("HSS Auth Successful")
                self.TID = T
                self.r = r
                
                time.sleep(0.1)
                #authenticate with base station
                self.eNB_auth(node)
        
        elif data["Type"] == "eNB_auth_response":
            #step 1: verify time stamp
            enc = AESCipher(self.hk)
            val = enc.decrypt(data["H_res"]).split("+")
            id = val[0]
            Th = val[1]
            if time.time() - float(Th) > 3:
                return
            prGreen("eNB Authentication Successfull")

            #Step 2: Create session key
            r3 = self.xor(data["R3"],self.hash(id + "+" + Th))
            self.session_key = self.hash(self.r2 + "+" + r3)
            prGreen("Hanover Successful")

            #step 3: Remove connection from previous connected base station
            try:
                if self.previous_connected_node != None:
                    self.disconnect_with_node(self.previous_connected_node)
                    self.delete_closed_connections()
                    prRed("Previous Node Disconnected")
            except Exception as e:
                print(e)

            self.previous_connected_node = self.nodes_outbound[0]





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

    def HSS_auth_request(self):
        Ki = self.hash(self.id + "+" + self.r)
        r0 = self.random_with_N_digits(32)
        R0 = self.xor(self.hash(Ki),r0)
        Tu = time.time()
        val = self.id + "+" + r0 + "+" + str(Tu)
        V0 = self.hash(val)
        message = HSS_auth_request_message(self.id,self.TID,R0,V0,Tu)
        return message

    def authenticate(self, des):
        #Inter MME
        if abs(self.previous_connected_node.port-des)>10 or self.session_key == None:
            #Inter MME
            #have to verify with HSS
            message = self.HSS_auth_request()
            #print(message)
            for node in self.nodes_outbound:
                if node.port == des:
                    time.sleep(0.1)
                    self.send_to_node(node, message)
        
        else:
            for node in self.nodes_outbound:
                if node.port == des:
                    self.eNB_auth(node)
                    #Intra MME


    def eNB_auth(self, node):
        enc = AESCipher(self.hk)
        Tc = time.time()
        temp = self.id + "+" + str(Tc)
        H_req = enc.encrypt(temp).decode()
        r2 = self.random_with_N_digits(32)
        self.r2 = r2
        val = self.id + "+" + str(Tc) + "+" + r2
        V2 = self.hash(val)
        R2 = self.xor(self.hash(temp), r2)
        msg = eNB_auth_message(R2,V2,H_req)
        #print(msg)
        self.send_to_node(node, msg)

        



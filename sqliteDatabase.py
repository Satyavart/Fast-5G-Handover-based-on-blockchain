#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Author: Satyavart 
Email: satyavarty591@gmail.com
'''

import sqlite3
import os
from colour import *


# save data of the new node to the sqlite3 database

def save(
    host,
    port,
    name,
    id,
    intial_time_stamp,
    home=None,
    ):

    # pwd = os.getcwd()
    # os.chdir(pwd+"/database")

    try:
        con = sqlite3.connect(os.path.join(os.getcwd() + '/database',
                              'registation.db'))
        cursor = con.cursor()
        data_tuple = (id, name, host, port, intial_time_stamp)
        query = ''

        if name.split('_')[0] == 'ME':
            query = 'INSERT into ME(id,name,ip,port,its,home) VALUES (?,?,?,?,?,?);'
            data_tuple = (
                id,
                name,
                host,
                port,
                intial_time_stamp,
                home,
                )
        elif name.split('_')[0] == 'eNB':
            query = 'INSERT into eNB(id,name,ip,port,its,parent) VALUES (?,?,?,?,?,?);'
            data_tuple = (
                id,
                name,
                host,
                port,
                intial_time_stamp,
                home,
                )
        elif name.split('_')[0] == 'MME':
            query = 'INSERT into MME(id,name,ip,port,its) VALUES (?,?,?,?,?);'
        elif name.split('_')[0] == 'HSS':
            query = 'INSERT into HSS(id,name,ip,port,its) VALUES (?,?,?,?,?);'
        cursor.execute(query, data_tuple)
        con.commit()
        prCyan('Info added to database')
        cursor.close()
    except sqlite3.OperationalError:
        con = sqlite3.connect(os.path.join(os.getcwd() + '/database',
                              'registation.db'))
        cursor = con.cursor()
        if name.split('_')[0] == 'ME':
            query = \
                'CREATE TABLE "ME"("id"	TEXT,"name"	TEXT,"ip" TEXT,"port" INTEGER,"its" REAL,"home" TEXT,PRIMARY KEY("id"));'
        elif name.split('_')[0] == 'eNB':
            query = \
                'CREATE TABLE "eNB" ("id" TEXT,"name" TEXT,"ip" TEXT,"port" INTEGER,"its" REAL,"parent" TEXT,PRIMARY KEY("id"));'
        elif name.split('_')[0] == 'MME':
            query = \
                'CREATE TABLE "MME" ("id" TEXT,"name" TEXT,"ip" TEXT,"port" INTEGER,"its" REAL,PRIMARY KEY("id"));'
        elif name.split('_')[0] == 'HSS':
            query = \
                'CREATE TABLE "HSS" ("id" TEXT,"name" TEXT,"ip" TEXT,"port" INTEGER,"its" REAL,PRIMARY KEY("id"));'
        cursor.execute(query)
        con.commit()
        cursor.close()
        prCyan("Table Didn't exist. Table created")
        save(host, port, name, id, intial_time_stamp, home)
    except sqlite3.Error as error:
        prCyan('Failed to delete reocord from a sqlite table', error)

    # os.chdir(pwd)

# delete data from sqlite3 database after the node is closed

def delete(id, type):

    # pwd = os.getcwd() + "/database"
    # os.chdir(pwd+"/database")

    sql_update_query = ''
    if type == 'ME':
        sql_update_query = """DELETE from ME where id = ?"""
    elif type == 'MME':
        sql_update_query = """DELETE from MME where id = ?"""
    elif type == 'HSS':
        sql_update_query = """DELETE from HSS where id = ?"""
    elif type == 'eNB':
        sql_update_query = """DELETE from eNB where id = ?"""
    try:
        con = sqlite3.connect(os.path.join(os.getcwd() + '/database',
                              'registation.db'))
        cursor = con.cursor()
        cursor.execute(sql_update_query, (id, ))
        con.commit()
        cursor.close()
    except sqlite3.Error as error:
        prCyan('Failed to delete reocord from a sqlite table')
    finally:
        if con:
            con.close()
            prCyan('sqlite connection is closed')


    # os.chdir(pwd)

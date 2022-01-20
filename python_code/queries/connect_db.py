#!/usr/bin/env python3
import mysql.connector
import configparser

# this file is imported by other scripts

# runs query on mysql database.
# details for this database are in the config.ini file
def run_query_db(query):
    # read database settings from ini file
    conf = configparser.ConfigParser()
    conf.read('/home/hdip_proj/config.ini')
    usr = conf['database']['user']
    pwd = conf['database']['password']
    db = conf['database']['db']

    # connect to mysql database
    dbconn = mysql.connector.connect(
        user=usr,
        password=pwd,
        host=usr + '.mysql.localhost',
        database=db)

    mycursor = dbconn.cursor()

    mycursor.execute(query)

    # get results
    results = mycursor.fetchall()

    # clean up connection
    mycursor.close()
    dbconn.close()

    return results

#!/usr/bin/env python3


# script to insert data from json api into database


import configparser
import sys
import json

# import the inserter class for the db format
from insert_data_db import connect_to_db


def main():
    # get data folder information
    conf = configparser.ConfigParser()
    conf.read('/home/hdip_proj/config.ini')
    data_folder = conf['folders']['data']

    # read in json file
    rl = open(data_folder + "nwbb-fxkq.json", 'r')
    json_file = json.load(rl)
    rl.close()

    # establish db connection
    inserter = connect_to_db()

    # loop through file and add anything not already in db
    i = 0
    for data in json_file:
        i += 1
        print("Inserting record", i)

        inserter.insert_incident(data)

    # commit changes
    inserter.dbconn.commit()

    # exit db connection
    inserter.disconnect()
    return


if __name__ == "__main__":
    main()
    sys.exit(0)

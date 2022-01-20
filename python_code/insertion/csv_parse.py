#!/usr/bin/env python3

# this file parses the historical csv file records
# corrects the formatting to match the required format
# and then places each row into the database

import csv
import sys
import datetime
import configparser

# import the inserter class for the db format
from insert_data_db import connect_to_db


# converts San Francisco to san_francisco
# used to make csv field names into json style field names
def snake_case(st):
    st = st.replace(" ", "_")
    return st.lower()


# creates a datetime object from the date given in the csv file
# this datetime object can be used by mysql-connector
# for insertion into the database
def fmt_datetime(st):
    # %I and %p are for 12 hour times
    fmt_str = '%Y/%m/%d %I:%M:%S %p'

    # create date object then return it as iso format string
    date_obj = datetime.datetime.strptime(st, fmt_str)
    return date_obj


def main():
    # get data folder location from config file
    conf = configparser.ConfigParser()
    conf.read('/home/hdip_proj/config.ini')
    data_folder = conf['folders']['data']

    # open the csv file
    csv_file = "Police_Department_Incident_Reports__2018_to_Present.csv"
    f = open(data_folder + csv_file, 'r')
    reader = csv.DictReader(f)

    # get inserter and make db connection
    inserter = connect_to_db()

    # first entry also populates fieldnames for dict
    # so need to read it in then reset file and when we
    # try to read the next record this will be the fieldnames
    # leaving the reader ready to read actual entries
    next(reader)
    f.seek(0)
    next(reader)  # reader is now on first record of csv file

    # because the csv has different field names than json
    # we need to change the headers into snake_case so the database insert
    # functions work
    reader.fieldnames = [snake_case(s) for s in reader.fieldnames]

    i = 0
    for row in reader:
        i += 1

        print("Inserting record", reader.line_num)

        # correctly format the datetime record
        row['incident_datetime'] = fmt_datetime(row['incident_datetime'])

        # insert the record
        inserter.insert_incident(row)

        # only commit after 10k rows due the huge size of the file
        # approx 180k rows
        if i % 10000 == 0:
            inserter.dbconn.commit()

    # commit any changes left over
    inserter.dbconn.commit()

    # clean up
    inserter.disconnect()
    f.close()


if __name__ == "__main__":
    main()
    sys.exit(0)

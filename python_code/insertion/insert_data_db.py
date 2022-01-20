#!/usr/bin/env python3

# This script inserts data into the database
# the inserters check we aren't inserting duplicate, invalid or
# data that we aren't interested in.
#
# This script is used by calling connect_to_db() which will return an
# instance of the Inserter class connected to this projects database.

import mysql.connector
from mysql.connector import errorcode
import configparser
import sys


# handles inserting data into a database when given a record
# can also commit changes to a database this allows us to insert multiple
# records and then commit later, for a large performance improvement
class Inserter:
    def __init__(self, db_connection):
        self.dbconn = db_connection
        self.mycursor = self.dbconn.cursor()

    # run query to get id if it's in table
    def query_id(self, query, vals):
        # if the query somehow fails then exit
        try:
            self.mycursor.execute(query, vals)
        except mysql.connector.Error as err:
            print("{0} Failed: {1}".format(query, err))
            self.disconnect()
            sys.exit(-1)

        res = self.mycursor.fetchone()
        return res

    # insert data and return last row id
    def insert_data(self, ins_query, vals):
        # if the insertion fails just exit
        try:
            self.mycursor.execute(ins_query, vals)
        except mysql.connector.Error as err:
            print("{0} Failed: {1}".format(ins_query, err))
            self.disconnect()
            sys.exit(-1)

        return self.mycursor.lastrowid

    # make sure data is valid for our use
    # ie. contains all the needed entries
    # json contains different names for fields than csv
    def data_is_invalid(self, data):
        needed_items = [
            "incident_datetime",
            "incident_day_of_week",
            "incident_category",
            "incident_subcategory",
            "incident_description",
            "intersection",
            "police_district",
            "analysis_neighborhood",
            "latitude",
            "longitude",
            "row_id"]

        for item in needed_items:
            if item not in data:
                print(item, "is missing from data!")
                return True
            # need to check for null in csv file
            if data[item] == '' or data[item] == "null":
                print(item, "is empty!")
                return True
        return False

    def insert_date_data(self, data):
        #############################
        # Day of Week
        day = data["incident_day_of_week"]
        day_q = ("SELECT id FROM day_of_week WHERE day = %s")
        day_id = self.query_id(day_q, (day,))
        if day_id is None:
            ins_q = ("INSERT INTO day_of_week(day) VALUES( %s )")
            day_id = self.insert_data(ins_q, (day,))
            print("\tinsert date")
        else:
            day_id = day_id[0]

        #############################
        # Date time

        # insert into date table
        # since day of week is inserted above we select for the correct id
        date_time = data["incident_datetime"]
        time_q = ("SELECT id FROM date WHERE date_time = %s")
        time_id = self.query_id(time_q, (date_time,))
        if time_id is None:
            ins_q = ("""
            INSERT INTO date(date_time, day_of_week_id)
                VALUES( %s, %s )""")
            time_id = self.insert_data(ins_q, (date_time, day_id))
            print("\tinsert date_time")
        else:
            time_id = time_id[0]
        return time_id

    def insert_crime_data(self, data):
        #############################
        # Category
        category = data["incident_category"]
        cat_q = ("SELECT id FROM category WHERE name = %s")
        cat_id = self.query_id(cat_q, (category,))

        if cat_id is None:
            ins_q = ("INSERT INTO category(name) VALUES( %s )")
            cat_id = self.insert_data(ins_q, (category,))
            print("\tinsert category")
        else:
            cat_id = cat_id[0]

        #############################
        # Subcategory
        subcategory = data["incident_subcategory"]
        subcat_q = ("""
        SELECT subcategory.id FROM subcategory, category
            WHERE subcategory.name = %s AND category.id = %s
        """)
        subcat_id = self.query_id(subcat_q, (subcategory, cat_id))

        if subcat_id is None:
            ins_q = ("""
            INSERT INTO subcategory(name, category_id)
                VALUES( %s, %s)""")
            subcat_id = self.insert_data(ins_q, (subcategory, cat_id))
            print("\tinsert subcategory")
        else:
            subcat_id = subcat_id[0]

        #############################
        # Description
        description = data["incident_description"]
        desc_q = ("""
        SELECT description.id FROM description, subcategory
            WHERE description.description = %s AND
                subcategory.id = %s""")
        desc_id = self.query_id(desc_q, (description, subcat_id))

        if desc_id is None:
            ins_q = ("""
            INSERT INTO description(description, subcategory_id)
                VALUES(%s, %s)""")
            desc_id = self.insert_data(ins_q, (description, subcat_id))
            print("\tinsert description")
        else:
            desc_id = desc_id[0]
        return desc_id

    def insert_location_data(self, data):
        # COORDS
        # if coords are in db then we can skip other checks

        # only need to query lat and long as the other pieces of data
        # will depend on these
        # floats have 6 decimal places
        lat = "{0:.6f}".format(float(data["latitude"]))
        longi = "{0:.6f}".format(float(data["longitude"]))

        # lat and long are floats so need special checks for comparing them
        location_q = ("""
        SELECT id FROM location
            WHERE ABS(latitude - %s) <= 1e-6 AND
                ABS(longitude - %s) <= 1e-6
        """)
        loc_id = self.query_id(location_q, (lat, longi))

        if loc_id is not None:
            return loc_id[0]

        # Otherwise we go through the rest trying to insert them

        #############################
        # Intersection
        intersection = data["intersection"]
        inter_q = ("SELECT id FROM intersection WHERE name = %s")
        inter_id = self.query_id(inter_q, (intersection,))
        if inter_id is None:
            ins_q = ("INSERT INTO intersection(name) VALUES( %s )")
            inter_id = self.insert_data(ins_q, (intersection,))
            print("\tinsert intersection")
        else:
            inter_id = inter_id[0]

        #############################
        # Police District
        district = data["police_district"]
        dist_q = ("SELECT id FROM police_district WHERE name = %s")
        dist_id = self.query_id(dist_q, (district,))
        if dist_id is None:
            ins_q = ("INSERT INTO police_district(name) VALUES( %s )")
            dist_id = self.insert_data(ins_q, (district,))
            print("\tinsert district")
        else:
            dist_id = dist_id[0]

        #############################
        # Neighbourhood
        neigh = data["analysis_neighborhood"]
        neigh_q = ("SELECT id FROM neighbourhood WHERE name = %s ")
        neigh_id = self.query_id(neigh_q, (neigh,))
        if neigh_id is None:
            ins_q = ("INSERT INTO neighbourhood(name) VALUES( %s )")
            neigh_id = self.insert_data(ins_q, (neigh,))
            print("\tinsert neighbourhood")
        else:
            neigh_id = neigh_id[0]

        #############################
        # Location
        ins_q = ("""
        INSERT INTO location(latitude, longitude, intersection_id,
            police_district_id, neighbourhood_id)
        VALUES( %s, %s, %s, %s, %s )""")
        loc_id = self.insert_data(ins_q,
                                  (lat, longi, inter_id, dist_id, neigh_id))
        print("\tinsert location")
        return loc_id

    def insert_incident_data(self, data, time_id, desc_id, loc_id):

        api_row_id = data["row_id"]
        q = ("SELECT api_row_id FROM incident WHERE api_row_id = %s")

        if self.query_id(q, (api_row_id,)) is None:
            ins_q = ("""
            INSERT INTO incident(api_row_id, date_id, description_id,
                location_id)
            VALUES( %s, %s, %s, %s)""")
            self.insert_data(ins_q, (api_row_id, time_id, desc_id, loc_id))
            print("\tinsert incident")

    # used to avoid inserting duplicate data early
    # rather than checking each part
    def incident_already_in_db(self, data):
        api_row_id = data["row_id"]
        q = ("SELECT api_row_id FROM incident WHERE api_row_id = %s")
        res = self.query_id(q, (api_row_id,))
        return (res is not None)

    # takes dictionary of row and inserts
    def insert_incident(self, data):
        # if data is invalid then skip
        if self.data_is_invalid(data):
            print("Data is invalid!")
            return

        # check we haven't added it already
        if self.incident_already_in_db(data):
            print("Data already inserted!")
            return

        # insert it
        time_id = self.insert_date_data(data)
        desc_id = self.insert_crime_data(data)
        loc_id = self.insert_location_data(data)
        self.insert_incident_data(data, time_id, desc_id, loc_id)

    # call this to clean up the connection before exiting
    def disconnect(self):
        self.mycursor.close()
        self.dbconn.close()


# debug to print the information we need
def print_incident(record):
    print("==================")
    print("Date")
    print("\t", record["incident_datetime"])
    print("\t", record["incident_day_of_week"])

    print("Crime")
    print('\t', record["incident_category"])
    print('\t', record["incident_subcategory"])
    print('\t', record["incident_description"])

    print("Location")
    print('\t', record["intersection"])
    print("\t", record["row_id"])
    print('\t', record["police_district"])
    print('\t', record["analysis_neighborhood"])
    print('\t', record["latitude"])
    print('\t', record["longitude"])


# connect to the database and return an inserter object to be used
def connect_to_db():
    # read in the config for database information
    conf = configparser.ConfigParser()
    conf.read('/home/hdip_proj/config.ini')
    usr = conf['database']['user']
    pwd = conf['database']['password']
    db = conf['database']['db']

    # handle connecting and errors
    # https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
    try:
        db_connection = mysql.connector.connect(
            user=usr,
            password=pwd,
            host=usr + '.mysql.localhost',
            database=db)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    # return an inserter object that is connected to the database
    return Inserter(db_connection)

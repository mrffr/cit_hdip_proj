#!/usr/bin/env python3

# This script downloads the csv file from the API and saves it.

import requests
import configparser
import sys


def main():
    # get location to save csv
    conf = configparser.ConfigParser()
    conf.read('/home/hdip_proj/config.ini')
    data_folder = conf['folders']['data']

    # download csv file
    r = requests.get("https://data.sfgov.org/api/views/wg3w-h783/rows.csv")

    # if request failed then exit
    if r.status_code != 200:
        print(r.status_code, " request failed: ", r.reason)
        sys.exit(-1)

    # write csv file
    csv_file = "Police_Department_Incident_Reports__2018_to_Present.csv"
    f = open(data_folder + csv_file, 'w')
    f.write(r.text)
    f.close()


if __name__ == "__main__":
    main()
    sys.exit(0)

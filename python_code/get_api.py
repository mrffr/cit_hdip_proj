#!/usr/bin/env python3

# This script downloads the JSON file from the san francisco
# API.

import requests
import configparser
import sys


def main():
    # get location to store json file
    conf = configparser.ConfigParser()
    conf.read('/home/hdip_proj/config.ini')
    data_folder = conf['folders']['data']

    # download json
    r = requests.get("https://data.sfgov.org/resource/nwbb-fxkq.json")

    # if request failed then exit
    if r.status_code != 200:
        print(r.status_code, " request failed: ", r.reason)
        sys.exit(-1)

    # write json file to correct location
    f = open(data_folder + "nwbb-fxkq.json", 'w')
    f.write(r.text)
    f.close()


if __name__ == "__main__":
    main()
    sys.exit(0)

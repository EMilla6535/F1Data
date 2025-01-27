import urllib
from urllib.request import urlopen
from urllib.error import HTTPError
import json
import os
import time

def downloadFile(download_url, filename, retries=0):
    try:
        response = urlopen(download_url)
        data_json = json.loads(response.read())
        with open(filename, "w") as outfile:
            json.dump(data_json, outfile)
    except HTTPError as e:
        content = e.read()
        if retries < 4:
            print("Error downloading the data. Waiting 60 seconds.")
            time.sleep(60)
            downloadFile(download_url, filename, retries+1)
        else:
            print("Maximum retries. Check internet connection or file availability.")

def loadDataFromUrl(download_url, retries=0):
    try:
        response = urlopen(download_url)
        data_json = json.loads(response.read())
    except HTTPError as e:
        content = e.read()
        if retries < 4:
            print("Error downloading the data. Waiting 60 seconds.")
            time.sleep(60)
            data_json = loadDataFromUrl(download_url, retries+1)
        else:
            print("Maximum retries. Check internet connection or file availability.")
            data_json = {}
    
    return data_json

def loadDataFromDisk(filepath):
    with open(filepath, 'r') as file:
        data_json = json.load(file)
    return data_json

def updateFile(url, filename, check_for_update=True):
    wait = False
    if not os.path.exists(filename):
        downloadFile(url, filename)
        time.sleep(5)
    elif check_for_update:
        # Check for updates
        offline_data = loadDataFromDisk(filename)
        online_data = loadDataFromUrl(url)
        if len(online_data) > len(offline_data):
            with open(filename, 'w') as outfile:
                json.dump(online_data, outfile)
            time.sleep(5)

def getDriversList(meeting_key: int):
    drivers_url = "https://api.openf1.org/v1/drivers?meeting_key=" + str(meeting_key)
    drivers_in_meeting = loadDataFromUrl(drivers_url)
    drivers = {}
    for item in drivers_in_meeting:
        driver_acronym = item['name_acronym']
        if driver_acronym not in drivers:
            drivers[driver_acronym] = item['driver_number']

    return drivers
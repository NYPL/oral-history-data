# -*- coding: utf-8 -*-

# This script will download all oral history interview and collection metadata directly from the oral history website.
# It will create:
#   - neighborhoods.json and neighborhoods.csv
#   - interviews.json and interviews.csv
#   - individual .json files for each interview which contain more metadata and annotations
# Usage:
#   python get_metadata.py -out "/Volumes/Seagate Backup Plus Drive/oral_history/"

import argparse
import csv
import json
import os
import sys
import urllib2

# Input
parser = argparse.ArgumentParser()
parser.add_argument('-out', dest="OUTPUT_DIR", default="tmp/", help="Path to output directory")
parser.add_argument('-url', dest="BASE_URL", default="http://oralhistory.nypl.org", help="Base URL to pull data from")
parser.add_argument('-overwrite', dest="OVERWRITE", default=False, help="Overwrite existing files")
args = parser.parse_args()

DIR = args.OUTPUT_DIR
INTERVIEW_DIR = DIR + "interviews/"
URL = args.BASE_URL
OVERWRITE = args.OVERWRITE

# Config fields for csv
NEIGHBORHOOD_FIELDS = [
    {"field": "slug", "header": "id"},
    {"field": "title", "header": "title"},
    {"field": "subtitle", "header": "subtitle"},
    {"field": "long_description", "header": "description"},
    {"field": "image.url", "header": "image_url"},
    {"field": "image.thumb.url", "header": "thumb_url"}
]
INTERVIEW_FIELDS = [
    {"field": "slug", "header": "id"},
    {"field": "storyteller_name", "header": "storyteller_name"},
    {"field": "interviewer_name", "header": "interviewer_name"},
    {"field": "summary", "header": "summary"},
    {"field": "url", "header": "audio_url"},
    {"field": "neighborhood.slug", "header": "neighborhood_id"},
    {"field": "notes", "header": "notes"},
    {"field": "place_of_birth", "header": "place_of_birth"},
    {"field": "date_of_birth", "header": "date_of_birth"},
    {"field": "location", "header": "location"},
    {"field": "occupations", "header": "occupations"},
    {"field": "image.url", "header": "image_url"},
    {"field": "image.thumb.url", "header": "thumb_url"}
]

# Make sure sub-directories exist
if not os.path.exists(INTERVIEW_DIR):
    os.makedirs(INTERVIEW_DIR)

def getData(filename, url, overwrite=False):
    # Download the file if not exists or overwrite
    data = None
    if not os.path.isfile(filename) or overwrite:
        print "Downloading %s" % url
        data = json.loads(urllib2.urlopen(url).read())
        with open(filename, 'w') as f:
            json.dump(data, f)

    # Read from file if already downloaded
    if data is None:
        # print "Opening %s" % filename
        with open(filename, 'rb') as f:
            data = json.load(f)

    return data

def toCSV(fields, filename, data, overwrite=False):
    if not os.path.isfile(filename) or overwrite:
        print "Writing to %s" % filename
        headers = [field["header"] for field in fields]
        with open(filename, 'wb') as f:
            fw = csv.writer(f)
            fw.writerow(headers)
            for item in data:
                row = []
                for field in fields:
                    fieldParts = field["field"].split(".")
                    value = ""
                    obj = None
                    for i, fp in enumerate(fieldParts):
                        if obj is None:
                            obj = item[fp]
                        else:
                            obj = obj[fp]
                        if type(obj) is not dict:
                            value = obj
                    row.append(value.encode('utf-8').strip())
                fw.writerow(row)

# First, get the neighborhoods
neighborhoods = getData(DIR + "neighborhoods.json", URL + "/neighborhoods.json", OVERWRITE)
print "Loaded %s neighborhoods" % len(neighborhoods)

# Next, get the interviews
interviews = getData(DIR + "interviews.json", URL + "/interviews.json", OVERWRITE)
interviewCount = len(interviews)
print "Loaded %s interviews" % interviewCount

# Download each interview
interviewsData = []
for interview in interviews:
    url = interview["url"]
    filename = INTERVIEW_DIR + interview["slug"] + ".json"
    interviewData = getData(filename, url, OVERWRITE)
    interviewsData.append(interviewData)

# convert neighborhoods to csv
toCSV(NEIGHBORHOOD_FIELDS, DIR + "neighborhoods.csv", neighborhoods, OVERWRITE)
toCSV(INTERVIEW_FIELDS, DIR + "interviews.csv", interviewsData, OVERWRITE)

print "Done."

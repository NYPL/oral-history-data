# -*- coding: utf-8 -*-

# This script will download all oral history interview and collection metadata and assets directly from the oral history website.
# It will create:
#   - neighborhoods.json and neighborhoods.csv
#   - interviews.json and interviews.csv
#   - individual .json files for each interview which contain more metadata and annotations
#   - write images and audio to ./audio and ./images folders
# Usage:
#   python get_metadata_and_assets.py -out "/Volumes/Seagate Backup Plus Drive/oral_history/"

import argparse
import csv
import errno
import json
import mutagen
from mutagen.mp3 import MP3
import os
import sys
import urllib
import urllib2

# Input
parser = argparse.ArgumentParser()
parser.add_argument('-out', dest="OUTPUT_DIR", default="tmp/", help="Path to output directory")
parser.add_argument('-url', dest="BASE_URL", default="http://oralhistory.nypl.org", help="Base URL to pull data from")
parser.add_argument('-image', dest="BASE_IMAGE_URL", default="https://oral-history.s3.amazonaws.com/", help="Base asset URL to pull data from")
parser.add_argument('-audio', dest="BASE_AUDIO_URL", default="https://s3.amazonaws.com/oral-history/", help="Base asset URL to pull data from")
parser.add_argument('-overwrite', dest="OVERWRITE", default=False, help="Overwrite existing files")
args = parser.parse_args()

DIR = args.OUTPUT_DIR
INTERVIEW_DIR = DIR + "interviews/"
AUDIO_DIR = DIR + "audio/"
URL = args.BASE_URL
IMAGE_URL = args.BASE_IMAGE_URL
AUDIO_URL = args.BASE_AUDIO_URL
OVERWRITE = args.OVERWRITE

# Config fields for csv
NEIGHBORHOOD_FIELDS = [
    {"field": "slug", "header": "id"},
    {"field": "title", "header": "title"},
    {"field": "subtitle", "header": "subtitle"},
    {"field": "long_description", "header": "description"},
    {"field": "image.url", "header": "image_url"},
    {"field": "image.thumb.url", "header": "thumb_url"},
    {"field": "interview_count", "header": "interview_count"},
    {"field": "duration", "header": "duration"}
]
INTERVIEW_FIELDS = [
    {"field": "slug", "header": "id"},
    {"field": "storyteller_name", "header": "storyteller_name"},
    {"field": "interviewer_name", "header": "interviewer_name"},
    {"field": "summary", "header": "summary"},
    {"field": "url", "header": "audio_url"},
    {"field": "neighborhood.slug", "header": "collection_id"},
    {"field": "neighborhood.title", "header": "collection_title"},
    {"field": "neighborhood.subtitle", "header": "collection_subtitle"},
    {"field": "notes", "header": "notes"},
    {"field": "place_of_birth", "header": "place_of_birth"},
    {"field": "date_of_birth", "header": "date_of_birth"},
    {"field": "location", "header": "location"},
    {"field": "occupations", "header": "occupations"},
    {"field": "image.url", "header": "image_url"},
    {"field": "image.thumb.url", "header": "thumb_url"},
    {"field": "duration", "header": "duration"}
]

# Make sure sub-directories exist
if not os.path.exists(INTERVIEW_DIR):
    os.makedirs(INTERVIEW_DIR)

def mkdirP(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

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

def getAsset(filename, url, overwrite=False):
    # Download the file if not exists or overwrite
    data = None
    if not os.path.isfile(filename) or overwrite:
        print "Downloading %s to %s" % (url, filename)
        urllib.urlretrieve(url, filename)

def getAudioFilename(url):
    parts = url.split("/")
    filename = urllib.unquote_plus(parts[-1])
    return AUDIO_DIR + filename

def getImageFilename(url):
    filename = url.replace("https://oral-history.s3.amazonaws.com/","")
    if "https://s3.amazonaws.com/" in url:
        filename = url.replace("https://s3.amazonaws.com/oral-history/","")
    parts = filename.split("/")
    dirs = "/".join(parts[:-1])
    mkdirP(dirs)
    filename = urllib.unquote_plus(parts[-1])
    return DIR + dirs + "/" + filename

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
                    if isinstance(value, (int, float)):
                        row.append(value)
                    else:
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

# Download assets
for i, neighborhood in enumerate(neighborhoods):
    imageFilename = getImageFilename(neighborhood["image"]["url"])
    thumbFilename = getImageFilename(neighborhood["image"]["thumb"]["url"])

    # download images
    getAsset(imageFilename, neighborhood["image"]["url"], OVERWRITE)
    getAsset(thumbFilename, neighborhood["image"]["thumb"]["url"], OVERWRITE)

    neighborhoods[i]["image_filename"] = imageFilename
    neighborhoods[i]["thumb_filename"] = thumbFilename

for i, interview in enumerate(interviewsData):
    audioFilename = getAudioFilename(interview["url"])
    imageFilename = getImageFilename(interview["image"]["url"])
    thumbFilename = getImageFilename(interview["image"]["thumb"]["url"])

    # download audio
    getAsset(audioFilename, interview["url"], OVERWRITE)
    # download images
    getAsset(imageFilename, interview["image"]["url"], OVERWRITE)
    getAsset(thumbFilename, interview["image"]["thumb"]["url"], OVERWRITE)

    interviewsData[i]["audio_filename"] = audioFilename
    interviewsData[i]["image_filename"] = imageFilename
    interviewsData[i]["thumb_filename"] = thumbFilename

# Add durations to each interview
for i, interview in enumerate(interviewsData):
    if ("duration" not in interview) or interview["duration"] <= 0:
        try:
            audio = MP3(interview["audio_filename"])
            interviewsData[i]["duration"] = audio.info.length # duration in seconds
        except mutagen.mp3.HeaderNotFoundError:
            print "Audio error with %s" % interview["audio_filename"]
            interviewsData[i]["duration"] = 0
            pass

# Add interview counts to each neighborhood
for i, neighborhood in enumerate(neighborhoods):
    nInterviews = [interview for interview in interviewsData if interview["neighborhood_id"]==neighborhood["id"]]
    interviewCount = len(nInterviews)
    neighborhoods[i]["interview_count"] = interviewCount
    neighborhoods[i]["duration"] = sum([interview["duration"] for interview in nInterviews])

# convert neighborhoods to csv
toCSV(NEIGHBORHOOD_FIELDS, DIR + "neighborhoods.csv", neighborhoods, OVERWRITE)
toCSV(INTERVIEW_FIELDS, DIR + "interviews.csv", interviewsData, OVERWRITE)

print "Done."

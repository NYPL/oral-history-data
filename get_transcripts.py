# -*- coding: utf-8 -*-

# This script will download all oral history interview transcripts directly from the oral history transcript website.
# It will create:
#   - A manifest `transcripts.json` file with links to each interview transcripts
#   - Individual folders for each interview that contains three formats of transcripts (`.json`, `.txt`, `.vtt`)
#   - `.json` files contain all the of the edits, while the `.txt` and `.vtt` contain the "best guess" transcriptions for each line
# Usage:
#   python get_transcripts.py -out "/Volumes/Seagate Backup Plus Drive/oral_history/"

import argparse
import csv
import json
import os
import sys
import urllib2

# Input
parser = argparse.ArgumentParser()
parser.add_argument('-out', dest="OUTPUT_DIR", default="tmp/", help="Path to output directory")
parser.add_argument('-url', dest="BASE_URL", default="http://transcribe.oralhistory.nypl.org", help="Base URL to pull data from")
parser.add_argument('-overwrite', dest="OVERWRITE", default=False, help="Overwrite existing files")
parser.add_argument('-edits', dest="EDITS", default=True, help="Include edits?")
args = parser.parse_args()

DIR = args.OUTPUT_DIR
TRANSCRIPT_DIR = DIR + "transcripts/"
URL = args.BASE_URL
OVERWRITE = args.OVERWRITE
EDITS = args.EDITS

# Make sure sub-directories exist
if not os.path.exists(TRANSCRIPT_DIR):
    os.makedirs(TRANSCRIPT_DIR)

def getData(filename, url, overwrite=False, downloadOnly=False):
    # Download the file if not exists or overwrite
    data = None
    if not os.path.isfile(filename) or overwrite:
        print "Downloading %s" % url
        data = urllib2.urlopen(url).read()
        with open(filename, 'w') as f:
            f.write(data)

    # Read from file if already downloaded
    if data is None and not downloadOnly:
        # print "Opening %s" % filename
        with open(filename, 'rb') as f:
            data = json.load(f)

    return data

# Download transcript manifest
transcripts = getData(DIR + "transcripts.json", URL + "/transcript_files.json", OVERWRITE)
transcripts = transcripts["entries"]
print "Retrieved %s transcripts" % len(transcripts)

for t in transcripts:
    name = t["id"]
    transcriptDir = TRANSCRIPT_DIR + name + "/"

    # Make sure sub-directories exist
    if not os.path.exists(transcriptDir):
        os.makedirs(transcriptDir)

    # Download files
    for frmt, url in t["files"].iteritems():
        filename = transcriptDir + name + "." + frmt
        if frmt == "json" and EDITS:
            url += "?edits=1"
        transcript = getData(filename, url, OVERWRITE, True)

print "Done."

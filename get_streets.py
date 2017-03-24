# -*- coding: utf-8 -*-
# Usage:
#  python get_streets.py data/document_texts_2016-08-15.csv data/documents_2016-08-15.csv analyses/streets.csv

import csv
import datetime
import re
import sys

if len(sys.argv) < 3:
  print "Usage: %s <inputfile texts csv> <inputfile docs csv> <outputfile streets csv>" % sys.argv[0]
  sys.exit(1)

INPUT_FILE_TEXTS = sys.argv[1]
INPUT_FILE_DOCS = sys.argv[2]
OUTPUT_FILE = sys.argv[3]

patterns = [
  # '([a-z0-9 ]+ (?:street|st|avenue|ave|rd|road|ln|lane|circle|square|park|place))(?: |$)'
  r"\b[a-z0-9 ]+ (?:street|st|avenue|ave|circle|square)\b"
]

def readCSV(filename):
  items = []
  with open(filename, 'rb') as f:
    rows = csv.reader(f, delimiter=',')
    headers = next(rows, None) # remove header
    # populate list
    for row in rows:
        item = {}
        for i, h in enumerate(headers):
          val = row[i]
          if val.isdigit():
            val = int(val)
          item[h] = val
        items.append(item)
    print "Read %s rows from file %s" % (len(items), filename)
    return items

texts = readCSV(INPUT_FILE_TEXTS)
docs = readCSV(INPUT_FILE_DOCS)

streets = []
for text in texts:
  string = str(text['text']).lower().strip() # lowercase, strip trailing whitespace
  # string = re.sub('[^a-z0-9, ]+', ' ', string) # strip non alpha-numeric
  ' '.join(string.split()) # strip redundant whitepace
  for pattern in patterns:
    matches = re.findall(pattern, string)
    if matches and len(matches) > 0:
      doc = docs[text['document']]
      for match in matches:
        if match:
          start = int(round(text['start']/1000))
          end = int(round(text['end']/1000))
          hhmmss = str(datetime.timedelta(seconds=start))
          streets.append([
            doc['index'],
            match,
            start,
            end,
            doc['url'] + '#' + hhmmss
          ])

print "Found %s streets" % len(streets)

with open(OUTPUT_FILE, 'wb') as f:
  w = csv.writer(f)
  w.writerow(['document', 'text', 'start', 'end', 'url'])
  for row in streets:
    w.writerow(row)
  print "Successfully wrote to file %s" % OUTPUT_FILE

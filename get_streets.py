# -*- coding: utf-8 -*-
# Usage:
#  python get_streets.py data/document_texts_2016-08-15.csv analyses/streets.csv

import csv
import re
import sys

if len(sys.argv) < 2:
  print "Usage: %s <inputfile texts csv> <outputfile streets csv>" % sys.argv[0]
  sys.exit(1)

INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]

patterns = [
  # '([a-z0-9 ]+ (?:street|st|avenue|ave|rd|road|ln|lane|circle|square|park|place))(?: |$)'
  '([a-z0-9, ]+ (?:street|st|avenue|ave|circle|square))(?: |$)'
]

texts = []
with open(INPUT_FILE, 'rb') as f:
  rows = csv.reader(f, delimiter=',')
  headers = next(rows, None) # remove header
  # populate text list
  for row in rows:
    text = {}
    for i, h in enumerate(headers):
      val = row[i]
      if val.isdigit():
        val = int(val)
      text[h] = val
    texts.append(text)
  print "Read %s rows from file %s" % (len(texts), INPUT_FILE)

streets = []
for text in texts:
  string = str(text['text']).lower().strip() # lowercase, strip trailing whitespace
  ' '.join(string.split()) # strip redundant whitepace
  string = re.sub('[^a-z0-9, ]+', '', string) # strip non alpha-numeric
  for pattern in patterns:
    m = re.search(pattern, string)
    if m:
      matches = m.groups()
      for match in matches:
        if match:
          streets.append([
            text['document'],
            match,
            text['start'],
            text['end']
          ])

print "Found %s streets" % len(streets)

with open(OUTPUT_FILE, 'wb') as f:
  w = csv.writer(f)
  w.writerow(['document', 'text', 'start', 'end'])
  for row in streets:
    w.writerow(row)
  print "Successfully wrote to file %s" % OUTPUT_FILE

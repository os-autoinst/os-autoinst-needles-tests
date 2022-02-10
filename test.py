#!/usr/bin/python3

import os
import sys
import re
import json

scriptdir = os.path.dirname(os.path.realpath(__file__))
needledir = os.path.join(scriptdir, "..")

returncode = 0

def error(msg):
    global returncode
    returncode = 1
    print(msg, file=sys.stderr)

# Get all needles
needles = set()
for f in os.listdir(needledir):
    if f.endswith('.json') or f.endswith('.png'):
        needle, ext = f.rsplit('.', 1)
        needles.add(needle)

# Check for missing parts
for needle in sorted(needles):
    jsonfile = os.path.join(needledir, needle + '.json')
    pngfile = os.path.join(needledir, needle + '.png')

    # Check for file existence
    if not os.path.isfile(jsonfile):
        error("Needle '{}' is missing its JSON file!".format(needle))
        continue # parsing the json makes no sense

    if not os.path.isfile(pngfile):
        error("Needle '{}' is missing its PNG file!".format(needle))

    # Check JSON content
    n = {}
    with open(jsonfile) as f:
        n = json.load(f)

    # Extract properties, we support legacy type with plain tags
    # properties: [tag1, tag2]
    # or new format with name-value pairs
    # properties: [{name: tag1, value: abc}]
    prop_names = map(lambda p: p.get('name') if type(p) is dict else p, n.get('properties', []))

    # Check if bugref is in name if workaround tag exists
    if 'workaround' in prop_names and not re.search(r'((poo|bsc|bnc|boo|kde)#?[A-Z0-9]+|jsc#?[A-Z]+-[0-9]+)', needle):
        error("Needle '{}' includes a workaround tag but has no bug-ID in filename!".format(needle))

    # Check if multiple areas with type=click exist in the same needle
    area_count = len([a for a in n['area'] if a['type'] == 'click'])
    if area_count > 1:
        error("Needle '{}' has {} areas with type=click while only one is allowed!".format(needle, area_count))

    # Check if name contains timestamp
    timestamp = re.sub(r"_.*$", '', re.sub(r"[_-][0-9]{1,2}$", '', needle).split("-")[-1])
    if not timestamp.isnumeric() or len(timestamp) < 8 or int(timestamp) < 20130000:
        error("Needle '{}' missing or invalid timestamp!".format(needle))

    # Check if needle contains duplicate tags
    if len(n['tags']) != len(set(n['tags'])):
        error("Needle '{}' has duplicate tags!".format(needle))


sys.exit(returncode)

import os
import sys
import re
import json

scriptdir = os.path.dirname(os.path.realpath(__file__))
needledir = os.path.abspath(os.path.join(scriptdir, ".."))

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
        error(f"Needle '{needle}' is missing its JSON file!")
        continue # parsing the json makes no sense

    if not os.path.isfile(pngfile):
        error(f"Needle '{needle}' is missing its PNG file!")

    # Check JSON content
    n = {}
    with open(jsonfile) as f:
        n = json.load(f)

    # Check if workaround tag exists if bugref is in name or if there is a reason in json file
    properties = n.get('properties', [])
    if properties is not None:
        workaround_found = False
        for p in properties:
            if isinstance(p, str) and p == 'workaround':
                if re.search(r'((poo|bsc|bnc|boo|kde)#?[A-Z0-9]+|jsc#?[A-Z]+-[0-9]+)', needle):
                    workaround_found = True
                break
            elif isinstance(p, dict) and p.get('name') == 'workaround':
                if p.get('value'):
                    workaround_found = True
                break
        if not workaround_found:
            error(f"Needle '{needle}' includes a workaround tag but has no bug-ID in filename or reason in json file!")

    # Check if multiple areas with type=click exist in the same needle
    area_count = len([a for a in n.get('area', []) if a.get('type') == 'click'])
    if area_count > 1:
        error(f"Needle '{needle}' has {area_count} areas with type=click while only one is allowed!")

    # Check if name contains timestamp
    timestamp = needle.split('-')[-1]
    if not timestamp.isnumeric() or len(timestamp) < 8 or int(timestamp) < 20130000:
        error(f"Needle '{needle}' is missing or has an invalid timestamp!")

    # Check if needle contains duplicate tags
    if len(set(n.get('tags', []))) != len(n.get('tags', [])):
        error(f"Needle '{needle}' has duplicate tags!")

sys.exit(returncode)

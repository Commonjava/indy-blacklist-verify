#!/usr/bin/env python

import requests
import os
import time
from hashlib import sha1
from ruamel.yaml import YAML

CONFIG_DIR = "/opt/config"
INFILE='infile'
OUTFILE = 'outfile'
DONEFILE = 'donefile'
REPO='repo'
URL = 'url'

# outfile='/opt/data/content-verify/checked.lst'
# infile='/opt/data/content-verify/blacklisted-artifacts.csv'

config = {}
for filename in os.listdir(CONFIG_DIR):
    if filename.startswith('.'):
        continue

    print(f"Reading configmap file: {filename}")
    with open(os.path.join(CONFIG_DIR, filename)) as f:
        v = f.read()
        config[filename] = v


infile = config[INFILE]
outfile = config[OUTFILE]
donefile = config[DONEFILE]

repo = config[REPO].replace(':', '/')

url = config[URL]
if url.startswith('/'):
    url = url[1:]


print(f"""USING CONFIGURATION:
----------------------------------------    
input file = {infile}
output file = {outfile}
done (marker) file = {donefile}

Indy URL = {url}
Indy repo = {repo}
----------------------------------------    


""")

if not os.path.exists(donefile):
    processed = []
    if os.path.exists(outfile):
        with open(outfile) as f:
            processed = [line.rstrip().split(':')[0] for line in f.readlines() if 'ERROR' not in line]  

    while not os.path.exists(infile):
        print("No input file yet. Waiting 10s...")
        time.sleep(10)

    with open(infile) as f:
        for line in f:
            parts = line.rstrip().split(',')
            path = parts[0]
            if path.startswith('/'):
                path = path[1:]

            badsum = parts[1]

            if path in processed:
                print(f"Skipping: {path}")
                continue

            print(f"Checking: {path}")
            with requests.get(f"{url}/api/content/{repo}/{path}", stream=True) as resp:
                if resp.status_code == 404:
                    result = "MISSING"
                elif resp.status_code != 200:
                    result = f"ERROR {resp.status_code}"
                else:
                    realsum = sha1()
                    for chunk in resp.iter_content(chunk_size=16384): 
                        if chunk: # filter out keep-alive new chunks
                            realsum.update(chunk)

                    realsum = realsum.hexdigest()
                    if realsum == badsum:
                        result = "MATCH"
                    else:
                        result = "MISMATCH"

            processed.append(path)
            with open(outfile, 'a') as f:
                f.write(f"{path}:{result}\n")

    # print(f"Removing input file {infile}")
    # os.remove(infile)
    with open(donefile, 'w') as f:
        f.write("DONE")

print("Finished. Sleeping so results can be extracted...")
while True:
    time.sleep(10)

"""Verify the live Pages build, including stale or incorrectly published artifacts."""
import json
import os
from pathlib import Path
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

root = Path(__file__).resolve().parents[1]
expected = json.loads((root / 'dist/build-info.json').read_text())
url = os.environ['PAGE_URL'].rstrip('/') + '/build-info.json?run=' + expected['run'] + '-' + expected['attempt']
for attempt in range(18):
    try:
        with urlopen(Request(url, headers={'Cache-Control': 'no-cache'}), timeout=15) as response:
            actual = json.load(response)
        if actual == expected:
            print('Verified the current build is live at ' + os.environ['PAGE_URL'])
            break
        print('Waiting for current build; live metadata: ' + str(actual), flush=True)
    except (URLError, ValueError) as error:
        print('Waiting for Pages propagation: ' + str(error), flush=True)
    if attempt == 17:
        raise SystemExit('Pages returned a stale or missing build after deployment.')
    time.sleep(5)

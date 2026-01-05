# Authentik-Enum
Simple Python3 Script to Enumerate Authentik Version

## How it works

Authentik uses versioned script includes (see [here](https://github.com/goauthentik/authentik/blob/bc24815ae6c8181216b88daeb0e8825aa7b17f7b/authentik/core/templates/if/admin.html#L6)).

<img width="1938" height="603" alt="image" src="https://github.com/user-attachments/assets/834628f1-1cdc-465b-94b8-af1a92d5b06b" />

This allows for unauthenticated version enumerations by file existence testing. Basically get all release versions from Github, then try to fetch each versioned JS file and display the result. If an exact versioned script was found (200 OK), you have enumerated the exact Authentik version in use.

## How to run

````bash
python authentik-enum.py -h
                                              
usage: authentik-enum.py [-h] [--base-url BASE_URL] [--repo REPO] [--timeout TIMEOUT] [--sleep SLEEP] [--all] [--include-404] [--verbose]

Find (or enumerate) authentik AdminInterface-{version}.js and print HTTP status + MD5.

options:
  -h, --help           show this help message and exit
  --base-url BASE_URL  Base URL, e.g. https://sso.example.com (default: None)
  --repo REPO          GitHub repo to query for releases (default: goauthentik/authentik)
  --timeout TIMEOUT    Network timeout (seconds) (default: 30.0)
  --sleep SLEEP        Sleep between requests (seconds) (default: 0.0)
  --all                Do not stop at first hit; enumerate all versions (default: False)
  --include-404        Print 404 rows (otherwise they are skipped) (default: False)
  --verbose            Print checked versions to STDERR (default: False)
````

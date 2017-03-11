#!/usr/bin/env python
"""A script to help with local testing of buildbot, before ansiblizing a remote buildbot master."""
import yaml
import json

secrets = yaml.load(open('secrets.yml')).get("buildbot_secrets")

with open('roles/buildbot/files/secrets.json', 'w') as s:
    json.dump(secrets, s)

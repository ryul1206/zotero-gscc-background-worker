# Python >= 3.6
from pyzotero import zotero
import requests
import yaml
import json

# Read the API key from a file
# with open('secret_api_key.txt', 'r') as f:
#     api_key = f.read().strip()
# with open('secret_user_id.txt', 'r') as f:
#     user_id = f.read().strip()
with open('secret_cfg.yml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

user_id = cfg['user_id']
api_key = cfg['api_key']

z = zotero.Zotero(user_id, 'user', api_key)
items = z.top(limit=10)

for item in items:
    print("Item: %s | Key: %s" % (item['data']['title'], item['key']))

# Discord style webhook
headers = {'Content-Type': 'application/json'}
data = {'content': 'Hello World'}
r = requests.post(cfg['discord_webhook'], headers=headers, json=data)
print(r.text)

# # Slack style webhook
# headers = {'Content-Type': 'application/json'}
# data = {'text': 'Hello World'}
# r = requests.post(cfg['slack_webhook'], headers=headers, json=data)
# print(r.text)

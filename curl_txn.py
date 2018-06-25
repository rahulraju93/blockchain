import requests
import json

payload= {"transaction":{"from":"n1FF1nz6tarkDVwWQkMnnwFPuPKUaQTdptE","to":"n1UVyFeu6fr4YJVf4LFQQTgS9WsisYmtZee", "value":"1000000000000000000","nonce":20,"gasPrice":"1000000","gasLimit":"2000000"},"passphrase":"passphrase"}

r=requests.post("http://localhost:8685/v1/admin/transactionWithPassphrase", data=json.dumps(payload))

print "r.text : ", r.json()


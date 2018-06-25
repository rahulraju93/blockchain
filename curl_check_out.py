#curl -i -H 'Accept: application/json' -X POST http://localhost:8685/v1/admin/transactionWithPassphrase -H 'Content-Type: application/json' -d '{}'


import requests
import json

payload= {"transaction":{"from":"n1FF1nz6tarkDVwWQkMnnwFPuPKUaQTdptE","to":"n1i3ToCvRr85Mfu3CRH7Bz4tuGGgrHaacn2", "value":"100","nonce":8,"gasPrice":"1000000","gasLimit":"2000000","contract":{"function":"takeout","args":"[150]"}}, "passphrase": "passphrase"}

r=requests.post("http://localhost:8685/v1/admin/transactionWithPassphrase", data=json.dumps(payload))

print "r.text : ", r.json()
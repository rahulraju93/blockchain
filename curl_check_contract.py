import requests
import json

payload= {"hash" : "341efae32d9af34772cd1699310d03f961c6280c3f476c38d5d2da310ab0222c"}

r=requests.post("http://localhost:8685/v1/user/getTransactionReceipt", data=json.dumps(payload))

print "r.text : ", r.text
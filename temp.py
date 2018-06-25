import requests
import json

payload= {"hash" : "aaebb86d15ca30b86834efb600f82cbcaf2d7aaffbe4f2c8e70de53cbed17889"}

r=requests.post("http://localhost:8685/v1/user/getTransactionReceipt", data=json.dumps(payload))

print "r.text : ", r.text
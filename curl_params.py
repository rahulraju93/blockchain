#curl -i -H 'Content-Type: application/json' -X POST http://localhost:8685/v1/user/accountstate -d '{"address":"n1i3ToCvRr85Mfu3CRH7Bz4tuGGgrHaacn2"}'

import requests
import json

payload= {"address":"n1Z3ybkR1UE7eVh53SEDT5fctLaRoNyYBUJ"}

r=requests.post("http://localhost:8685/v1/user/accountstate", data=json.dumps(payload))

#print "r.text : ", r.json()

r = r.json()
print r['result']['nonce']
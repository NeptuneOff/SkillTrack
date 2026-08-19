import json, urllib.request
API='http://localhost:8000'
body=json.dumps({'email':'demo@skilltrack.dev','password':'DemoPassword123!'}).encode()
req=urllib.request.Request(API+'/auth/login',data=body,headers={'Content-Type':'application/json'})
token=json.loads(urllib.request.urlopen(req).read())['access_token']
req=urllib.request.Request(API+'/dashboard',headers={'Authorization':'Bearer '+token})
print(json.loads(urllib.request.urlopen(req).read()))

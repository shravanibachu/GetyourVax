import pymongo
import requests
conn = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = conn["data"]
mycol = mydb["states"]
headers = {'user-agent': "EdgeHTML/Blink"}
r = requests.get('https://cdn-api.co-vin.in/api/v2/admin/location/states',headers=headers)
mycol.insert_many(r.json()["states"])
print(len(r.json()["states"]))
count = 0
mycol2 = mydb["districts"]
for x in r.json()["states"]:
    res = requests.get('https://cdn-api.co-vin.in/api/v2/admin/location/districts/'+str(x["state_id"]), headers=headers)
    res = res.json()["districts"]
    for x in res:
        x["district_name"] = x["district_name"].lower()
    mycol2.insert_many(res)
    count+=len(res)
print("Done Successfully..!")
print(count)
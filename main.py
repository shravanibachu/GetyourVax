import json
import logging
import pymongo
from flask import Flask,request,render_template
import geocoder
from geopy.distance import geodesic
import requests
app = Flask(__name__)
conn = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = conn["data"]
mycol2 = mydb["districts"]
key_token = ''#bing key token
map_box_token = ""#mapbox key

def helper1(dict1):
    for x in dict1:
        address =  x["name" ] + ", " + x["block_name"]+", "+x["district_name"]+", "+x["state_name"]
        details = geocoder.mapbox(address, key = map_box_token)
        details = details.json
        lat = details['lat']
        lon = details['lng']
        if(lat and lon):
            x['lat'] = lat
            x['long'] = lon
    return dict1

def helper(dict1,user):
    list1 = []
    user = ""+str(user[0])+","+str(user[1])
    for x in dict1:
        lat = x['lat']
        long = x['long']
        dest = str(lat)+","+str(long)
        params = {
	        'origins' : user ,
            'destinations' : dest,
            'key' : key_token,
            'travelMode' : 'driving'
            }
        a = requests.get("https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?",params).json()
        d = a["resourceSets"][0]['resources'][0]['results'][0]['travelDistance']

        list1.append((x,d))
    list1.sort(key = lambda x : (x[1]))
    results = []
    for x in list1:
        x[0]["distance"] = x[1]
        results.append(x[0])
    return results

def filter(resul,vaccine):
    results = []
    for x in resul:
        if(x["vaccine"].lower().strip()==vaccine.lower().strip()):
            results.append(x)
    return results

@app.route('/',methods = ["GET","POST"])
def hello_world():
    if(request.method=="POST"):
        number = request.form.get("name")
        date = request.form.get("date")
        latt = float(request.form.get("lattitude"))
        long = float(request.form.get("longitude"))
        date = date[8:10]+"-"+ date[5:7] +"-"+date[:4]
        vaccine = request.form.get("Vaccines")
        headers = {'user-agent': "EdgeHTML/Blink"}
        key = number.lower()
        temp_result = mycol2.find({"district_name" : key})
        name = ""
        for nam in temp_result:
            name = nam["district_id"]
            break
        if(not name):
            return "Enter Valid Details"
        name =str(name)
        result = requests.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id=' + name + '&date=' + date,headers=headers)
        result = result.json()["sessions"]
        result = filter(result,vaccine)
        result = helper1(result)
        #print(result)
        result = helper(result,(latt,long))
        return render_template("result.html",result = result)

        
    else:
        return render_template("index.html")
if __name__=="__main__":
    app.run(debug=True)
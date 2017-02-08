import requests
import numpy as np
import csv
import sqlite3
import json

#hard code name of files
#open file
#geolcate address
#add relevant information to database

#setsebool -P httpd_can_network_connect_db on


def import_file(db, file, addr, field):
	"""use this to import data into the db"""
	conn = sqlite3.connect(db)
	c = conn.cursor()
	with open(file) as csvfile:
		reader = csv.DictReader(csvfile)
		procid = 1
		for row in reader:
			#query = "http://localhost/nominatim/search?q=%s,%s,%s,%s&format=json&polygon=1&addressdetails=1" %(row["Street  Address"], row["City"], row["State"], row["Zip Code"])
			req = "http://nominatim.openstreetmap.org/search?q=%s,%s,%s&format=json&polygon=1&addressdetails=1" %(row["Street  Address"], row["City"], row["State"])
			resp = requests.get(req)
			outp = json.loads(resp.text)
			lat = outp[0]['lat']
			lon = outp[0]['lon']
			c.execute('INSERT INTO proc VALUES (?,?,?,?)', (procid,lon,lat,row[field],) )
			procid =procid+1

	conn.commit()
	return


def geolocate(addr):
	#some how query the server
	#return a long and a lat coordinate
	return

if __name__ == "__main__":
	import_file("db/test.db","input/test.csv",["Street  Address","City","State","Zip"],"Commodity Listing")
	#req= "http://nominatim.openstreetmap.org/search?q=%s,%s,%s,%s&format=json&polygon=1&addressdetails=1"
	#outp = requests.get(req)
	#fin = json.loads(outp.text)
	#print(fin[0]['lat'])
	#print(fin['lat'])
	#print(fin['long'])
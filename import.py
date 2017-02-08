import requests
import numpy as np
import csv
import sqlite3
import json
import string



def import_proc(db, file):
	"""use this to import processors into the data into the db"""
	conn = sqlite3.connect(db)
	c = conn.cursor()
	with open(file) as csvfile:
		reader = csv.DictReader(csvfile)
		procid = 1
		for row in reader:
			addr = "%s,%s,%s" %(row["Street  Address"], row["City"], row["State"])
			lat,lon = geolocate(addr)
			c.execute('INSERT INTO proc VALUES (?,?,?,?)', (procid,lat,lon,row["Commodity Listing"],) )
			procid =procid+1
	conn.commit()
	return


def import_store(db,file):
	"""use this to import store data into the db"""
	conn = sqlite3.connect(db)
	c = conn.cursor()
	with open(file) as csvfile:
		reader = csv.DictReader(csvfile)
		storeid = 1
		for row in reader:
			#string slicing to find the location
			loc_raw = row["Location"]
			ind1 = string.find(loc_raw, '(')
			ind2 = string.find(loc_raw, ')')
			ind3 = string.find(loc_raw[ind1:ind2],', ')
			lat = float(loc_raw[ind1+1:ind1+ind3])
			lon = float(loc_raw[ind1+ind3+2:ind2])
			c.execute('INSERT INTO stores VALUES (?,?,?,?)', (storeid,lat,lon,row["Square Footage"],) )
			#eventually will match postal codes with property value in db
			#eventually will filter store types
			storeid =storeid+1
	conn.commit()
	return


def geolocate(addr):
	"""code for querying nominatim"""
	#query = "http://localhost/nominatim/search?q=%s&format=json&polygon=1&addressdetails=1" %addr
	req = "http://nominatim.openstreetmap.org/search?q=%s&format=json&polygon=1&addressdetails=1" %addr
	resp = requests.get(req)
	outp = json.loads(resp.text)
	return outp[0]['lat'], outp[0]['lon']

if __name__ == "__main__":
	import_proc("db/test.db","input/ptest.csv")
	import_store("db/test.db","input/stest.csv")
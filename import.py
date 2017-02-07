import requests
import numpy as np
import csv
import sqlite3

#hard code name of files
#open file
#geolcate address
#add relevant information to database


def import_file(db, file, addr, field):
	"""use this to import data into the db"""
	conn = sqlite3.connect("db")
	with open(file) as csvfile:
		reader = csv.DictReader(csvfile)
		procid = 1
		for row in reader:
			procid
			#concat address
			#query the server for gps
			#add gps, field to db
			row[field]
	return


def geolocate(addr):
	#some how query the server
	#return a long and a lat coordinate
	return

if __name__ == "__main__":
	import_file("db/test.db","input/test.csv",["Street  Address","City","State","Zip"],"Commodity Listing")
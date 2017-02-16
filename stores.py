import requests
import numpy as np
import csv
import sqlite3
import json
import string
from osgeo import gdal, gdalconst, gdalnumeric, ogr, osr
import sys
import os

def geolocate(addr):
	"""code for querying nominatim"""
	#query = 'http://localhost/nominatim/search?q=%s&format=json&polygon=1&addressdetails=1' %addr
	req = 'http://nominatim.openstreetmap.org/search?q=%s&format=json&polygon=1&addressdetails=1' %addr
	resp = requests.get(req)
	outp = json.loads(resp.text)
	return outp[0]['lat'], outp[0]['lon']


def census_tract(lat,lon):
	"""given census tract file, figure out which tract a given point falls in"""

	#load census tract shapefile
	driver = ogr.GetDriverByName('ESRI Shapefile')
	tractfile = driver.Open('input/tl_2010_36_tract10/tl_2010_36_tract10.shp')
	tractlayer = tractfile.GetLayer()
	point = ogr.Geometry(ogr.wkbPoint)
	point.AddPoint(lon,lat)
	tractlayer.SetSpatialFilter(ogr.CreateGeometryFromWkt(point.ExportToWkt()))

	for feature in tractlayer:
		#http://gis.stackexchange.com/questions/27493/is-nad-83-the-same-as-epsg4326
		#seems as though I don't need to reproject...
  	 	return int(feature.GetField('GEOID10'))
	
	return 0 #if there isn't a census tract just return 0


def import_proc(db, file):
	"""use this to import processors into the data into the db"""
	conn = sqlite3.connect(db)
	c = conn.cursor()
	with open(file) as csvfile:
		reader = csv.DictReader(csvfile)
		procid = 1
		for row in reader:
			addr = '%s,%s,%s' %(row['Street  Address'], row['City'], row['State'])
			lat,lon = geolocate(addr)
			c.execute('INSERT INTO procs VALUES (?,?,?,?)', (procid,lat,lon,row['Commodity Listing'],) )
			procid =procid+1
	conn.commit()
	return


def import_tractvalues(db,file):
	"""import census data about median household incomes"""
	conn = sqlite3.connect(db)
	c = conn.cursor()
	with open(file) as csvfile: #hardcoded name of tract file
		reader = csv.DictReader(csvfile)
		next(reader)
		for row in reader:
			value = int(row['HD02_VD01']) if (str.find(row['HD02_VD01'],'*')==-1) else 0
			geoid = row['GEO.id2']
			c.execute('INSERT INTO tractvalues VALUES (?,?)', (geoid,value) )
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
			loc_raw = row['Location']
			ind1 = string.find(loc_raw, '(')
			ind2 = string.find(loc_raw, ')')
			ind3 = string.find(loc_raw[ind1:ind2],', ')
			lat = float(loc_raw[ind1+1:ind1+ind3])
			lon = float(loc_raw[ind1+ind3+2:ind2])
			tract = census_tract(lat,lon) #determine census tract to match with property values
			c.execute('INSERT INTO stores VALUES (?,?,?,?,?)', (storeid,lat,lon,row['Square Footage'],tract,) )
			#eventually will filter store types
			storeid =storeid+1
	conn.commit()
	return


if __name__ == '__main__':
	import_tractvalues('db/test.db','input/ACS_10_SF4_B25077/ACS_10_SF4_B25077_with_ann.csv')
	#import_proc('db/test.db','input/ptest.csv')
	#import_store('db/test.db','input/stest.csv')
	#census_tract(40.658597, -73.981943) #test if this works
	
import requests
import numpy as np
import csv
import sqlite3
import json
import string
from osgeo import gdal, gdalconst, gdalnumeric, ogr, osr
import sys
import os

def geolocate(street, city):
	"""code for querying nominatim"""
	addr = '%s,%s'%(street,city)
	#query = 'http://localhost/nominatim/search?q=%s&format=json&polygon=1&addressdetails=1' %addr
	req = 'http://nominatim.openstreetmap.org/search?q=%s&format=json&polygon=1&addressdetails=1' %addr
	resp = requests.get(req)
	try:
		outp = json.loads(resp.text)
		lat, lon = outp[0]['lat'], outp[0]['lon']
	except:
		req = 'http://nominatim.openstreetmap.org/search?q=%s&format=json&polygon=1&addressdetails=1' %city
		resp = requests.get(req)
		outp = json.loads(resp.text)
		lat, lon = outp[0]['lat'], outp[0]['lon']
	return lat,lon
		


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


def import_proc(db, file, band):
	"""use this to import processors into the data into the db"""
	conn = sqlite3.connect(db)
	c = conn.cursor()
	c.execute('SELECT * FROM bands WHERE band = ?;', (band,))
	croptype = c.fetchone()[1]
	with open(file) as csvfile:
		procid = 1 #keep track of procid's using row # (so that I don't repeat any)
		reader = csv.DictReader(csvfile)
		for row in reader:
			#if this proc matches the correct band
			c.execute('SELECT procid FROM procs WHERE procid = ?;', (procid,))
			exists_procid = c.fetchone()
			commodity = row['Commodity Listing']
			commodity_constraint = (commodity.find(croptype)>-1 or commodity.find('Fruit') > -1 or commodity.find('Vegetable') > -1)
			if( commodity_constraint and exists_procid==None and row['State']=='NY' ):
				street = row['Street  Address']
				city = '%s,%s' %(row['City'], row['State'])
				lat,lon = geolocate(street, city)
				c.execute('INSERT INTO procs VALUES (?,?,?,?)', (procid,lat,lon,row['Commodity Listing'],) )
			procid = procid + 1 #keep track of procid's using row #
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
		for row in reader:
			loc_raw = row['Location']	#string slicing to find the location
			ind1 = string.find(loc_raw, '(4') #exploit the fact that NY is on 40th parallel
			if(str.find(row['Establishment Type'],'JAC')>-1 and ind1>-1 ):
				ind2 = string.find(loc_raw[ind1:], ')') +ind1
				ind3 = string.find(loc_raw[ind1:ind2],', ')
				lat = float(loc_raw[ind1+1:ind1+ind3])
				lon = float(loc_raw[ind1+ind3+2:ind2])
				tract = census_tract(lat,lon) #determine census tract to match with property values
				#may get more sophisticated with what counts later
				c.execute('INSERT INTO stores VALUES (NULL,?,?,?,?)', (lat,lon,row['Square Footage'],tract,) )
	conn.commit()
	return


if __name__ == '__main__':
	import_tractvalues('db/test.db','input/ACS_10_SF4_B25077/ACS_10_SF4_B25077_with_ann.csv')
	#import_proc('db/test.db','input/ptest.csv')
	#import_store('db/test.db','input/stest.csv')
	#census_tract(40.658597, -73.981943) #test if this works
	
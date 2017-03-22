from solutions import *
import sqlite3
import string
import os
from qgis.core import *
import numpy as np
from osgeo import gdal, gdalconst, gdalnumeric, ogr, osr



class Ag_Figure:
	"""this class is designed to make all the figures easy to make
	features in figures have 2 fields: name, price, and type
	figures also can have edges"""


	def __init__(self, fname):
		"""initialize the figure, file is the name of the output file"""
		driver = ogr.GetDriverByName('ESRI Shapefile')
		

		sr = osr.SpatialReference()
		res = sr.ImportFromEPSG(4326)

		self.file = driver.CreateDataSource(fname)
		self.layer = self.file.CreateLayer('layer_1', srs = sr)

		name = ogr.FieldDefn("name", ogr.OFTString)
		price = ogr.FieldDefn("price", ogr.OFTReal)
		ftype = ogr.FieldDefn("ftype", ogr.OFTInteger) #1 - farms, 2 - procs, 3 - stores

		self.layer.CreateField(price)
		self.layer.CreateField(name)
		self.layer.CreateField(ftype)

	
	def create_feature(self, geom, name, price, ftype):
		"""use this to add a feature to the layer in the figure
		also returns the result so it you can make edges between 
		features"""
		outFeature = ogr.Feature(self.layer.GetLayerDefn())
		outFeature.SetGeometry(geom)
		outFeature.SetField('price', price)
		outFeature.SetField('name', name)
		outFeature.SetField('ftype', ftype)
		self.layer.CreateFeature(outFeature)
		return outFeature
	

	def create_edge(start,end):
		"""use this to create edges in between 2 features"""
		pass


	def close(self):
		"""close the figure"""
		self.layer = None
		self.file = None


def make_folder(band):
	"""makes a folder in the figures directory with the
	specified name
	returns the name of the folder"""
	folder = 'maps/map_%d'%band
	if not os.path.exists(folder):
		os.makedirs(folder)
	return folder


def get_coord(db, name, table):
	"""return the location of this id as a point geometry"""
	query1 = None #set the query based on which table
	if (table == 'stores'):
		query1 = 'SELECT * FROM constores WHERE geoid = ?'
	elif (table == 'farms'):
		query1 = 'SELECT * FROM farms where farmid = ?'
	elif (table == 'procs'):
		query1 = 'SELECT * FROM procs where procid = ?'
	else :
		return None

	conn = sqlite3.connect(db)
	c = conn.cursor()
	c.execute(query1,(name,))
	
	query_result = c.fetchone()
	lat, lon = query_result[1],query_result[2]

	point = ogr.Geometry(ogr.wkbPoint)
	point.AddPoint(lon,lat)

	return ogr.CreateGeometryFromWkt(point.ExportToWkt())


def get_tract(geoid):
	"""given geoid, return the geometry of it's corresponding census tract"""
	driver = ogr.GetDriverByName('ESRI Shapefile')
	tractfile = driver.Open('input/tl_2010_36_tract10/tl_2010_36_tract10.shp') #load census tract shapefile
	tractlayer = tractfile.GetLayer()
	tractlayer.SetAttributeFilter("GEOID10 = '%d'"%geoid)
	feature = tractlayer.GetNextFeature()
	return feature


def map_1(band):	
	"""create a shapefile with all the census districts and prices"""
	folder = make_folder(band)
	sol = 'solutions/solution_%d/band_%d.sol'%(band,band)
	filename = folder + '/map_1_%d.shp'%band
	solp = Solution_Parser(sol)
	agfig = Ag_Figure(filename)
	geoid,price = solp.next_store()
	while(geoid != None):
		#needs to be this way because scope in python isn't right
		feature = get_tract(geoid)
		geom = feature.GetGeometryRef() 
		agfig.create_feature(geom, geoid, price, 3)
		geoid,price = solp.next_store()
	agfig.close()


def map_2(db, band):
	"""draw the network with prices (with or without edges)"""
	folder = make_folder(band)
	sol = 'solutions/solution_%d/band_%d.sol'%(band,band)

	filename = folder + '/map_2_%d.shp'%band
	solp = Solution_Parser(sol)
	agfig = Ag_Figure(filename)

	#draw stores
	geoid,price = solp.next_store()
	while(geoid != None):
		geom = get_coord(db,geoid,'stores')
		agfig.create_feature(geom, geoid, price, 3)
		geoid,price = solp.next_store()

	#draw procs
	procid,price = solp.next_proc()
	while(procid != None):
		geom = get_coord(db,procid,'procs')
		agfig.create_feature(geom, geoid, price, 2)
		procid,price = solp.next_proc()

	#draw farms
	farmid,price = solp.next_farm()
	while(farmid != None):
		geom = get_coord(db,farmid,'farms')
		agfig.create_feature(geom, farmid, price, 1)
		farmid,price = solp.next_farm()

	agfig.close()


def map_3(db):
	"""plot all the stores in NYS"""
	filename = 'misc/map_3.shp'
	agfig = Ag_Figure(filename)
	conn = sqlite3.connect(db)
	c = conn.cursor()
	query = 'SELECT * FROM stores'
	for row in c.execute(query):
		lat, lon = row[1],row[2]
		point = ogr.Geometry(ogr.wkbPoint)
		point.AddPoint(lon,lat)
		geom = ogr.CreateGeometryFromWkt(point.ExportToWkt())		
		agfig.create_feature(geom, row[0], 0, 3)


def compare_1(db, band1,band2):
	"""difference prices for 2 different band"""
	filename = 'maps/misc/compare_1_%d_%d.shp'%(band1,band2)
	agfig = Ag_Figure(filename)
	solfile1 = 'solutions/solution_%d/band_%d.sol'%(band1,band1)
	solfile2 = 'solutions/solution_%d/band_%d.sol'%(band2,band2)
	solp1 = Solution_Parser(solfile1)
	solp2 = Solution_Parser(solfile2)

	name1,price1 = solp1.next_store()

	#add the stores to the shape file
	while name1 != None:
		name2,price2 = solp2.next_store()
		while name2 != None:
			if(name1 == name2):
				geom = get_coord(db,name1,'stores')
				agfig.create_feature(geom, name1, price1-price2, 3)
				break
		name1,price1 = solp1.next_store()


def compare_2(db, band1,band2):
	"""do the same thing as compare 1 only do it with procs"""
	filename = 'maps/misc/compare_2_%d_%d.shp'%(band1,band2)
	agfig = Ag_Figure(filename)
	solfile1 = 'solutions/solution_%d/band_%d.sol'%(band1,band1)
	solfile2 = 'solutions/solution_%d/band_%d.sol'%(band2,band2)
	solp1 = Solution_Parser(solfile1)
	solp2 = Solution_Parser(solfile2)

	#add the procs to the shape file
	name1,price1 = solp1.next_proc()
	while name1 != None:
		name2,price2 = solp2.next_proc()
		while name2 != None:
			if(name1 == name2):
				geom = get_coord(db,name1,'procs')
				agfig.create_feature(geom, name1, price1-price2, 2)
				break
		name1,price1 = solp1.next_proc()


def run(db, list):
	for i in list:
		map_1(i)
		map_2(db, i)


if __name__ == "__main__":
	#run('db/ag_networks2.db', [243,49,66,69])
	#run('db/test2.db',[1,68])
	compare_1('db/test2.db',1,68)
	compare_2('db/test2.db',1,68)
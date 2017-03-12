import sqlite3
import string
import os
from qgis.core import *
import numpy as np
from osgeo import gdal, gdalconst, gdalnumeric, ogr, osr


class Solution_Parser:
	"""converts a solution into a feature"""
	
	def __init__(self, fname):
		self.fname = fname

		open_file = open(self.fname)
		file = open_file.readlines()
		self.flen =len(file)


		#initial values (i.e. first one in solution file)	
		self.farm1 =0
		for line in file:
			if(string.find(line,'farm_')>-1):
				break
			self.farm1 = self.farm1+1

		self.store1 = 0
		for line in file:
			if(string.find(line,'store_')>-1):
				break
			self.store1 = self.store1+1

		self.proc1 = 0
		for line in file:
			if(string.find(line,'proc_')>-1):
				break
			self.proc1 = self.proc1+1
		
		#initial indexes
		self.sindex = self.store1
		self.findex = self.farm1
		self.pindex = self.proc1


	def parse_line(self, line_index, ltype):
		"""use this to parse a line in the solution file"""
		open_file = open(self.fname)
		file = open_file.readlines()
		
		if(line_index < self.flen):
			line = file[line_index]
			index = string.find(line, ltype)
			if index > -1:
				index2 = string.find(line, ' ')
				name = int(line[index+len(ltype):index2])
				price = float(line[1+index2:-1])
				return name,price
		return None, None

	
	def next_store(self):
		"""return the next store in the solution file with geoid, price"""
		result = self.parse_line(self.sindex,'store_')
		self.sindex = self.sindex + 1
		return result


	def next_farm(self):
		"""return the next farm in solution file with farmid, price"""
		result = self.parse_line(self.findex,'farm_')
		self.findex = self.findex + 1
		return result


	def next_proc(self):
		"""return the next proc in the solution file with procid, price"""
		result = self.parse_line(self.pindex,'proc_')
		self.pindex = self.pindex + 1
		return result


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


def make_folder(outfolder):
	"""makes a folder in the figures directory with the
	specified name
	returns the name of the folder"""
	folder = 'figures/'+ outfolder
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


def test1(sol, outfolder):	
	"""create a shapefile with all the census districts and prices"""
	folder = make_folder(outfolder)

	filename = folder + '/test1.shp'
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


def test2(db, sol, outfolder):
	"""draw the network with prices (with or without edges)"""
	folder = make_folder(outfolder)

	filename = folder + '/test2.shp'
	solp = Solution_Parser(sol)
	agfig = Ag_Figure(filename)

	#print("stores")
	geoid,price = solp.next_store()
	while(geoid != None):
		geom = get_coord(db,geoid,'stores')
		agfig.create_feature(geom, geoid, price, 3)
		geoid,price = solp.next_store()

	#print("procs")
	procid,price = solp.next_proc()
	while(procid != None):
		geom = get_coord(db,procid,'procs')
		agfig.create_feature(geom, geoid, price, 2)
		procid,price = solp.next_proc()

	#print("farms")
	farmid,price = solp.next_farm()
	while(farmid != None):
		geom = get_coord(db,farmid,'farms')
		agfig.create_feature(geom, farmid, price, 1)
		farmid,price = solp.next_farm()

	agfig.close()


def test3(db, outfolder):
	"""plot all the stores in NYS"""
	folder = make_folder(outfolder)
	filename = folder + '/test3.shp'
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

	



if __name__ == "__main__":
	#out1 = test1('output/result_49/band_49.sol','band_49' )
	#out1 = test1('output/result_1/band_1.sol','band_1' )
	#out2 = test2('db/test2.db', 'output/result_1/band_1.sol', 'band_1')
	#out3 = test2('db/ag_networks.db', 'output/result_49/band_49.sol', 'band_49')
	out5 = test3('db/ag_networks.db', 'stores')
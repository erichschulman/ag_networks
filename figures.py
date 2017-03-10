import sqlite3
import string
import os
from qgis.core import *
import numpy as np
from osgeo import gdal, gdalconst, gdalnumeric, ogr, osr


#overlay farms, congressional district centroids, and processors 
#draw lines between each one

#show farms with colors
#show procs with colors
#show cong district centroids with colors
#show cong district with colors


def census_tract(geoid):
	"""given geoid, return it's corresponding census tract as a feature"""

	#load census tract shapefile
	driver = ogr.GetDriverByName('ESRI Shapefile')
	tractfile = driver.Open('input/tl_2010_36_tract10/tl_2010_36_tract10.shp')
	tractlayer = tractfile.GetLayer()
	tractlayer.SetAttributeFilter("GEOID10 = '%d'"%geoid)

	for feature in tractlayer:
		return feature
	
	return None #if there isn't a census tract just return 0


def color_ramp(file, name):
	"""format the qgis file with the appropriate color ramp"""
	QgsApplication.setPrefixPath("/usr/bin/", True)
	qgs = QgsApplication([], False)
	qgs.initQgis()
	print(os.path.abspath(file))

	layer = QgsVectorLayer(os.path.abspath(file), name, "ogr")

	for cat in layer.rendererV2().categories():
		print "%s: %s :: %s" % (cat.value().toString(), cat.label(), str(cat.symbol()))
	qgs.exitQgis()


def test1(db, inf, outf, band):	
	"""create a shapefile with all the census districts and prices"""

	#create a folder with the name
	folder = "%s/band_%d"%(outf, band)
	if not os.path.exists(folder):
		os.makedirs(folder)


	driver = ogr.GetDriverByName('ESRI Shapefile')

	file = driver.CreateDataSource('%s/band_%d.shp'%(folder,band))
	layer = file.CreateLayer('%s/band_%d'%(folder,band))

	#cycle through the results and get the geoid as a key
	conn = sqlite3.connect(db)
	c = conn.cursor()

	f = open('%s/result_%d/band_%d.sol'%(inf,band,band) )

	geoidfield = ogr.FieldDefn("GEOID", ogr.OFTString)
	pricefield = ogr.FieldDefn("price", ogr.OFTReal)
	
	layer.CreateField(pricefield)
	layer.CreateField(geoidfield)


	for line in f:
		index = string.find(line, 'store_')
		if index > -1:
			index2 = string.find(line, ' ')
			geoid = int(line[index+6:index2])
			price = float(line[1+index2:-1])
			#print('geoid: |%s| price: |%s|'%(geoid,price))
			
			feature = census_tract(geoid)
			geom = feature.GetGeometryRef()

			outFeature = ogr.Feature(layer.GetLayerDefn())
			outFeature.SetGeometry(geom)
			outFeature.SetField('price', price)
			outFeature.SetField('GEOID', geoid)

			layer.CreateFeature(outFeature)


	#close the resultant files
	file = None
	layer = None
	#return file name



if __name__ == "__main__":
	#out1 = test1('ag_networks.db', 'output','figures',49)
	out1 = test1('test2.db', 'output','figures',1)
	#color_ramp('figures/band_1/band_1.shp','band_1')
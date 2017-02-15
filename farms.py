import sqlite3
from osgeo import gdal, ogr
import sys


def test():
	conn1 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED')
	conn2 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED')
	c1 = conn1.cursor()
	c2 = conn2.cursor()
	i = 1
	for row in c2.execute('SELECT * FROM proc'):
		print(row)
		i = i+1
		c1.execute('INSERT INTO stores VALUES (?,?,?,?)', (20+i,20,20,20,) )
	conn1.commit()

def test2():
	conn1 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED')
	c1 = conn1.cursor()
	for row in c1.execute('SELECT * FROM ?', 'stores'):
		print(row)


def import_farms(file, band):
	gdal.UseExceptions()

	ds = gdal.Open('test.tif')
	srcband = src_ds.GetRasterBand(band)

	#close dataset
	ds = None

if __name__ == "__main__":
	import_farms('input/NASSnyc2010.036.tif.8033/cdl_tm_r_ny_2010_utm18.tif',68):
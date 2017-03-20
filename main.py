import sqlite3
import os
from farms import *
from edges import *
from stores import *
from transport import *


#to start osrm: osrm-routed ../maps/new-york-latest.osrm

def create_db(db):
	"""run the sql file to create the db"""
	f = open('db_create.sql','r')
	sql = f.read()
	if (os.path.isfile(db) ):
		os.remove(db)
	con = sqlite3.connect(db) #create the db
	cur = con.cursor()
	cur.executescript(sql)
	con.commit()


#243 ,49, 

def main(db, farms, procs, stores, bands):
	create_db(db)
	
	#import data
	print('Loading Bands into the DB...')
	import_bands(db)
	print('Loading Census Data into the DB...')
	import_tractvalues(db, 'input/ACS_10_SF4_B25077/ACS_10_SF4_B25077_with_ann.csv')	
	print('Loading Stores into the DB...')
	import_store(db,stores)
	
	for b in bands:
		print('Loading Band %d Processors into the DB...'%b )
		import_proc(db,procs,b)
		print('Loading Band %d Farms into the DB...'%b )
		import_farms(db, farms, b ,10)

	#calculate edges
	print('Building Store Edges...')
	proc_edges(db)
	print('Building Farm Edges...')
	proc_edges(db, farms = True )
	print('DB Complete!')
	for b in bands:
		print('Running LP for Band %d...'%b)
		tranport(db, b)
	return


if __name__ == "__main__":
	#onions - 49
	#cherries - 66
	#cabbage - 243
	#grapes - 69

	#main('db/band_243.db','input/NASSnyc2010.036.tif.8033/cdl_tm_r_ny_2010_utm18.tif','input/Farm_Product_Dealer_Licenses_Currently_Issued.csv','input/Retail_Food_Stores.csv', [243,49,66,69])
	main('db/test2.db', 'input/test.tif', 'input/ptest.csv', 'input/stest.csv' , [1,68])
import sqlite3
from farms import *
from edges import *
from stores import *


#to start osrm osrm-routed ../maps/new-york-latest.osrm

def create_db(db):
	"""run the sql file to create the db"""
	f = open('db_create.sql','r')
	sql = f.read()
	con = sqlite3.connect(db) #create the db
	cur = con.cursor()
	cur.executescript(sql)
	con.commit()


def main(db,farms,procs,stores):
	create_db(db)
	
	#import data
	print('Loading Bands into the DB...')
	import_bands(db)
	print('Loading Census Data into the DB...')
	import_tractvalues(db, 'input/ACS_10_SF4_B25077/ACS_10_SF4_B25077_with_ann.csv')
	print('Loading Farms into the DB...')
	import_farms(db, farms,1,10)
	import_farms(db, farms,36,10)
	print('Loading Processors into the DB...')
	import_proc(db,procs)
	print('Loading Stores into the DB...')
	import_store(db,stores)

	#calculate edges
	print('Building Store Edges...')
	proc_edges(db)
	print('Building Farm Edges...')
	proc_edges(db, farms = True )
	print('DB Complete!')
	return


if __name__ == "__main__":
	main('db/test2.db','input/test.tif','input/ptest.csv','input/stest.csv')
import sqlite3
from farms import *
from edges import *
from stores import *


#to start osrm osrm-routed ../maps/new-york-latest.osrm from the directory
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
	import_bands(db)
	import_tracts(db)
	import_farms(db, farms,36,10)
	import_proc(db,procs)
	import_store(db,stores)

	#calculate edges
	proc_edges(db)
	proc_edges(db, farms = True )
	fp_edges(db)


if __name__ == "__main__":
	main('db/test.db','input/test.tif','input/ptest.csv','input/stest.csv')
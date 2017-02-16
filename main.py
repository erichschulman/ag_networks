import sqlite3
from farms import *
from edges import *
from stores import *


#to start osrm osrm-routed ../maps/new-york-latest.osrm from the directory

def main(db):

	f = open('ag_networks.sql','r')
	sql = f.read()
	con = sqlite3.connect(db) #create the db
	cur = con.cursor()
	cur.executescript(sql)
	
	import_proc(db,'input/ptest.csv')
	import_store(db,'input/stest.csv')
	import_farms(db, 'input/test.tif',36,10)
	proc_edges(db)
	proc_edges(db, farms = True )
	fp_edges(db)

	con.commit()
	return

if __name__ == "__main__":
	main("db/test.db")
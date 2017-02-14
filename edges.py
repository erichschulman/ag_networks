import requests
import sqlite3
import json


#to start osrm osrm-routed ../maps/new-york-latest.osrm from the directory

def fp_edges(db):
	"""figures out which is the most efficient edge between farms and stores"""
	conn1 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED') #probably not secure, but ya know
	conn2 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED')
	
	return


def proc_edges(db, farms=False):
	"""use this to create edges between procs, farms and stores
	set the flag to switch between farms and stores. stores by default"""

	table = 'ps_edges'
	query = 'SELECT procs.procid, procs.lat, procs.lon, stores.storeid, stores.lat, stores.lon FROM procs, stores'
	if (farms):
		table = 'fp_edges'
		query = 'SELECT procs.procid, procs.lat, procs.lon, farm.farmid, farm.lat, farm.lon FROM procs, farms'

	"""computes edge weights between stores and processors"""
	conn1 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED') #probably not secure, but ya know
	conn2 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED')
	c1 = conn1.cursor()
	c2 = conn2.cursor()
	if (type)

	for row in c1.execute(query):
			duration = routing(row[2],row[1],row[5],row[4])
			c2.execute('INSERT INTO ? VALUES (?,?,?,?)', (table, row[3],row[0],0,duration,))
	
	conn2.commit()
	return


def routing(lon0,lat0,lon1,lat1):
	"""wrapper for doing routing with OSRM"""
	req = "http://0.0.0.0:5000/route/v1/table/%s,%s;%s,%s"%(lon0,lat0,lon1,lat1)
	osrm_raw = requests.get(req)
	orsm =json.loads(osrm_raw.text)
	return orsm['routes'][0]['duration']


if __name__ == "__main__":
	#proc_edges("db/test.db")
	proc_edges("db/test.db", farms = True )
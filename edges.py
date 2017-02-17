import requests
import sqlite3
import json

#to start osrm osrm-routed ../maps/new-york-latest.osrm


def routing(lon0,lat0,lon1,lat1):
	"""wrapper for doing routing with OSRM"""
	req = "http://0.0.0.0:5000/route/v1/table/%s,%s;%s,%s"%(lon0,lat0,lon1,lat1)
	osrm_raw = requests.get(req)
	orsm =json.loads(osrm_raw.text)
	return orsm['routes'][0]['duration']


def proc_edges(db, farms=False):
	"""use this to create edges between procs, farms and stores
	set the flag to switch between farms and stores. stores by default"""

	table = 'ps_edges'
	query1 = 'SELECT procs.procid, procs.lat, procs.lon, stores.storeid, stores.lat, stores.lon FROM procs, stores'
	query2 = 'INSERT INTO ps_edges VALUES (?,?,?)'
	
	if (farms):
		table = 'fp_edges'
		query1 = 'SELECT procs.procid, procs.lat, procs.lon, farms.farmid, farms.lat, farms.lon FROM procs, farms'
		query2 = 'INSERT INTO fp_edges VALUES (?,?,?)'

	conn1 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED') #probably not secure, but ya know
	conn2 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED')
	c1 = conn1.cursor()
	c2 = conn2.cursor()

	for row in c1.execute(query1):
			duration = routing(row[2],row[1],row[5],row[4])
			c2.execute(query2, (row[3],row[0],duration,))
	
	conn2.commit()
	return


def fp_edges(db):
	"""print the edges as a test"""
	edges = FP_Edges(db)

	current_edge = edges.next_edge()
	while(current_edge!=None):
		print(current_edge)
		current_edge = edges.next_edge()
	return


if __name__ == "__main__":
	#proc_edges("db/test.db")
	#proc_edges("db/test.db", farms = True )
	fp_edges("db/test.db")
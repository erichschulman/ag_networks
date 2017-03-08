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


def proc_edges(db, farms=False, constores = True):
	"""use this to create edges between procs, farms and stores
	set the flag to switch between farms and stores. stores by default"""

	table = 'ps_edges'
	query1 = 'SELECT * FROM ps_list LEFT OUTER JOIN ps_edges ON ps_list.geoid = ps_edges.storeid AND ps_edges.procid = ps_list.procid;'
	#breaking compatibility with individual stores
	query2 = 'INSERT INTO ps_edges VALUES (?,?,?);'
	index = 8
	
	if (farms):
		table = 'fp_edges'
		query1 = 'SELECT * FROM farm_proc_bands LEFT OUTER JOIN fp_edges ON farm_proc_bands.farmid = fp_edges.farmid AND farm_proc_bands.procid = fp_edges.procid;'
		query2 = 'INSERT INTO fp_edges VALUES (?,?,?);'
		query3 = 'SELECT * FROM fp_edges WHERE procid = ? AND farmid = ?'
		index = 9

	conn1 = sqlite3.connect(db, isolation_level = 'DEFERRED') #probably not secure, but ya know
	conn2 = sqlite3.connect(db, isolation_level = 'DEFERRED')
	c1 = conn1.cursor()
	c2 = conn2.cursor()

	for row in c1.execute(query1):
		if( not farms):
			print(row[index])
		if(row[index] == None): #ensure this edge doesn't already exist
			duration = routing(row[2],row[1],row[5],row[4])
			c2.execute(query2, (row[3],row[0],duration,))
			conn2.commit()
	return





if __name__ == "__main__":
	#proc_edges("db/test.db")
	#proc_edges("db/test.db", farms = True )
	fp_edges("db/test.db")
import requests
import sqlite3
import json


#to start osrm osrm-routed ../maps/new-york-latest.osrm from the directory

def proc_edges(db, farms=False):
	"""use this to create edges between procs, farms and stores
	set the flag to switch between farms and stores. stores by default"""

	table = 'ps_edges'
	query1 = 'SELECT procs.procid, procs.lat, procs.lon, stores.storeid, stores.lat, stores.lon FROM procs, stores'
	query2 = 'INSERT INTO ps_edges VALUES (?,?,?,?)'
	
	if (farms):
		table = 'fp_edges'
		query1 = 'SELECT procs.procid, procs.lat, procs.lon, farms.farmid, farms.lat, farms.lon FROM procs, farms'
		query2 = 'INSERT INTO fp_edges VALUES (?,?,?,?)'

	conn1 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED') #probably not secure, but ya know
	conn2 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED')
	c1 = conn1.cursor()
	c2 = conn2.cursor()

	for row in c1.execute(query1):
			duration = routing(row[2],row[1],row[5],row[4])
			c2.execute(query2, (row[3],row[0],0,duration,))
	
	conn2.commit()
	return


def routing(lon0,lat0,lon1,lat1):
	"""wrapper for doing routing with OSRM"""
	req = "http://0.0.0.0:5000/route/v1/table/%s,%s;%s,%s"%(lon0,lat0,lon1,lat1)
	osrm_raw = requests.get(req)
	orsm =json.loads(osrm_raw.text)
	return orsm['routes'][0]['duration']


class FP_Edges:
	"""figures out which is the most efficient edge between farms and stores,
	behavior is unspecified if multiple instances are active at the same time"""

	def __init__(self, db):
		"""initialize the FP_Edges class so I can get entries from it"""
		self.conn1 = sqlite3.connect(db, isolation_level = 'DEFERRED') #may regret this later
		self.c1 = self.conn1.cursor()
		self.database = db

		query = ("SELECT fp_edges.farmid as farmid, ps_edges.storeid as storeid, "
				"MIN(fp_edges.routdist + ps_edges.routdist) as dist "
				"FROM ps_edges, fp_edges "
				"WHERE ps_edges.procid = fp_edges.procid "
				"GROUP BY fp_edges.farmid, ps_edges.storeid;")

		self.c1.execute(query)

	def next_edge(self):
		"""return the next row in the table"""
		return self.c1.fetchone()


	def restart_conn(self):
		"""restart the table from the begining"""
		self.c1.close()

		self.conn1 = sqlite3.connect(self.database, isolation_level = 'DEFERRED') #may regret this later
		self.c1 = self.conn1.cursor()

		query = ("SELECT fp_edges.farmid as farmid, ps_edges.storeid as storeid, "
				"MIN(fp_edges.routdist + ps_edges.routdist) as dist "
				"FROM ps_edges, fp_edges "
				"WHERE ps_edges.procid = fp_edges.procid "
				"GROUP BY fp_edges.farmid, ps_edges.storeid;")

		self.c1.execute(query)



def fp_edges(db):
	"""print the edges as a test"""
	edges = FP_Edges(db)

	current_edge = edges.next_edge()
	while(current_edge!=None):
		print(current_edge)
		current_edge = edges.next_edge()

	edges.restart_conn()

	print("restarted connection")
	current_edge = edges.next_edge()
	while(current_edge!=None):
		print(current_edge)
		current_edge = edges.next_edge()

	return


if __name__ == "__main__":
	#proc_edges("db/test.db")
	#proc_edges("db/test.db", farms = True )
	fp_edges("db/test.db")
from gurobipy import *
import sqlite3


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
		return


def example(output):
	"""example of transportation problem using 
	gurobi optimizer, may have bugs"""

	nodes = ['farm1', 'farm2', 'store1', 'store2', 'store3']
	edges, costs = multidict({
		('farm1', 'store1'): 100,
		('farm1', 'store2'):  80,
		('farm1', 'store3'):  120,
		('farm2',  'store1'):   120,
		('farm2',  'store2'): 120,
		('farm2',  'store3'):  120 })

	flows = {'store1':20,
		'store2':20,
		'store3':20,
		'farm1':-30,
		'farm2':-30}

	# Create optimization model
	m = Model('transportation')
	# Create prices
	prices = m.addVars(nodes, lb=0.0, obj=flows, name="prices")
	# add arbitrage constraint constraints
	m.addConstrs( (prices[v]-prices[w]  <= costs[v,w] for v,w in edges),
 		"arbitrage")

	m.write(output+'/test.lp')
	# Compute optimal solution
	m.optimize()
	# Print solutio
	if m.status == GRB.Status.OPTIMAL:
		#solution = m.getAttr('prices')
		#print(solution)
		m.write(output+'/test.sol')


def tranport(output, db):
	"""pull data from the databse to solve the transportation
	problem for NYS. This is it!"""

	m = Model('transportation')

	conn = sqlite3.connect('db/test.db')
	c = conn.cursor()
	query1 = ('SELECT farmid, (100*area/tot) as tota FROM ' +
				'farms, (SELECT CAST(SUM(area) as FLOAT) as tot FROM farms);')
	query2 = ('SELECT storeid, (100*value*sqftg/tot) as tota FROM'
			'(SELECT * FROM stores AS S, tractvalues AS T '+
			'WHERE T.geoid = S.geoid), '+
			'(SELECT CAST(sum(value*sqftg) AS FLOAT) as tot '+
			'FROM stores AS S, tractvalues AS T '+
			'WHERE T.geoid = S.geoid);')

	farms = {}
	#add farms
	for row in c.execute(query1):
		farms[row[0]] = m.addVar( obj=(-row[1]), name=('farm_%s'% row[0]) )

	stores = {}
	#add stores
	for row in c.execute(query2):
		stores[row[0]] = m.addVar( obj=row[1], name=('store_%s'% row[0]) )

	#add edge constraints
	edges = FP_Edges(db)
	current_edge = edges.next_edge()
	while(current_edge!=None):
		m.addConstr(farms[current_edge[0]] - stores[current_edge[1]] <= current_edge[2], "row_%s+%s"%(current_edge[0],current_edge[1])) #not sure about this?
		current_edge = edges.next_edge()

	m.write(output+'/ag_networks.lp')
	# Compute optimal solution
	m.optimize()
	# Print solutio
	if m.status == GRB.Status.OPTIMAL:
		#solution = m.getAttr('prices')
		#print(solution)
		m.write(output+'/ag_networks.sol')


if __name__ == "__main__":
	tranport('output','db/test.db')
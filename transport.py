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

	#add edge constraints
	edges = FP_Edges(db)
	current_edge = edges.next_edge()
	while(current_edge!=None):
		print(current_edge)
		current_edge = edges.next_edge()


	#add variables
	# Alternate version:
	# m.addConstrs(
	#   (quicksum(flow[h,i,j] for i,j in arcs.select('*',j)) + inflow[h,j] ==
	#     quicksum(flow[h,j,k] for j,k in arcs.select(j,'*'))
	#     for h in commodities for j in nodes), "node")

	#add cost constraints
	# for i,j in arcs:
	#   m.addConstr(sum(flow[h,i,j] for h in commodities) <= capacity[i,j],
	#               "cap[%s,%s]" % (i, j))

	

	m.write(output+'/test.lp')
	# Compute optimal solution
	m.optimize()
	# Print solutio
	if m.status == GRB.Status.OPTIMAL:
		#solution = m.getAttr('prices')
		#print(solution)
		m.write(output+'/test.sol')



if __name__ == "__main__":
	example('output')
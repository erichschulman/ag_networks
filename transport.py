from gurobipy import *
import sqlite3


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


def tranport(output, db, band):
	"""pull data from the databse to solve the transportation
	problem for NYS. This is it!"""

	m = Model('transportation')

	conn = sqlite3.connect('db/test.db')
	c = conn.cursor()
	query1 = 'SELECT * FROM farm_percents WHERE band=?'
	query2 = 'SELECT * FROM store_percents;'
	query3 = 'SELECT * FROM fs_edges;'

	farms = {}
	#add farms
	for row in c.execute(query1, (band,)):
		farms[row[0]] = m.addVar( obj=(-row[1]), name=('farm_%s'% row[0]) )

	stores = {}
	#add stores
	for row in c.execute(query2):
		stores[row[0]] = m.addVar( obj=row[1], name=('store_%s'% row[0]) )

	#add edge constraints

	for row in c.execute(query3):
		m.addConstr(farms[row[0]] - stores[row[1]] <= row[2], "row_%s_%s"%(row[0],row[1])) #not sure about this?

	m.write(output+'/test2.lp')
	# Compute optimal solution
	m.optimize()
	# Print solutio
	if m.status == GRB.Status.OPTIMAL:
		#solution = m.getAttr('prices')
		#print(solution)
		m.write(output+'/test2.sol')


if __name__ == "__main__":
	tranport('output','db/test.db', 36)
import datetime
from gurobipy import *
import sqlite3


def example(output):
	"""example of transportation problem using 
	gurobi optimizer, may have bugs"""

	nodes = ['farm1', 'farm2','farm3', 'store1', 'store2', 'store3' ,'proc1', 'proc2']
	edges, costs = multidict({
		('farm1', 'proc1'): 30,
		('farm2', 'proc1'):  30,
		('farm3', 'proc1'):  30,
		('farm1',  'proc2'):   30,
		('farm2',  'proc2'): 30,
		('farm3',  'proc2'):  30,
		('proc1', 'store1'): 30,
		('proc1', 'store2'): 30,
		('proc1', 'store3'): 30,
		('proc2', 'store1'): 30,
		('proc2', 'store2'): 30,
		('proc2', 'store3'): 30 })

	flows = {'store1':-30,
		'store2':-30,
		'store3':-30,
		'farm1':30,
		'farm2':30,
		'farm3':30,
		'proc1':0,
		'proc2':0}

	# Create optimization model
	m = Model('transportation')
	# Create prices
	prices = m.addVars(nodes, lb=0.0, obj=flows, name="prices")
	# add arbitrage constraint constraints
	m.addConstrs( (-prices[v]+prices[w]  <= costs[v,w] for v,w in edges),
 		"arbitrage")

	today = datetime.date.today() #set the date for orginizational
	m.write(output+today.strftime('/test_%m_%d.lp'))
	# Compute optimal solution
	m.optimize()
	# Print solutio
	if m.status == GRB.Status.OPTIMAL:
		#solution = m.getAttr('prices')
		#print(solution)
		m.write(output+today.strftime('/test_%m_%d.sol'))


def tranport(output, db, band, constores = True):
	"""pull data from the databse to solve the transportation
	problem for NYS."""

	m = Model('transportation')

	conn = sqlite3.connect(db)
	c = conn.cursor()
	query1 = 'SELECT * FROM farm_percents WHERE band=?'
	#figured I'd keep the option to use individual stores, not gonna really pursue it though
	query2 = 'SELECT * FROM constore_percents;' if constores else 'SELECT * FROM store_percents;'
	query3 = 'SELECT procid, 0 FROM conprocs GROUP BY procid' #create a list of processors (with flow constraints)
	
	#query the database for edges
	query4 = 'SELECT * FROM fp_edges;'
	query5 = 'SELECT * FROM ps_edges;'

	farms = {} #add farms
	for row in c.execute(query1, (band,)):
		farms[row[0]] = m.addVar( obj=row[1], name=('farm_%s'% row[0]) )

	stores = {} #add stores
	for row in c.execute(query2):
		stores[row[0]] = m.addVar( obj=(-row[1]), name=('store_%s'% row[0]) )

	procs = {} #add processors to the problem
	for row in c.execute(query3):
		procs[row[0]] = m.addVar( obj=row[1], name=('proc_%s'% row[0]) )

	#add constraints representing farm to processors
	for row in c.execute(query4):
		m.addConstr( -farms[row[0]] + procs[row[1]] <= row[2], "row_%s_%s"%(row[0],row[1])) #not sure about this?

	#add constraints representing processor to store
	for row in c.execute(query5):
		m.addConstr(-procs[row[1]] +  stores[row[0]] <= row[2], "row_%s_%s"%(row[0],row[1])) #not sure about this?

	m.write('%s/band_%d.lp'%(output,band))
	# Compute optimal solution
	m.optimize()
	# Print solution
	if m.status == GRB.Status.OPTIMAL:
		#solution = m.getAttr('prices')
		#print(solution)
		m.write('%s/band_%d.sol'%(output,band))


if __name__ == "__main__":
	tranport('output','db/test2.db', 1)
	#example('output')
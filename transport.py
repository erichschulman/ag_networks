import datetime
from gurobipy import *
import sqlite3


def example(output):
	"""example of transportation problem using 
	gurobi optimizer, may have bugs"""

	nodes = ['farm1', 'farm2','farm3', 'store1', 'store2', 'store3' ,'proc1', 'proc2']
	edges, costs = multidict({
		('farm1', 'proc1'): 100,
		('farm2', 'proc1'):  80,
		('farm3', 'proc1'):  120,
		('farm1',  'proc2'):   120,
		('farm2',  'proc2'): 120,
		('farm3',  'proc2'):  120,
		('proc1', 'store1'): 100,
		('proc1', 'store2'): 100,
		('proc1', 'store3'): 100,
		('proc2', 'store1'): 100,
		('proc2', 'store2'): 100,
		('proc2', 'store3'): 100 })

	flows = {'store1':40,
		'store2':20,
		'store3':30,
		'farm1':-50,
		'farm2':-30,
		'farm3':-10,
		'proc1':0,
		'proc2':0}

	# Create optimization model
	m = Model('transportation')
	# Create prices
	prices = m.addVars(nodes, lb=0.0, obj=flows, name="prices")
	# add arbitrage constraint constraints
	m.addConstrs( (prices[v]-prices[w]  <= costs[v,w] for v,w in edges),
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
	problem for NYS. This is it!"""

	m = Model('transportation')

	conn = sqlite3.connect('db/test.db')
	c = conn.cursor()
	query1 = 'SELECT * FROM farm_percents WHERE band=?'
	query2 = 'SELECT * FROM store_percents;'
	if(constores): #in this case we are using consolidated stores by census tract
		query2 = 'SELECT * FROM constore_percents;'
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
	# Print solution
	if m.status == GRB.Status.OPTIMAL:
		#solution = m.getAttr('prices')
		#print(solution)
		m.write(output+'/test2.sol')


if __name__ == "__main__":
	#tranport('output','db/test.db', 68)
	example('output')